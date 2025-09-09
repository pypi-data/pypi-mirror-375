# runpod.py
import asyncio
import os
import json
import re
import runpod
from typing import List, Dict, Any, Optional, Union, Tuple
from llm_multiprovider.providers.base import ModelProviderBase
from llm_multiprovider.utils.request_utils import extract_json_object


def _strip_thinking(text: str) -> Tuple[str, Optional[str]]:
    """Elimina bloques <think>...</think> y devuelve (texto_limpio, contenido_think)."""
    if not text:
        return "", None
    pat = re.compile(r"<think>(.*?)</think>", re.DOTALL | re.IGNORECASE)
    pieces = pat.findall(text)
    thinking = "\n\n".join(p.strip() for p in pieces) if pieces else None
    cleaned = pat.sub("", text).strip()
    return cleaned, thinking


class RunpodProvider(ModelProviderBase):
    """Proveedor RunPod para endpoints custom (no OpenAI-style).

    - Generación y chat: limpia eco del prompt por defecto (presentación),
      manteniendo el prompt original para rutas de logprobs.
    - Logprobs: usa `details`, `decoder_input_details` y, si está disponible, `prefill`.
    """

    # si el endpoint devuelve details/top_tokens, podemos ofrecer logprobs
    supports_logprobs: bool = True

    def __init__(self, model_name: str, using_tokenizer: bool, tokenizer_name: str = None):
        super().__init__(model_name, using_tokenizer, tokenizer_name)
        api_key = os.getenv("RUNPOD_API_KEY")
        endpoint_id = os.getenv("RUNPOD_ENDPOINT") or os.getenv("RUNPOD_ENDPOINT_ID")
        if not api_key:
            raise ValueError("RUNPOD_API_KEY is not set.")
        if not endpoint_id:
            raise ValueError("RUNPOD_ENDPOINT (o RUNPOD_ENDPOINT_ID) no está configurado.")

        runpod.api_key = api_key
        self.endpoint = runpod.Endpoint(endpoint_id)


        # último raw de respuesta (útil para debug)
        self.last_raw: Optional[Dict[str, Any]] = None
        self.dump_raw: bool = os.getenv("RUNPOD_DUMP_RAW", "0") not in ("0", "false", "False", "")

    # ---------- helpers ----------

    def _dump_raw(self, where: str, data: Any) -> None:
        """Guarda el último raw a /tmp para depuración si RUNPOD_DUMP_RAW=1."""
        try:
            if not self.dump_raw:
                return
            path = "/tmp/runpod_last.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"where": where, "data": data}, f, ensure_ascii=False, indent=2)
            self.logger.info(f"RunPod - raw guardado en {path} ({where})")
        except Exception as e:
            self.logger.warning(f"RunPod - fallo al guardar raw: {e}")

    def _strip_prompt_echo(self, text: str, prompt: str) -> str:
        """Intenta eliminar eco del prompt de la salida de texto."""
        if not text or not prompt:
            return text
        p = prompt.strip()
        t = text

        # caso 1: empieza por el prompt
        if t.startswith(p):
            return t[len(p):].lstrip()

        # caso 2: el prompt aparece al final de la entrada justo antes de la respuesta
        idx = t.rfind(p)
        if 0 <= idx < len(t) - len(p):
            tail = t[idx + len(p):].lstrip()
            if len(tail) >= 2:
                return tail

        return t

    def _build_generate_payload(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Normaliza parámetros estilo providers:
          - max_tokens -> max_new_tokens
          - greedy si temperature <= 0
          - mapea top_p/top_k/seed
          - return_full_text=False por defecto (mejor para presentación)
        """
        temperature = kwargs.pop("temperature", 0.7)
        max_tokens = kwargs.pop("max_tokens", kwargs.pop("max_new_tokens", 128))
        top_p = kwargs.pop("top_p", None)
        top_k = kwargs.pop("top_k", None)
        seed = kwargs.pop("seed", None)

        generate = {
            "prompt": prompt,
            "max_new_tokens": max_tokens,
            "details": kwargs.pop("details", True),
            "decoder_input_details": kwargs.pop("decoder_input_details", True),
            # por defecto NO eco en salida de texto de generación
            "return_full_text": kwargs.pop("return_full_text", False),
        }

        # Greedy vs sampling
        try:
            t = float(temperature) if temperature is not None else 0.7
        except Exception:
            t = 0.7
        if t <= 0:
            generate["do_sample"] = False
        else:
            generate["do_sample"] = True
            generate["temperature"] = t
            if top_p is not None:
                generate["top_p"] = top_p
            if top_k is not None:
                generate["top_k"] = top_k

        if seed is not None:
            generate["seed"] = seed

        # `top_n_tokens` para logprobs de salida (si tu endpoint lo soporta)
        if "top_n_tokens" in kwargs:
            generate["top_n_tokens"] = kwargs["top_n_tokens"]

        # Campo libre por si tu endpoint usa sampling_params aparte
        sampling_params = kwargs.pop("sampling_params", {})

        # Deja pasar cualquier extra específico del endpoint:
        generate.update(kwargs)

        return {
            "generate": generate,
            "sampling_params": sampling_params,
        }

    async def _run_endpoint(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Ejecuta el endpoint asincrónicamente y devuelve la salida como dict."""
        try:
            job = self.endpoint.run(payload)
            while True:
                await asyncio.sleep(0.5)
                status = job.status()
                if status == "COMPLETED":
                    out = job.output()
                    self.last_raw = out  # cachea último raw
                    self._dump_raw("completed", out)
                    return out
                if status in ("CANCELLED", "FAILED"):
                    self.logger.error(f"RunPod - Job status: {status}")
                    return None
        except Exception as e:
            self.logger.error(f"RunPod - Error running endpoint: {e}")
            return None

    @staticmethod
    def _extract_text_from_output(resp: Dict[str, Any]) -> Optional[str]:
        """
        Intenta varias claves comunes para texto.
        Adapta a tu esquema de salida real del endpoint.
        """
        if not resp:
            return None
        # casos comunes
        if "generated_text" in resp and isinstance(resp["generated_text"], str):
            return resp["generated_text"]
        if "output_text" in resp and isinstance(resp["output_text"], str):
            return resp["output_text"]
        if isinstance(resp.get("output"), dict):
            for k in ("generated_text", "text", "output_text"):
                if isinstance(resp["output"].get(k), str):
                    return resp["output"][k]
        if isinstance(resp.get("output"), list) and resp["output"]:
            cand = resp["output"][0]
            if isinstance(cand, dict):
                for k in ("generated_text", "text", "output_text"):
                    if isinstance(cand.get(k), str):
                        return cand[k]
            elif isinstance(cand, str):
                return cand
        return None

    # ---------- generate ----------
    async def generate_text(self, prompt: str, **kwargs) -> List[str]:
        """Genera texto. Por defecto limpia el eco del prompt para presentación."""
        self.logger.info("RunPod - Generating text")
        keep_echo = bool(kwargs.pop("keep_echo", False))  # para depurar, dejar eco si se desea
        payload = self._build_generate_payload(prompt, **kwargs)
        resp = await self._run_endpoint(payload)
        if not resp:
            self.logger.error("RunPod - Empty response")
            return []
        text = self._extract_text_from_output(resp) or ""
        text, _thinking = _strip_thinking(text)
        if not keep_echo:
            text = self._strip_prompt_echo(text, prompt)
        return [text]

    # ---------- chat ----------
    async def chat_completion(self, messages: List[Dict[str, Any]], **kwargs) -> List[str]:
        """Chat completion con limpieza de eco del prompt aplicado por defecto."""
        self.logger.info("RunPod - Chat completion")
        keep_echo = bool(kwargs.pop("keep_echo", False))

        if self.tokenizer and hasattr(self.tokenizer, "apply_chat_template"):
            prompt = self.tokenizer.apply_chat_template(messages, tokenize=False)
        else:
            # fallback simple
            prompt = "\n".join(f"{m.get('role','user')}: {m.get('content','')}" for m in messages)

        payload = self._build_generate_payload(prompt, **kwargs)
        resp = await self._run_endpoint(payload)
        if not resp:
            self.logger.error("RunPod - Empty response")
            return []
        text = self._extract_text_from_output(resp) or ""
        text, _thinking = _strip_thinking(text)
        if not keep_echo:
            text = self._strip_prompt_echo(text, prompt)
        return [text]

    # ---------- logprobs (siguiente token/top-N) ----------
    async def logprobs(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Requiere que tu endpoint soporte:
          details=True, decoder_input_details=True, top_n_tokens (p.ej. 5)
        Devuelve:
          { tokens: [...], token_logprobs: [...], top_logprobs: [[{token,logprob}...], ...] }
        """
        self.logger.info("RunPod - Logprobs")
        payload = self._build_generate_payload(
            prompt,
            max_new_tokens=1,
            details=True,
            decoder_input_details=True,
            top_n_tokens=kwargs.pop("top_n_tokens", 5),
            # forzamos raw completo (no influye en prefill)
            return_full_text=True,
            **kwargs,
        )
        resp = await self._run_endpoint(payload)
        if not resp or "details" not in resp:
            self.logger.warning("RunPod - No logprobs in response.")
            return None

        details = resp["details"]
        # tokens generados (no especiales)
        tokens: List[str] = []
        token_logprobs: List[Optional[float]] = []
        if "tokens" in details:
            for t in details["tokens"]:
                if not t.get("special", False):
                    tokens.append(t.get("text", ""))
                    token_logprobs.append(t.get("logprob"))

        # top-N por posición
        top_logprobs: List[List[Dict[str, Any]]] = []
        if "top_tokens" in details:
            for slot in details["top_tokens"]:
                slot_list = [{"token": tt.get("text", ""), "logprob": tt.get("logprob")} for tt in slot]
                top_logprobs.append(slot_list)

        return {
            "tokens": tokens,
            "token_logprobs": token_logprobs,
            "top_logprobs": top_logprobs,
        }

    # ---------- logprobs para un target concreto ----------
    async def get_logprobs_for_target_output(self, prompt: str, target_output: str) -> Optional[Dict[str, Any]]:
        """
        Usa `prefill` (si el endpoint lo expone) para obtener los logprobs del prompt+target.
        Requiere tener `self.tokenizer` para separar prompt/target en ids.
        """
        self.logger.info("RunPod - get_logprobs_for_target_output")

        if not self.tokenizer:
            self.logger.warning("RunPod - tokenizer requerido para separar prompt/target.")
            return None

        full_text = f"{prompt} {target_output}"
        payload = self._build_generate_payload(
            full_text,
            max_new_tokens=1,
            details=True,
            decoder_input_details=True,
            top_n_tokens=5,
            return_full_text=True,
        )
        resp = await self._run_endpoint(payload)
        if not resp or "details" not in resp:
            self.logger.warning("RunPod - No details in response.")
            return None

        details = resp["details"]
        if "prefill" not in details:
            self.logger.warning("RunPod - No prefill in response.")
            return None

        prefill = [t for t in details["prefill"] if not t.get("special", False)]
        all_tokens = [t.get("text", "") for t in prefill]
        all_logprobs = [t.get("logprob") for t in prefill]
        all_token_ids = [t.get("id") for t in prefill]

        # longitud en tokens del prompt
        prompt_token_length = len(self.tokenizer.encode(prompt, add_special_tokens=False))

        target_tokens = all_tokens[prompt_token_length:]
        target_logprobs = all_logprobs[prompt_token_length:]
        target_token_ids = all_token_ids[prompt_token_length:]
        reconstructed_text = self.tokenizer.decode([tid for tid in target_token_ids if tid is not None])

        # top-N alineado (si el backend lo entrega por posición)
        top_logprobs: List[List[Dict[str, Any]]] = []
        if "top_tokens" in details:
            for slot in details["top_tokens"][prompt_token_length:]:
                slot_list = [{"token": tt.get("text", ""), "logprob": tt.get("logprob")} for tt in slot]
                top_logprobs.append(slot_list)

        return {
            "tokens": target_tokens,
            "token_logprobs": target_logprobs,
            "token_ids": target_token_ids,
            "reconstructed_text": reconstructed_text,
            "top_logprobs": top_logprobs,
        }

    # ---------- JSON helper ----------
    async def get_json_response(self, prompt: str, preoutput: Union[str, dict], **kwargs) -> Optional[dict]:
        """Genera texto (sin eco por defecto) y extrae un JSON válido de la salida."""
        self.logger.info("RunPod - JSON response")
        # Aseguramos que la generación no incluya eco del prompt (mejora parsing)
        kwargs = dict(kwargs)
        kwargs.setdefault("return_full_text", False)
        kwargs.setdefault("keep_echo", False)

        texts = await self.generate_text(prompt, **kwargs)
        if not texts:
            return None
        result_text = (texts[0] or "").strip()
        try:
            return extract_json_object(result_text, preoutput if isinstance(preoutput, str) else "")
        except Exception as e:
            self.logger.error(f"❌ Error parsing JSON: {e}")
            return None
