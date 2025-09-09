import os
from typing import List, Dict, Any, Optional, Union, Optional, Tuple
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, pipeline

try:
    from auto_gptq import AutoGPTQForCausalLM
except Exception:
    AutoGPTQForCausalLM = None

try:
    from awq import AutoAWQForCausalLM
except Exception:
    AutoAWQForCausalLM = None



_local_pipelines = {}

# ---------- Utilidades compartidas ----------
from dataclasses import dataclass
import torch


@dataclass(frozen=True)
class LocalLoadConfig:
    # "auto" | "fp16" | "bf16" | "bnb-4bit" | "bnb-8bit" | "gptq" | "awq"
    strategy: str = "auto"
    device_map: str = "auto"
    trust_remote_code: bool = True
    use_safetensors: bool = True

def _prefer_bf16() -> torch.dtype:
    if torch.cuda.is_available():
        try:
            if torch.cuda.is_bf16_supported():
                return torch.bfloat16
        except Exception:
            pass
        return torch.float16
    return torch.float32  # CPU

def _local_load_config_from_env() -> LocalLoadConfig:
    strategy = os.getenv("LOCAL_STRATEGY", "auto").lower()
    device_map = os.getenv("LOCAL_DEVICE_MAP", "auto")
    trust = os.getenv("LOCAL_TRUST_REMOTE_CODE", "1") not in ("0", "false", "False")
    use_safetensors = os.getenv("LOCAL_USE_SAFETENSORS", "1") not in ("0", "false", "False")
    return LocalLoadConfig(
        strategy=strategy,
        device_map=device_map,
        trust_remote_code=trust,
        use_safetensors=use_safetensors,
    )



def get_local_pipeline(model_name: str, config: Optional[LocalLoadConfig] = None):
    """
    Carga un pipeline HF con cuantización opcional (cacheado).
    Estrategia elegida vía `config` o variables de entorno.
    """
    config = config or _local_load_config_from_env()
    cache_key = f"{model_name}:::{config.strategy}:::{config.device_map}"
    if cache_key in _local_pipelines:
        return _local_pipelines[cache_key]

    print(f"🔄 Cargando modelo local {model_name} con estrategia '{config.strategy}'...")

    # Tokenizer (compartido)
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=config.trust_remote_code,
        use_fast=True,
    )

    model = None
    strategy = config.strategy

    try:
        if strategy in ("bnb-4bit", "bnb-8bit"):
            bnb_cfg = BitsAndBytesConfig(
                load_in_4bit=(strategy == "bnb-4bit"),
                load_in_8bit=(strategy == "bnb-8bit"),
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=_prefer_bf16(),
            )
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                trust_remote_code=config.trust_remote_code,
                quantization_config=bnb_cfg,
                device_map=config.device_map,
                use_safetensors=config.use_safetensors,
            )

        elif strategy == "gptq":
            if AutoGPTQForCausalLM is None:
                print("⚠️ auto-gptq no instalado; degradando a bnb-4bit…")
                return get_local_pipeline(model_name, LocalLoadConfig(strategy="bnb-4bit", device_map=config.device_map))
            model = AutoGPTQForCausalLM.from_quantized(
                model_name,
                trust_remote_code=config.trust_remote_code,
                device="cuda" if config.device_map == "auto" else config.device_map,
                use_safetensors=config.use_safetensors,
            )

        elif strategy == "awq":
            if AutoAWQForCausalLM is None:
                print("⚠️ awq no instalado; degradando a bnb-4bit…")
                return get_local_pipeline(model_name, LocalLoadConfig(strategy="bnb-4bit", device_map=config.device_map))
            model = AutoAWQForCausalLM.from_quantized(
                model_name,
                trust_remote_code=config.trust_remote_code,
                device="cuda" if config.device_map == "auto" else config.device_map,
            )

        elif strategy in ("fp16", "bf16"):
            dtype = torch.float16 if strategy == "fp16" else _prefer_bf16()
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                trust_remote_code=config.trust_remote_code,
                torch_dtype=dtype,
                device_map=config.device_map,
                use_safetensors=config.use_safetensors,
            )

        else:  # "auto"
            dtype = _prefer_bf16() if torch.cuda.is_available() else None
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                trust_remote_code=config.trust_remote_code,
                torch_dtype=dtype,
                device_map=config.device_map,
                use_safetensors=config.use_safetensors,
            )

    except Exception as e:
        # Fallback robusto
        print(f"⚠️ Falló la estrategia '{strategy}' ({e}). Cargando FP16/BF16…")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=config.trust_remote_code,
            torch_dtype=_prefer_bf16(),
            device_map=config.device_map,
            use_safetensors=config.use_safetensors,
        )

    pipe = pipeline(
        task="text-generation",
        model=model,
        tokenizer=tokenizer,
        device_map=config.device_map,
        return_full_text=False,
    )

    _local_pipelines[cache_key] = pipe
    return pipe
