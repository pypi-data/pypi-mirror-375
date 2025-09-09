from dotenv import load_dotenv
load_dotenv()
import asyncio
from llm_multiprovider.utils.metrics import *
from llm_multiprovider.providers.model_provider_factory import ModelProviderFactory



async def run_common_tests(provider, model_name):
    """Run the tests common to all providers."""
    # 🔹 Testing get_json_response
    print("\n🔹 Testing get_json_response...")
    preoutput = '{"city": "'
    json_prompt = """
    Give me ONLY a valid JSON object in the following format:

    {"city": "<capital city>", "country": "<country name>"}

    Do not include explanations or text outside the JSON.
    What is the capital of France?
    """ + preoutput
    json_result = await provider.get_json_response(json_prompt, preoutput, temperature=0)
    print(f"🔹 JSON result: {json_result}")

    print("\n🔹 Testing generate_text...")
    response = await provider.generate_text("Hello, how are you?", temperature=0.7, n=1)
    print(f"🔹 Respuesta: {response}")

    print("\n🔹 Testing chat_completion...")
    chat_response = await provider.chat_completion(
        [{"role": "user", "content": "Tell me a joke"}],
        temperature=0.7,
        max_tokens=500
    )
    print(f"🔹 Respuesta: {chat_response}")


async def run_logprobs_tests(provider, model_name):
    """Run logprobs-related tests only if provider supports them."""
    if not getattr(provider, "supports_logprobs", False):
        print("\n⚠️ Skipping logprobs tests: not supported by this provider.")
        return

    print("\n🔹 Testing logprobs...")
    logprobs_response = await provider.logprobs("The capital of USA is ")
    print(f"🔹 Logprobs response: {logprobs_response}")

    print("\n🔹 Testing logprobs for target output...")
    prompt = "What is the capital of USA?"
    target_output = "The capital of USA is Washington D.C."

    model_output_list = await provider.generate_text(prompt, temperature=0, n=1, max_tokens=20)
    print("model_output", model_output_list)
    model_output = model_output_list[0]
    print("model_output", model_output)

    logprobs_response = await provider.get_logprobs_for_target_output(prompt, target_output)

    if logprobs_response:
        print("\n🔍 Logprobs Details:")
        print(f"Reconstructed target text: {logprobs_response.get('reconstructed_text')}")
        print(f"Tokens: {logprobs_response.get('tokens')}")
        print(f"Token IDs: {logprobs_response.get('token_ids')}")
        print(f"Token log probabilities: {logprobs_response.get('token_logprobs')}")

        metrics_to_calculate = ["log_probability", "perplexity", "meteor_score", "cosine_similarity"]
        metrics = calculate_metrics_from_logprobs(
            logprobs_response.get("token_logprobs"),
            metrics_to_calculate,
            target_output,
            model_output,
            model_type="all-mpnet-base-v2",
            debug=True,
        )
        print("metrics", metrics)
    else:
        print("❌ Failed to fetch logprobs for target output.")


# ---------- Provider-specific tests ----------
async def test_together_ai():
    model_name = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    provider_name = "together_ai"
    print(f"\n🚀 Testing TogetherAI ({model_name})")
    provider = ModelProviderFactory.create_provider(provider_name=provider_name, model_name=model_name, using_tokenizer=True, tokenizer_name="meta-llama/Llama-3.3-70B-Instruct")
    await run_common_tests(provider, model_name)
    await run_logprobs_tests(provider, model_name)


async def test_openrouter():
    model_name = "meta-llama/llama-3.3-70b-instruct:free"
    provider_name = "openrouter"
    print(f"\n🚀 Testing OpenRouter ({model_name})")
    provider = ModelProviderFactory.create_provider(provider_name=provider_name, model_name=model_name, using_tokenizer=True, tokenizer_name="meta-llama/Llama-3.3-70B-Instruct")
    await run_common_tests(provider, model_name)
    await run_logprobs_tests(provider, model_name)


async def test_ollama():
    model_name = "qwen3:8b"
    provider_name = "ollama"
    print(f"\n🚀 Testing Ollama ({model_name})")
    provider = ModelProviderFactory.create_provider(provider_name=provider_name, model_name=model_name, using_tokenizer=True, tokenizer_name="Qwen/Qwen2.5-7B-Instruct")
    await run_common_tests(provider, model_name)
    await run_logprobs_tests(provider, model_name)


async def test_cerebras():
    model_name = "llama3.3-70b"
    provider_name = "cerebras"
    print(f"\n🚀 Testing Cerebras ({model_name})")
    provider = ModelProviderFactory.create_provider(provider_name=provider_name, model_name=model_name, using_tokenizer=True, tokenizer_name="meta-llama/Llama-3.3-70B-Instruct")
    await run_common_tests(provider, model_name)
    await run_logprobs_tests(provider, model_name)


async def test_groq():
    model_name = "llama-3.3-70b-versatile"
    provider_name = "groq"
    print(f"\n🚀 Testing Groq ({model_name})")
    provider = ModelProviderFactory.create_provider(provider_name=provider_name, model_name=model_name, using_tokenizer=True, tokenizer_name="meta-llama/Llama-3.3-70B-Instruct")
    await run_common_tests(provider, model_name)
    await run_logprobs_tests(provider, model_name)

async def test_local():
    model_name = "Qwen/Qwen2.5-0.5B-Instruct"
    provider_name = "local"
    print(f"\n🚀 Testing Local ({model_name})")
    provider = ModelProviderFactory.create_provider(provider_name=provider_name, model_name=model_name, using_tokenizer=True, tokenizer_name="Qwen/Qwen2.5-0.5B-Instruct")
    await run_common_tests(provider, model_name)
    await run_logprobs_tests(provider, model_name)    


async def test_runpod():
    model_name = "TensorML/fanslove_creator_70B_AWQ"
    provider_name = "runpod"
    print(f"\n🚀 Testing Runpod ({model_name})")
    provider = ModelProviderFactory.create_provider(provider_name=provider_name, model_name=model_name, using_tokenizer=True, tokenizer_name="mistralai/Mistral-7B-Instruct-v0.3")
    await run_common_tests(provider, model_name)
    await run_logprobs_tests(provider, model_name)   


async def test_runpod_openai():
    model_name = "TensorML/fanslove_creator_70B_AWQ"
    provider_name = "runpod_openai"
    print(f"\n🚀 Testing Runpod-OpenaI ({model_name})")
    provider = ModelProviderFactory.create_provider(provider_name=provider_name, model_name=model_name, using_tokenizer=True, tokenizer_name="mistralai/Mistral-7B-Instruct-v0.3")
    await run_common_tests(provider, model_name)
    await run_logprobs_tests(provider, model_name)   


async def test_openai():
    # Puedes cambiar el modelo por env var si quieres
    model_name = os.getenv("OPENAI_TEST_MODEL", "gpt-4o-mini")
    provider_name = "openai"
    print(f"\n🚀 Testing OpenAI ({model_name})")
    # Para OpenAI mejor no forzar tokenizer local
    provider = ModelProviderFactory.create_provider(
        provider_name=provider_name,
        model_name=model_name,
        using_tokenizer=False, 
        tokenizer_name="Xenova/gpt-4o"
    )
    await run_common_tests(provider, model_name)
    await run_logprobs_tests(provider, model_name)


# ---------- Main ----------
async def main():
    #await test_together_ai()
    #await test_openrouter()
    #await test_ollama()
    #await test_cerebras()
    #await test_groq()
    #await test_local()
    #await test_runpod()
    #await test_runpod_openai()
    await test_openai()




if __name__ == "__main__":
    asyncio.run(main())
