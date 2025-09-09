import os
from typing import List, Dict, Any, Optional
from llm_multiprovider.providers.base import ModelProviderBase
from llm_multiprovider.utils.request_utils import send_request, extract_json_object


class CerebrasProvider(ModelProviderBase):
    """Cerebras provider usando el enrutador multiproveedor."""

    supports_logprobs = False  # 🚨 Cerebras no soporta echo+logprobs (todavía)

    def __init__(self, model_name: str, using_tokenizer: bool, tokenizer_name: str = None):
        super().__init__(model_name, using_tokenizer, tokenizer_name)
        self.provider_name = "cerebras"
        self.api_key = os.getenv("CEREBRAS_API_KEY")
        if not self.api_key:
            raise ValueError("CEREBRAS_API_KEY is not set in the .env file.")


