import os
from typing import List, Dict, Any, Optional, Union
from llm_multiprovider.providers.base import ModelProviderBase
from llm_multiprovider.utils.request_utils import send_request, extract_json_object


class GroqProvider(ModelProviderBase):
    """Groq provider usando el enrutador multiproveedor."""

    supports_logprobs: bool = False

    def __init__(self, model_name: str, using_tokenizer: bool, tokenizer_name: str = None):
        super().__init__(model_name, using_tokenizer, tokenizer_name)
        self.provider_name = "groq"
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not set in the .env file.")

    async def logprobs(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        self.logger.info("Groq - Logprobs")
        overrides = {"max_tokens": 5, "logprobs": 5}
        overrides.update(kwargs)
        messages = [{"role": "user", "content": prompt}]
        try:
            resp = await send_request(
                self.provider_name,
                self.model_name,
                messages=messages,
                params=overrides,
            )
            raw_choice = resp.get("raw", {}).get("choices", [{}])[0]
            logprobs_data = raw_choice.get("logprobs")
            if not logprobs_data:
                return None
            return {
                "tokens": logprobs_data.get("tokens", []),
                "token_logprobs": logprobs_data.get("token_logprobs", []),
                "top_logprobs": logprobs_data.get("top_logprobs", []),
            }
        except Exception as e:
            self.logger.warning(f"Groq - logprobs not available for model {self.model_name}: {e}")
            return None


