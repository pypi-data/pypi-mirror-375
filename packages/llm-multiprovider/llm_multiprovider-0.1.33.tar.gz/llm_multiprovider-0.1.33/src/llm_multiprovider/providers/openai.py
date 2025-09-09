import os
from typing import List, Dict, Any, Optional, Union
from llm_multiprovider.providers.base import ModelProviderBase
from llm_multiprovider.utils.request_utils import send_request, extract_json_object

class OpenAIProvider(ModelProviderBase):
    """
    Provider para OpenAI, usando el enrutador multiproveedor `send_request("openai", ...)`.

    - generate_text -> usa Chat Completions unificando prompt->messages (como en Groq).
    - chat_completion -> Chat Completions normal.
    - logprobs -> intenta pedir logprobs en Chat (tokens generados); devuelve dict normalizado.
    - get_logprobs_for_target_output -> no soportado (no hay echo en chat), devuelve None.
    - get_json_response -> genera y extrae JSON con tu helper.
    """

    # OpenAI Chat da logprobs solo de tokens generados (no echo del prompt)
    supports_logprobs: bool = True

    def __init__(self, model_name: str, using_tokenizer: bool, tokenizer_name: str = None):
        super().__init__(model_name, using_tokenizer, tokenizer_name)
        self.provider_name = "openai"
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
        if using_tokenizer:
            from llm_multiprovider.utils.tokenizer_mapper import TokenizerMapper
            self.tokenizer = TokenizerMapper.get_tokenizer(model_name) if using_tokenizer else None
        else: 
            self.tokenizer = None

    # ---------- Logprobs (tokens generados) ----------
    async def logprobs(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Pide logprobs en Chat Completions (OpenAI los da para tokens generados).
        Devuelve un dict normalizado: { tokens: [...], token_logprobs: [...], top_logprobs: [[...], ...] }
        """
        self.logger.info("OpenAI - Logprobs")
        overrides = {
            "max_tokens": kwargs.get("max_tokens", 5),
            # OpenAI Chat usa "logprobs": True y "top_logprobs": k
            "logprobs": True,
            "top_logprobs": kwargs.get("top_logprobs", 5),
        }
        messages = [{"role": "user", "content": prompt}]

        try:
            resp = await send_request(
                self.provider_name,
                self.model_name,
                messages=messages,
                params={**kwargs, **overrides},
            )
        except Exception as e:
            self.logger.warning(f"OpenAI - logprobs request failed: {e}")
            return None

        raw = resp.get("raw") or {}
        choices = raw.get("choices") or []
        if not choices:
            return None

        # Formato OpenAI Chat: choice["logprobs"]["content"] = [{token, logprob, top_logprobs:[{token,logprob}...]}...]
        lp = (choices[0] or {}).get("logprobs") or {}
        content = lp.get("content") or []
        if not content:
            return None

        tokens = []
        token_logprobs = []
        top_logprobs = []
        for slot in content:
            tokens.append(slot.get("token", ""))
            token_logprobs.append(slot.get("logprob"))
            tops = slot.get("top_logprobs") or []
            top_logprobs.append([{"token": t.get("token", ""), "logprob": t.get("logprob")} for t in tops])

        return {
            "tokens": tokens,
            "token_logprobs": token_logprobs,
            "top_logprobs": top_logprobs,
        }



