import os
from typing import List, Dict, Any, Optional
from llm_multiprovider.providers.base import ModelProviderBase
from llm_multiprovider.utils.request_utils import send_request, extract_json_object



class TogetherAIProvider(ModelProviderBase):
    """TogetherAI provider usando el enrutador multiproveedor."""

    # ✅ TogetherAI soporta echo+logprobs (prompt + completions)
    supports_logprobs = True

    def __init__(self, model_name: str, using_tokenizer: bool, tokenizer_name: str = None):
        super().__init__(model_name, using_tokenizer, tokenizer_name)
        self.provider_name = "together_ai"
        self.api_key = os.getenv("TOGETHER_API_KEY")
        if not self.api_key:
            raise ValueError("TOGETHER_API_KEY is not set in the .env file.")
        if using_tokenizer:
            from llm_multiprovider.utils.tokenizer_mapper import TokenizerMapper
            self.tokenizer = TokenizerMapper.get_tokenizer(model_name) if using_tokenizer else None
        else: 
            self.tokenizer = None



    async def logprobs(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Devuelve la respuesta normalizada del enrutador.
        Para next-token logprobs típicamente:
            await self.logprobs(prompt, max_tokens=1, logprobs=1)
        """
        self.logger.info("TogetherAI - Logprobs")
        overrides = {"max_tokens": 1, "logprobs": 1}
        overrides.update(kwargs)
        return await send_request(self.provider_name, self.model_name, prompt=prompt, params=overrides)

    async def get_logprobs_for_target_output(self, prompt: str, target_output: str) -> Optional[Dict[str, Any]]:
        """
        Usa echo+logprobs en completions y extrae SOLO los tokens del target_output.
        """
        if not self.tokenizer:
            raise ValueError("Tokenizer is required for logprobs but not initialized.")

        full_text = f"{prompt} {target_output}"
        prompt_ids = self.tokenizer.encode(prompt, add_special_tokens=False)
        prompt_len = len(prompt_ids)

        resp = await send_request(
            self.provider_name,
            self.model_name,
            prompt=full_text,
            params={"echo": True, "logprobs": 1, "max_tokens": 1},
        )

        pl = resp.get("prompt_logprobs")
        if not pl:
            return None

        tokens = pl.get("tokens", [])
        token_logprobs = pl.get("token_logprobs", [])
        token_ids = pl.get("token_ids", [])

        target_tokens = tokens[prompt_len:]
        target_logps = token_logprobs[prompt_len:]
        target_ids = token_ids[prompt_len:] if token_ids else []

        reconstructed = None
        try:
            reconstructed = self.tokenizer.convert_tokens_to_string(target_tokens)
        except Exception:
            pass

        return {
            "tokens": target_tokens,
            "token_logprobs": target_logps,
            "token_ids": target_ids,
            "reconstructed_text": reconstructed,
        }

