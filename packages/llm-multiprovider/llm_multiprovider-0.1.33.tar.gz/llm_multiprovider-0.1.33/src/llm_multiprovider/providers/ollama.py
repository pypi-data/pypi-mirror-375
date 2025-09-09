#OLLAMA REST API https://www.postman.com/postman-student-programs/ollama-api/request/uprcxdn/chat-completion-with-tools
import os
from typing import List, Dict, Any, Optional, Union
from llm_multiprovider.providers.base import ModelProviderBase
from llm_multiprovider.utils.request_utils import send_request, extract_json_object



class OllamaProvider(ModelProviderBase):
    """Ollama provider usando el enrutador multiproveedor."""

    # ❌ Ollama no soporta logprobs
    supports_logprobs = False

    def __init__(self, model_name: str, using_tokenizer: bool, tokenizer_name: str = None):
        super().__init__(model_name, using_tokenizer, tokenizer_name)
        self.provider_name = "ollama"





'''
payload = {
  "model": model_name,
  "messages": [
    {
      "role": "user",
      "content": "What is the weather today in Paris?"
    }
  ],
  "stream": False,
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_current_weather",
        "description": "Get the current weather for a location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The location to get the weather for, e.g. San Francisco, CA"
            },
            "format": {
              "type": "string",
              "description": "The format to return the weather in, e.g. 'celsius' or 'fahrenheit'",
              "enum": ["celsius", "fahrenheit"]
            }
          },
          "required": ["location", "format"]
        }
      }
    }
  ]
}
'''