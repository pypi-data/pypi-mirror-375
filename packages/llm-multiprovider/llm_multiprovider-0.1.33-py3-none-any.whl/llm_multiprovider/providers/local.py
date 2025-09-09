import os
from typing import List, Dict, Any, Optional, Union

import torch

from llm_multiprovider.providers.base import ModelProviderBase
from llm_multiprovider.utils.request_utils import (
    send_request,
    extract_json_object,    
)

from llm_multiprovider.utils.local_utils import get_local_pipeline

class LocalProvider(ModelProviderBase):
    """Proveedor local (Hugging Face) alineado con el resto de providers.

    - generate_text / chat_completion / get_json_response usan `send_request("local", ...)`
      que a su vez reutiliza un pipeline cacheado (device_map="auto").
    - logprobs / get_logprobs_for_target_output usan el MISMO pipeline cacheado para extraer logits,
      evitando cargar el modelo dos veces y manteniendo eficiencia.
    """

    # Soportamos logprobs completos al ser local
    supports_logprobs: bool = True

    def __init__(self, model_name: str, using_tokenizer: bool, tokenizer_name: str = None):
        super().__init__(model_name, using_tokenizer, tokenizer_name)
        self.provider_name = "local"


    # ---------- Logprobs (último token por defecto; configurable) ----------
    async def logprobs(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Calcula logprobs para los próximos tokens basándose en los logits del modelo local.

        Por defecto devuelve top-k del próximo token. Puedes pasar:
          - top_k: int (por defecto 10)
          - return_top_ids: bool (por defecto True) para incluir token_ids en el resultado
        """
        self.logger.info("Local - Logprobs")
        top_k: int = int(kwargs.get("top_k", 10))
        return_top_ids: bool = bool(kwargs.get("return_top_ids", True))

        pipe = get_local_pipeline(self.model_name)
        hf_tokenizer = pipe.tokenizer
        hf_model = pipe.model

        hf_model.eval()
        device = next(hf_model.parameters()).device

        with torch.no_grad():
            input_ids = hf_tokenizer.encode(prompt, return_tensors="pt").to(device)
            outputs = hf_model(input_ids)
            logits = outputs.logits  # [batch, seq, vocab]
            last_logits = logits[0, -1, :]  # últimos logits

            probs = torch.softmax(last_logits, dim=-1)
            top_probs, top_indices = torch.topk(probs, k=min(top_k, probs.shape[-1]))
            top_tokens = hf_tokenizer.convert_ids_to_tokens(top_indices.tolist())
            top_logprobs = top_probs.log().tolist()

        out = {
            "tokens": top_tokens,
            "token_logprobs": top_logprobs,
        }
        if return_top_ids:
            out["token_ids"] = top_indices.tolist()
        return out

    # ---------- Logprobs para un target concreto ----------
    async def get_logprobs_for_target_output(self, prompt: str, target_output: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene log-probabilidad por token para `target_output` condicionada al `prompt`.
        """
        self.logger.info("Local - get_logprobs_for_target_output")

        pipe = get_local_pipeline(self.model_name)
        hf_tokenizer = pipe.tokenizer
        hf_model = pipe.model

        hf_model.eval()
        device = next(hf_model.parameters()).device

        full_text = f"{prompt} {target_output}"
        with torch.no_grad():
            # Tokenizamos prompt y full
            prompt_ids = hf_tokenizer.encode(prompt, add_special_tokens=False)
            input_ids = hf_tokenizer.encode(full_text, return_tensors="pt").to(device)
            # Índices de los tokens del target dentro de la secuencia completa
            target_ids = input_ids[0, len(prompt_ids):].tolist()

            # forward
            outputs = hf_model(input_ids)
            # Logits alineados por posición (para cada token predecimos el siguiente)
            # Cogemos el tramo que predice exactamente los tokens del target
            start = len(prompt_ids) - 1
            end = len(input_ids[0]) - 1
            slice_logits = outputs.logits[0, start:end, :]  # [len(target), vocab]

            log_probs = torch.log_softmax(slice_logits, dim=-1)
            # Extraemos los logprobs de los tokens objetivo
            idx = torch.arange(len(target_ids), device=log_probs.device)
            selected_logprobs = log_probs[idx, torch.tensor(target_ids, device=log_probs.device)]

        tokens = hf_tokenizer.convert_ids_to_tokens(target_ids)
        reconstructed = hf_tokenizer.decode(target_ids, skip_special_tokens=True)

        return {
            "tokens": tokens,
            "token_logprobs": selected_logprobs.tolist(),
            "token_ids": target_ids,
            "reconstructed_text": reconstructed,
        }

