from dotenv import load_dotenv
load_dotenv()
import os
import asyncio
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




# ---------- Provider-specific tests ----------
async def test_together_ai():
    model_name = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    provider_name = "together_ai"
    print(f"\n🚀 Testing TogetherAI ({model_name})")
    provider = ModelProviderFactory.create_provider(provider_name=provider_name, model_name=model_name, using_tokenizer=False)
    await run_common_tests(provider, model_name)


async def test_openrouter():
    model_name = "meta-llama/llama-3.3-70b-instruct:free"
    provider_name = "openrouter"
    print(f"\n🚀 Testing OpenRouter ({model_name})")
    provider = ModelProviderFactory.create_provider(provider_name=provider_name, model_name=model_name, using_tokenizer=False)
    await run_common_tests(provider, model_name)


async def test_ollama():
    model_name = "qwen3:8b"
    provider_name = "ollama"
    print(f"\n🚀 Testing Ollama ({model_name})")
    provider = ModelProviderFactory.create_provider(provider_name=provider_name, model_name=model_name, using_tokenizer=False)
    await run_common_tests(provider, model_name)


async def test_cerebras():
    model_name = "llama3.3-70b"
    provider_name = "cerebras"
    print(f"\n🚀 Testing Cerebras ({model_name})")
    provider = ModelProviderFactory.create_provider(provider_name=provider_name, model_name=model_name, using_tokenizer=False)
    await run_common_tests(provider, model_name)


async def test_groq():
    model_name = "llama-3.3-70b-versatile"
    provider_name = "groq"
    print(f"\n🚀 Testing Groq ({model_name})")
    provider = ModelProviderFactory.create_provider(provider_name=provider_name, model_name=model_name, using_tokenizer=False)
    await run_common_tests(provider, model_name)

# async def test_local():
#     model_name = "Qwen/Qwen2.5-0.5B-Instruct"
#     provider_name = "local"
#     print(f"\n🚀 Testing Local ({model_name})")
#     provider = ModelProviderFactory.create_provider(provider_name=provider_name, model_name=model_name, using_tokenizer=False)
#     await run_common_tests(provider, model_name)


# async def test_runpod():
#     model_name = "TensorML/fanslove_creator_70B_AWQ"
#     provider_name = "runpod"
#     print(f"\n🚀 Testing Runpod ({model_name})")
#     provider = ModelProviderFactory.create_provider(provider_name=provider_name, model_name=model_name, using_tokenizer=False)
#     await run_common_tests(provider, model_name)


async def test_runpod_openai():
    model_name = "TensorML/fanslove_creator_70B_AWQ"
    provider_name = "runpod_openai"
    print(f"\n🚀 Testing Runpod-OpenaI ({model_name})")
    provider = ModelProviderFactory.create_provider(provider_name=provider_name, model_name=model_name, using_tokenizer=False)
    await run_common_tests(provider, model_name)


async def test_openai():
    # Puedes cambiar el modelo por env var si quieres
    model_name = os.getenv("OPENAI_TEST_MODEL", "gpt-4o-mini")
    provider_name = "openai"
    print(f"\n🚀 Testing OpenAI ({model_name})")
    # Para OpenAI mejor no forzar tokenizer local
    provider = ModelProviderFactory.create_provider(
        provider_name=provider_name,
        model_name=model_name,
        using_tokenizer=False
    )
    await run_common_tests(provider, model_name)


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
