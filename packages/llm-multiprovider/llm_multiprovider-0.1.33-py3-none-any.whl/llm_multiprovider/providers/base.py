import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union


from llm_multiprovider.utils.request_utils import send_request, extract_json_object

class ModelProviderBase(ABC):
    """Abstract base class for all model providers."""

    def __init__(self, model_name: str, using_tokenizer: bool, tokenizer_name: str = None):
        self.model_name = model_name
        self.logger = logging.getLogger(self.__class__.__name__)
        # Opcional: si quieres un tokenizer explícito (para reconstrucciones), lo pedimos por mapper.
        if using_tokenizer:
            from llm_multiprovider.utils.tokenizer_mapper import TokenizerMapper
            self.tokenizer = TokenizerMapper.get_tokenizer(model_name) 
        else: 
            self.tokenizer = None

    async def generate_text(self, prompt: str, **kwargs) -> List[str]:
        self.logger.info("Generating text")
        resp = await send_request(self.provider_name, self.model_name, prompt=prompt, params=kwargs)
        return [c["text"] for c in resp.get("choices", [])]

    async def chat_completion(self, messages: List[Dict[str, Any]], **kwargs) -> List[str]:
        self.logger.info("Chat completion")
        resp = await send_request(self.provider_name, self.model_name, messages=messages, params=kwargs)
        return [c["text"] for c in resp.get("choices", [])]


    async def logprobs(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Get log probabilities if supported; otherwise, return None."""
        return None


    async def get_logprobs_for_target_output(self, prompt: str, target_output: str) -> Optional[Dict[str, Any]]:
        """
        Get log-probabilities for each token in the target output.

        Args:
            prompt (str): The input prompt.
            target_output (str): The expected output sequence.

        Returns:
            dict: A dictionary containing log probabilities for only the target_output tokens.
        """
        return None

    async def get_json_response(self, prompt: str, preoutput: Union[str, dict], **kwargs) -> Optional[dict]:
        """
        Generate text and extract a valid JSON object from the output.

        - Forces temperature=0 unless caller overrides.
        - Adds stop token "}" unless caller overrides.
        - Ensures output ends with "}".
        - Uses extract_json_object to clean up.
        """
        self.logger.info(f"{self.provider_name} - JSON response")

        # Force deterministic generation by default
        kwargs.setdefault("temperature", 0)

        # Add stop token unless already provided
        if "stop" not in kwargs:
            kwargs["stop"] = ["}"]

        resp = await send_request(
            self.provider_name,
            self.model_name,
            prompt=prompt,
            params=kwargs,
        )
        print(prompt)
        print(resp)

        result_text = resp["choices"][0]["text"].strip()

        # Ensure closing brace
        if not result_text.endswith("}"):
            result_text += "}"

        try:
            return extract_json_object(result_text, preoutput if isinstance(preoutput, str) else "")
        except Exception as e:
            self.logger.error(f"❌ Error parsing JSON: {e}")
            return None
