import os
import re
import json
import httpx
from typing import List, Dict, Any, Optional, Union
from llm_multiprovider.providers.base import ModelProviderBase
from llm_multiprovider.utils.request_utils import extract_json_object



class RunpodOpenAIProvider(ModelProviderBase):
    """RunPod provider para endpoints OpenAI-style (/v1/completions y /v1/chat/completions)."""

    supports_logprobs: bool = True  # si el endpoint no los soporta, devolvemos None

    def __init__(self, model_name: str, using_tokenizer: bool, tokenizer_name: str = None):
        super().__init__(model_name, using_tokenizer, tokenizer_name)
        self.api_key = os.getenv("RUNPOD_OPENAI_API_KEY")
        self.base_url = (os.getenv("RUNPOD_OPENAI_ENDPOINT") or "").rstrip("/")
        self.secret_key = os.getenv("RUNPOD_X_SECRET_KEY")  # opcional
        self.dump_raw = os.getenv("RUNPOD_OPENAI_DUMP", "0") not in ("0", "false", "False", "")

        if not self.api_key:
            raise ValueError("RUNPOD_OPENAI_API_KEY is not set.")
        if not self.base_url:
            raise ValueError("RUNPOD_OPENAI_ENDPOINT is not set.")


    # ---------------- helpers ----------------

    def _headers(self) -> Dict[str, str]:
        h = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.secret_key:
            h["X-Secret-Key"] = self.secret_key
        return h

    def _normalize_base(self) -> str:
        """
        Acepta varias formas y normaliza a .../openai/v1:
        - https://api.runpod.ai/v2/<id>
        - https://api.runpod.ai/v2/<id>/run    -> /openai/v1
        - https://api.runpod.ai/v2/<id>/runsync -> /openai/v1
        - https://api.runpod.ai/v2/<id>/openai  -> /openai/v1
        - ya en /openai/v1 o en ruta final (completions/chat/completions)
        """
        u = self.base_url

        # Si ya termina en endpoint final, vuelve a la base /v1
        if u.endswith("/completions") or u.endswith("/chat/completions"):
            return u.rsplit("/", 2)[0]

        # /openai -> /openai/v1
        if re.search(r"/openai$", u, re.I):
            return u + "/v1"

        # /run o /runsync -> /openai/v1
        if re.search(r"/(run|runsync)$", u, re.I):
            return re.sub(r"/(run|runsync)$", "/openai/v1", u, flags=re.I)

        # /v2/<id> sin sufijo -> añadimos /openai/v1
        if re.search(r"/v2/[^/]+$", u):
            return u + "/openai/v1"

        # si ya termina en /openai/v1 o /v1
        if u.endswith("/openai/v1") or u.endswith("/v1"):
            return u

        # fallback: si nos dieron /openai con prefijos raros
        m = re.search(r"(.*?/openai)(/v1)?$", u, re.I)
        if m:
            return m.group(1) + "/v1"

        # último recurso: asumimos que esto ya es base /v1
        return u

    def _resolve_url(self, use_chat: bool) -> str:
        base_v1 = self._normalize_base().rstrip("/")
        if base_v1.endswith("/completions") or base_v1.endswith("/chat/completions"):
            return base_v1
        return f"{base_v1}/chat/completions" if use_chat else f"{base_v1}/completions"

    @staticmethod
    def _normalize_gen_params(kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza params al estilo OpenAI (max_tokens, n, temperature, etc.)."""
        p: Dict[str, Any] = {}

        # max_tokens / max_new_tokens
        if "max_tokens" in kwargs:
            p["max_tokens"] = kwargs["max_tokens"]
        elif "max_new_tokens" in kwargs:
            p["max_tokens"] = kwargs["max_new_tokens"]

        # n
        if "num_return_sequences" in kwargs:
            p["n"] = kwargs["num_return_sequences"]

        # copia directa de claves conocidas
        for k in (
            "temperature",
            "top_p",
            "presence_penalty",
            "frequency_penalty",
            "stop",
            "logprobs",
            "top_logprobs",
            "echo",
            "seed",
        ):
            if k in kwargs and kwargs[k] is not None:
                p[k] = kwargs[k]
        return p

    @staticmethod
    def _extract_comp_texts(resp: Dict[str, Any]) -> List[str]:
        return [(c.get("text") or "").strip() for c in (resp.get("choices") or [])]

    @staticmethod
    def _extract_chat_texts(resp: Dict[str, Any]) -> List[str]:
        out: List[str] = []
        for ch in (resp.get("choices") or []):
            msg = ch.get("message") or {}
            content = msg.get("content", "")
            out.append(content if isinstance(content, str) else str(content))
        return [t.strip() for t in out]

    @staticmethod
    def _extract_logprobs_from_choice(choice: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        lp = choice.get("logprobs")
        if not lp:
            return None
        out = {
            "tokens": lp.get("tokens") or [],
            "token_logprobs": lp.get("token_logprobs") or [],
        }
        if "top_logprobs" in lp and lp["top_logprobs"] is not None:
            out["top_logprobs"] = lp["top_logprobs"]
        return out

    # -------- logging del RAW + volcado opcional --------

    def _info_dump(self, resp: httpx.Response, data: Any, where: str) -> None:
        try:
            req_id = (
                resp.headers.get("x-request-id")
                or resp.headers.get("x-requestid")
                or resp.headers.get("x-runpod-request-id")
            )
            pretty = json.dumps(data, ensure_ascii=False, indent=2) if isinstance(data, (dict, list)) else str(data)
            truncated = (pretty[:2000] + "…") if len(pretty) > 2000 else pretty
            self.logger.info(f"[RunpodOpenAI:{where}] status={resp.status_code} request_id={req_id}\nRAW: {truncated}")
            if self.dump_raw:
                with open("/tmp/runpod_openai_last.json", "w", encoding="utf-8") as f:
                    json.dump(
                        {"where": where, "status": resp.status_code, "headers": dict(resp.headers), "data": data},
                        f,
                        ensure_ascii=False,
                        indent=2,
                    )
                self.logger.info("Runpod OpenAI - raw guardado en /tmp/runpod_openai_last.json")
        except Exception as e:
            self.logger.info(f"[RunpodOpenAI:{where}] fallo al volcar raw: {e}")

    # -------- extractor “fallback” si no hay choices típicos --------

    @staticmethod
    def _fallback_texts(data: Any) -> List[str]:
        if not isinstance(data, dict):
            return []
        # Campos alternativos
        for key in ("output_text", "generated_text", "text"):
            if key in data and isinstance(data[key], str):
                return [data[key]]

        # {"outputs":[{"text":"..."}]}
        if "outputs" in data and isinstance(data["outputs"], list):
            for item in data["outputs"]:
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    return [item["text"]]

        # {"data":[{"text":"..."}]}
        if "data" in data and isinstance(data["data"], list):
            for item in data["data"]:
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    return [item["text"]]
        return []

    # ---------------- core methods ----------------

    async def generate_text(self, prompt: str, **kwargs) -> List[str]:
        self.logger.info("Runpod OpenAI - Generating text")
        url = self._resolve_url(use_chat=False)
        payload = {"model": self.model_name, "prompt": prompt, "stream": False}
        payload.update(self._normalize_gen_params(kwargs))

        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(url, json=payload, headers=self._headers())
            if r.status_code == 404 and "/run" in self.base_url:
                fixed = re.sub(r"/(run|runsync)$", "/openai/v1", self.base_url, flags=re.I)
                url = (fixed.rstrip("/") + "/completions")
                r = await client.post(url, json=payload, headers=self._headers())
            r.raise_for_status()
            try:
                data = r.json()
            except Exception:
                data = r.text
            self._info_dump(r, data, "completions")

        if isinstance(data, dict) and "error" in data:
            self.logger.error(f"Runpod OpenAI - Error: {data['error']}")

        texts = self._extract_comp_texts(data) if isinstance(data, dict) else []
        if not texts:
            fb = self._fallback_texts(data)
            if fb:
                self.logger.warning("Runpod OpenAI - 'choices' vacío; usando fallback extractor.")
                return [t.strip() for t in fb if isinstance(t, str)]
            self.logger.warning("Runpod OpenAI - Empty choices in completions response.")
        return texts

    async def chat_completion(self, messages: List[Dict[str, Any]], **kwargs) -> List[str]:
        self.logger.info("Runpod OpenAI - Chat completion")
        url = self._resolve_url(use_chat=True)
        payload = {"model": self.model_name, "messages": messages, "stream": False}
        payload.update(self._normalize_gen_params(kwargs))

        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(url, json=payload, headers=self._headers())
            if r.status_code == 404 and "/run" in self.base_url:
                fixed = re.sub(r"/(run|runsync)$", "/openai/v1", self.base_url, flags=re.I)
                url = (fixed.rstrip("/") + "/chat/completions")
                r = await client.post(url, json=payload, headers=self._headers())
            r.raise_for_status()
            try:
                data = r.json()
            except Exception:
                data = r.text
            self._info_dump(r, data, "chat.completions")

        if isinstance(data, dict) and "error" in data:
            self.logger.error(f"Runpod OpenAI - Error: {data['error']}")

        texts = self._extract_chat_texts(data) if isinstance(data, dict) else []
        if not texts:
            fb = self._fallback_texts(data)
            if fb:
                self.logger.warning("Runpod OpenAI - 'choices' vacío en chat; usando fallback extractor.")
                return [t.strip() for t in fb if isinstance(t, str)]
            self.logger.warning("Runpod OpenAI - Empty choices in chat response.")
        return texts

    async def logprobs(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        self.logger.info("Runpod OpenAI - Logprobs")
        url = self._resolve_url(use_chat=False)
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens": 1,
            "logprobs": kwargs.get("logprobs", 5),
            "echo": True,
            "stream": False,
        }
        payload.update(self._normalize_gen_params(kwargs))
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(url, json=payload, headers=self._headers())
                if r.status_code == 404 and "/run" in self.base_url:
                    fixed = re.sub(r"/(run|runsync)$", "/openai/v1", self.base_url, flags=re.I)
                    url = (fixed.rstrip("/") + "/completions")
                    r = await client.post(url, json=payload, headers=self._headers())
                r.raise_for_status()
                try:
                    data = r.json()
                except Exception:
                    data = r.text
                self._info_dump(r, data, "logprobs")
        except Exception as e:
            self.logger.warning(f"Runpod OpenAI - logprobs request failed: {e}")
            return None

        if not isinstance(data, dict) or not data.get("choices"):
            self.logger.warning("Runpod OpenAI - No choices in logprobs response.")
            return None
        lp = self._extract_logprobs_from_choice(data["choices"][0])
        if not lp:
            self.logger.warning(f"Runpod OpenAI - Choice has no logprobs: {data['choices'][0]}")
        return lp

    async def get_logprobs_for_target_output(self, prompt: str, target_output: str) -> Optional[Dict[str, Any]]:
        self.logger.info("Runpod OpenAI - get_logprobs_for_target_output")
        url = self._resolve_url(use_chat=False)
        full_text = f"{prompt} {target_output}"
        payload = {
            "model": self.model_name,
            "prompt": full_text,
            "max_tokens": 1,
            "logprobs": 5,
            "echo": True,
            "stream": False,
        }
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(url, json=payload, headers=self._headers())
                if r.status_code == 404 and "/run" in self.base_url:
                    fixed = re.sub(r"/(run|runsync)$", "/openai/v1", self.base_url, flags=re.I)
                    url = (fixed.rstrip("/") + "/completions")
                    r = await client.post(url, json=payload, headers=self._headers())
                r.raise_for_status()
                try:
                    data = r.json()
                except Exception:
                    data = r.text
                self._info_dump(r, data, "target_logprobs")
        except Exception as e:
            self.logger.warning(f"Runpod OpenAI - target logprobs request failed: {e}")
            return None

        if not isinstance(data, dict) or not data.get("choices"):
            self.logger.warning("Runpod OpenAI - No choices in target logprobs response.")
            return None

        lp_full = self._extract_logprobs_from_choice(data["choices"][0])
        if not lp_full:
            self.logger.warning(f"Runpod OpenAI - Choice has no logprobs (target). Choice: {data['choices'][0]}")
            return None

        tokens = lp_full.get("tokens", [])
        token_logprobs = lp_full.get("token_logprobs", [])
        top_logprobs = lp_full.get("top_logprobs", [])

        if not self.tokenizer:
            return {
                "tokens": tokens,
                "token_logprobs": token_logprobs,
                "top_logprobs": top_logprobs,
                "token_ids": [],
                "reconstructed_text": None,
            }

        prompt_ids = self.tokenizer.encode(prompt, add_special_tokens=False)
        p_len = len(prompt_ids)

        target_tokens = tokens[p_len:]
        target_logps = token_logprobs[p_len:]
        target_top = top_logprobs[p_len:] if isinstance(top_logprobs, list) else []

        try:
            token_ids = self.tokenizer.encode(target_output, add_special_tokens=False)
            reconstructed = self.tokenizer.decode(token_ids, skip_special_tokens=True)
        except Exception:
            token_ids, reconstructed = [], None

        return {
            "tokens": target_tokens,
            "token_logprobs": target_logps,
            "top_logprobs": target_top,
            "token_ids": token_ids,
            "reconstructed_text": reconstructed,
        }

    async def get_json_response(self, prompt: str, preoutput: Union[str, dict], **kwargs) -> Optional[dict]:
        self.logger.info("Runpod OpenAI - JSON response")
        texts = await self.generate_text(prompt, **kwargs)
        if not texts:
            self.logger.warning("Runpod OpenAI - No text generated for JSON extraction.")
            return None
        result_text = (texts[0] or "").strip()
        try:
            return extract_json_object(result_text, preoutput if isinstance(preoutput, str) else "")
        except Exception as e:
            self.logger.error(f"❌ Error parsing JSON: {e}")
            return None
