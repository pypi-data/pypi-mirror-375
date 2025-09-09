import json
import traceback
import os
import re
import httpx
from typing import List, Dict, Any, Optional, Union, Optional, Tuple
from json_repair import repair_json


DEFAULT_TIMEOUT = 60.0


# Añade este helper (por encima de send_request o en utilidades)
def _build_local_gen_args(params: Dict[str, Any]) -> Dict[str, Any]:
    gen = {"max_new_tokens": params["max_tokens"]}

    # Normaliza temperatura
    temp = params.get("temperature", 0.7)
    try:
        temp = float(temp) if temp is not None else 0.7
    except Exception:
        temp = 0.7

    if temp <= 0:
        # Greedy determinista (evita el ValueError de transformers)
        gen["do_sample"] = False
        # No pasamos temperature/top_p/top_k en greedy
    else:
        gen["do_sample"] = True
        gen["temperature"] = temp
        if params.get("top_p") is not None:
            gen["top_p"] = params["top_p"]
        if params.get("top_k") is not None:
            gen["top_k"] = params["top_k"]

    # Opcionales
    if params.get("eos_token_id") is not None:
        gen["eos_token_id"] = params["eos_token_id"]
    if params.get("eos_token_ids") is not None:
        gen["eos_token_id"] = params["eos_token_ids"]  # HF acepta int o lista

    return gen

def messages_to_prompt(messages: List[Dict[str, str]]) -> str:
    """
    Fallback simple (solo si el proveedor no soporta /chat/completions).
    """
    parts = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        parts.append(f"{role}: {content}")
    return "\n".join(parts)

def _merge_params(defaults: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    out = defaults.copy()
    out.update({k: v for k, v in overrides.items() if v is not None})
    return out

def _normalize_stop(stop: Optional[Union[str, List[str]]]) -> Optional[List[str]]:
    if stop is None:
        return None
    if isinstance(stop, str):
        return [stop]
    return list(stop)

def _normalize_output_texts_from_chat(choices: List[Dict[str, Any]]) -> List[str]:
    texts = []
    for ch in choices or []:
        msg = ch.get("message") or {}
        texts.append((msg.get("content") or "").strip())
    return texts

def _normalize_output_texts_from_completions(choices: List[Dict[str, Any]]) -> List[str]:
    return [ (c.get("text") or "").strip() for c in (choices or []) ]

# ---------- Enrutador multiproveedor ----------


async def send_request(
    provider: str,
    model_name: str,
    *,
    prompt: Optional[str] = None,
    messages: Optional[List[Dict[str, str]]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Enrutador multiproveedor. Devuelve SIEMPRE:
    {
      "choices": [{"text": "...", "thinking": "..."}],  # thinking solo si existe
      "raw": <respuesta completa del proveedor>,
      "prompt_logprobs": { "tokens": [...], "token_logprobs": [...], "token_ids": [...] }  # opcional
    }
    """
    import re
    if not prompt and not messages:
        raise ValueError("Debes proporcionar 'prompt' o 'messages'.")

    provider = (provider or "").lower()
    # ¡OJO! NO lower-case del model_name; muchos modelos son case-sensitive (HF)
    stop_default = None  # mejor no imponer "}" como stop global
    default_params = {
        "max_tokens": 300,
        "temperature": 0.7,
        "presence_penalty": 0.0,
        "repetition_penalty": 0.0,
        "stop": stop_default,
        "n": 1,
        "logprobs": None,     # para completions que lo soporten
        "echo": None,         # para completions con logprobs del prompt
        "top_p": None,
    }
    params = _merge_params(default_params, params or {})
    params["stop"] = _normalize_stop(params.get("stop"))

    # --- helper: extraer y limpiar bloques <think> ---
    def _extract_and_strip_think(text: str) -> Tuple[str, Optional[str]]:
        if not text:
            return "", None
        pat = re.compile(r"<think>(.*?)</think>", re.DOTALL | re.IGNORECASE)
        pieces = pat.findall(text)
        thinking = "\n\n".join(p.strip() for p in pieces) if pieces else None
        cleaned = pat.sub("", text).strip()
        return cleaned, thinking

    # modelos que suelen devolver <think>...</think>
    def _is_thinky_model(name: str) -> bool:
        ln = (name or "").lower()
        return any(tag in ln for tag in ["deepseek", "r1", "qwen", "qwen3"])


    try:
        # ---------- TogetherAI ----------
        if provider == "together_ai":
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Bearer {os.getenv('TOGETHER_API_KEY')}",
            }
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                if messages is not None:
                    payload = {
                        "model": model_name,
                        "messages": messages,
                        "temperature": params["temperature"],
                        "n": params["n"],
                        "max_tokens": params["max_tokens"],
                        "stop": params["stop"],
                    }
                    resp = await client.post(
                        os.getenv("TOGETHER_CHAT_URL", "https://api.together.xyz/v1/chat/completions"),
                        json=payload, headers=headers
                    )
                    resp.raise_for_status()
                    raw = resp.json()
                    texts = _normalize_output_texts_from_chat(raw.get("choices", []))
                    out = {"choices": [{"text": (t or "").strip()} for t in texts], "raw": raw}
                else:
                    payload = {
                        "model": model_name,
                        "prompt": prompt,
                        "temperature": params["temperature"],
                        "n": params["n"],
                        "repetition_penalty": params["repetition_penalty"],
                        "presence_penalty": params["presence_penalty"],
                        "max_tokens": params["max_tokens"],
                        "stop": params["stop"],
                        "logprobs": params.get("logprobs"),
                        "echo": params.get("echo"),
                        "top_p": params.get("top_p"),
                    }
                    resp = await client.post(
                        os.getenv("TOGETHER_BASE_URL", "https://api.together.xyz/v1/completions"),
                        json=payload, headers=headers
                    )
                    resp.raise_for_status()
                    raw = resp.json()
                    texts = _normalize_output_texts_from_completions(raw.get("choices", []))
                    out = {"choices": [{"text": (t or "").strip()} for t in texts], "raw": raw}
                    # prompt logprobs (si viene)
                    if raw.get("prompt") and isinstance(raw["prompt"], list) and raw["prompt"][0].get("logprobs"):
                        lp = raw["prompt"][0]["logprobs"]
                        out["prompt_logprobs"] = {
                            "tokens": lp.get("tokens") or [],
                            "token_logprobs": lp.get("token_logprobs") or [],
                            "token_ids": lp.get("token_ids") or [],
                        }

        # ---------- Ollama ----------
        elif provider == "ollama":
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                if messages is not None:
                    payload = {
                        "model": model_name,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": params["temperature"],
                            "presence_penalty": params["presence_penalty"],
                            "repetition_penalty": params["repetition_penalty"],
                            "num_predict": params["max_tokens"],
                            "stop": params["stop"],
                            "top_p": params.get("top_p"),
                        },
                    }
                    resp = await client.post(
                        os.getenv("OLLAMA_CHAT_URL", "http://localhost:11434/api/chat"),
                        json=payload
                    )
                    resp.raise_for_status()
                    raw = resp.json()
                    text = (raw.get("message", {}) or {}).get("content", "") or ""
                    out = {"choices": [{"text": text.strip()}], "raw": raw}
                else:
                    payload = {
                        "model": model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": params["temperature"],
                            "presence_penalty": params["presence_penalty"],
                            "repetition_penalty": params["repetition_penalty"],
                            "num_predict": params["max_tokens"],
                            "stop": params["stop"],
                            "top_p": params.get("top_p"),
                        },
                    }
                    resp = await client.post(
                        os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api/generate"),
                        json=payload
                    )
                    resp.raise_for_status()
                    raw = resp.json()
                    text = raw.get("response", "") or ""
                    out = {"choices": [{"text": text.strip()}], "raw": raw}

        # ---------- Local (Transformers / HF) ----------
        elif provider == "local":
            from llm_multiprovider.utils.local_utils import LocalLoadConfig, get_local_pipeline
            # Construye prompt según haya messages o prompt
            strategy = (params or {}).get("local_strategy") or os.getenv("LOCAL_STRATEGY", "auto")
            cfg = LocalLoadConfig(strategy=strategy, device_map=os.getenv("LOCAL_DEVICE_MAP", "auto"))
            pipe = get_local_pipeline(model_name, config=cfg)
            tok = pipe.tokenizer

            if messages is not None and hasattr(tok, "apply_chat_template"):
                actual_prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            else:
                actual_prompt = prompt if prompt is not None else messages_to_prompt(messages or [])

            # ✅ Construye argumentos de generación seguros (greedy si temperature<=0)
            gen_args = _build_local_gen_args(params)

            outputs = pipe(actual_prompt, **gen_args)
            text = outputs[0]["generated_text"]
            out = {"choices": [{"text": (text or "").strip()}], "raw": {"pipeline": True, "outputs": outputs}}

        # ---------- Cerebras (OpenAI-like) ----------
        elif provider == "cerebras":
            headers = {
                "Authorization": f"Bearer {os.getenv('CEREBRAS_API_KEY')}",
                "Content-Type": "application/json"
            }
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                if messages is not None:
                    payload = {
                        "model": model_name,
                        "messages": messages,
                        "temperature": params["temperature"],
                        "max_tokens": params["max_tokens"],
                        "stop": params["stop"],
                        "top_p": params.get("top_p"),
                    }
                    resp = await client.post(
                        os.getenv("CEREBRAS_CHAT_URL", "https://api.cerebras.ai/v1/chat/completions"),
                        json=payload, headers=headers
                    )
                    resp.raise_for_status()
                    raw = resp.json()
                    texts = _normalize_output_texts_from_chat(raw.get("choices", []))
                    out = {"choices": [{"text": (t or "").strip()} for t in texts], "raw": raw}
                else:
                    payload = {
                        "model": model_name,
                        "prompt": prompt,
                        "temperature": params["temperature"],
                        "max_tokens": params["max_tokens"],
                        "stop": params["stop"],
                        "top_p": params.get("top_p"),
                    }
                    resp = await client.post(
                        os.getenv("CEREBRAS_BASE_URL", "https://api.cerebras.ai/v1/completions"),
                        json=payload, headers=headers
                    )
                    resp.raise_for_status()
                    raw = resp.json()
                    texts = _normalize_output_texts_from_completions(raw.get("choices", []))
                    out = {"choices": [{"text": (t or "").strip()} for t in texts], "raw": raw}

        # ---------- Groq (OpenAI-like) ----------
        # ---------- Groq (solo chat/completions) ----------
        elif provider == "groq":
            headers = {
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            }

            # Unifica: si no vienen messages, convertimos prompt -> messages
            msgs = messages if messages is not None else [{"role": "user", "content": prompt or ""}]

            payload = {
                "model": model_name,
                "messages": msgs,
                "temperature": params["temperature"],
                "max_tokens": params["max_tokens"],
                "stop": params["stop"],
                "top_p": params.get("top_p"),
                # Groq soporta logprobs en chat para tokens generados
                "logprobs": params.get("logprobs"),
                "top_logprobs": params.get("top_logprobs"),
                # NO existe echo+logprobs en chat; ignoraremos params["echo"]
            }

            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                resp = await client.post(
                    os.getenv("GROQ_CHAT_URL", "https://api.groq.com/openai/v1/chat/completions"),
                    json=payload, headers=headers
                )
            resp.raise_for_status()
            raw = resp.json()

            texts = _normalize_output_texts_from_chat(raw.get("choices", []))
            out = {"choices": [{"text": (t or "").strip()} for t in texts], "raw": raw}

            # Groq chat no devuelve prompt_logprobs (no echo)
            # Si quieres leer logprobs de tokens generados:
            # raw["choices"][0].get("logprobs")  <- si el modelo lo soporta

            return out


        # ---------- OpenRouter (OpenAI-like) ----------
        elif provider == "openrouter":
            headers = {
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json",
                "HTTP-Referer": os.getenv("OPENROUTER_REFERRER", ""),
                "X-Title": os.getenv("OPENROUTER_APP_NAME", "LLM-Multiprovider"),
            }
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                if messages is not None:
                    payload = {
                        "model": model_name,
                        "messages": messages,
                        "temperature": params["temperature"],
                        "max_tokens": params["max_tokens"],
                        "stop": params["stop"],
                        "top_p": params.get("top_p"),
                        "n": params["n"],
                    }
                    resp = await client.post(
                        os.getenv("OPENROUTER_CHAT_URL", "https://openrouter.ai/api/v1/chat/completions"),
                        json=payload, headers=headers
                    )
                    resp.raise_for_status()
                    raw = resp.json()
                    texts = _normalize_output_texts_from_chat(raw.get("choices", []))
                    out = {"choices": [{"text": (t or "").strip()} for t in texts], "raw": raw}
                else:
                    payload = {
                        "model": model_name,
                        "prompt": prompt,
                        "temperature": params["temperature"],
                        "max_tokens": params["max_tokens"],
                        "stop": params["stop"],
                        "top_p": params.get("top_p"),
                        "n": params["n"],
                        "logprobs": params.get("logprobs"),
                        "echo": params.get("echo"),
                    }
                    resp = await client.post(
                        os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/completions"),
                        json=payload, headers=headers
                    )
                    resp.raise_for_status()
                    raw = resp.json()
                    texts = _normalize_output_texts_from_completions(raw.get("choices", []))
                    out = {"choices": [{"text": (t or "").strip()} for t in texts], "raw": raw}
                    if raw.get("choices") and raw["choices"][0].get("logprobs") and params.get("echo"):
                        lp = raw["choices"][0]["logprobs"]
                        out["prompt_logprobs"] = {
                            "tokens": lp.get("tokens") or [],
                            "token_logprobs": lp.get("token_logprobs") or [],
                            "token_ids": [],
                        }

        # ---------- OpenAI (OpenAI-like) ----------
        elif provider == "openai":
            base_url = (os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY is not set.")

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            org_id = os.getenv("OPENAI_ORG_ID")
            project = os.getenv("OPENAI_PROJECT")
            if org_id:
                headers["OpenAI-Organization"] = org_id
            if project:
                headers["OpenAI-Project"] = project

            # Unifica: si solo hay prompt, lo convertimos a messages
            msgs = messages if messages is not None else [{"role": "user", "content": prompt or ""}]

            payload = {
                "model": model_name,
                "messages": msgs,
                "temperature": params["temperature"],
                "max_tokens": params["max_tokens"],
                "stop": params["stop"],
                "top_p": params.get("top_p"),
            }

            # Chat logprobs: logprobs=True y top_logprobs=int
            lp = params.get("logprobs")
            tlp = params.get("top_logprobs")
            if (isinstance(lp, bool) and lp) or isinstance(lp, int):
                payload["logprobs"] = True
                if isinstance(lp, int) and tlp is None:
                    payload["top_logprobs"] = lp
                elif isinstance(tlp, int):
                    payload["top_logprobs"] = tlp

            # response_format opcional (útil para JSON)
            if params.get("response_format") is not None:
                payload["response_format"] = params["response_format"]

            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                resp = await client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
                resp.raise_for_status()
                raw = resp.json()

            texts = _normalize_output_texts_from_chat(raw.get("choices", []))
            out = {"choices": [{"text": (t or "").strip()} for t in texts], "raw": raw}



        else:
            raise Exception(f"Provider '{provider}' not declared")

        # -------- Post-procesado común: extraer <think> y adjuntar 'thinking' --------
        if _is_thinky_model(model_name):
            for choice in out.get("choices", []):
                original = choice.get("text", "")
                cleaned, thinking = _extract_and_strip_think(original)
                choice["text"] = cleaned
                if thinking:
                    choice["thinking"] = thinking     
                print("original --> " + str(original))
                print("cleaned --> " + str(cleaned))
                print("thinking --> " + str(thinking))

        return out

    except Exception as err:
        print(f"❌ Error en send_request (provider={provider}): {err}")
        raise




def extract_json_object(raw: str, preoutput: str) -> dict:
    """
    Extrae y decodifica un JSON válido desde un string sucio generado por LLM.
    Usa el preoutput si se conoce para reconstruir el texto.
    Devuelve un dict. Si falla, intenta repararlo con jsonrepair. Si aún falla, devuelve {}.
    """
    if not raw:
        print("⛔ Empty input")
        return {}

    raw = raw.strip()
    print(f"🔍 Raw after strip: {repr(raw)}")

    # Eliminar triple backticks si los hay
    raw = re.sub(r"```.*?$", "", raw, flags=re.DOTALL).strip()

    # Reconstruir si preoutput se pasó
    if preoutput:
        # Solo añadimos preoutput si NO está ya en raw
        if not raw.startswith(preoutput):
            raw = preoutput + raw
            print(f"🔧 Reconstructed full JSON: {repr(raw)}")
        else:
            print("✅ Preoutput already present in raw, skipping reconstruction")

    # En caso de que haya basura antes del JSON
    if not raw.startswith("{"):
        idx = raw.find("{")
        if idx >= 0:
            raw = raw[idx:]

    # 👉 Cortar en el primer cierre válido del objeto JSON
    closing_idx = raw.find("}") + 1
    if closing_idx > 0:
        raw = raw[:closing_idx]

    # Intento normal
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except Exception as e:
        traceback.print_exc()
        print("⚠️ Failed to parse JSON object:", e)

    # Intento de reparación
    try:
        print("🛠 Trying to repair JSON...")
        repaired = repair_json(raw)
        parsed = json.loads(repaired)
        print("✅ Repaired JSON successfully.")
        if isinstance(parsed, dict):
            print("📄 Repaired JSON content:")
            print(json.dumps(parsed, indent=2, ensure_ascii=False))  # legible y con soporte UTF-8
            return parsed
    except Exception as e:
        traceback.print_exc()
        print("❌ Failed to repair JSON:", e)

    return {}
