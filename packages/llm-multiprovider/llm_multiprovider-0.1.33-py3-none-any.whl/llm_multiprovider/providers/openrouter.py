import os
from typing import List, Dict, Any, Optional, Union
from llm_multiprovider.providers.base import ModelProviderBase
from llm_multiprovider.utils.request_utils import send_request, extract_json_object


class OpenRouterProvider(ModelProviderBase):
    """OpenRouter provider usando el enrutador multiproveedor."""

    # 🚨 OpenRouter soporta logprobs, pero NO soporta echo+logprobs
    supports_logprobs = True

    def __init__(self, model_name: str, using_tokenizer: bool, tokenizer_name: str = None):
        super().__init__(model_name, using_tokenizer, tokenizer_name)
        self.provider_name = "openrouter"
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not set in the .env file.")



    async def logprobs(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Devuelve logprobs de los tokens generados.
        OpenRouter NO soporta echo=True, por lo que no incluye logprobs del prompt.
        """
        self.logger.info("OpenRouter - Logprobs")
        overrides = {"max_tokens": 5, "logprobs": True, "top_logprobs": 5}
        overrides.update(kwargs)

        resp = await send_request(
            self.provider_name,
            self.model_name,
            prompt=prompt,
            params=overrides,
        )

        # En OpenRouter vendrán dentro de choices[0]["logprobs"]
        raw_choice = resp.get("raw", {}).get("choices", [{}])[0]
        logprobs_data = raw_choice.get("logprobs")
        if not logprobs_data:
            return None

        return {
            "tokens": logprobs_data.get("tokens", []),
            "token_logprobs": logprobs_data.get("token_logprobs", []),
            "top_logprobs": logprobs_data.get("top_logprobs", []),
        }

