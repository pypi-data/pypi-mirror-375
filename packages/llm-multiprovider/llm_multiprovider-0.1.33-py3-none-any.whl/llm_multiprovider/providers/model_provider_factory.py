import os
import asyncio
from typing import Type, Dict
from importlib import import_module

from llm_multiprovider.providers.base import ModelProviderBase


def _load(path: str) -> Type[ModelProviderBase]:
    """
    Dynamically import a provider class given its "module:ClassName" path.

    Example:
        _load("llm_multiprovider.providers.openai:OpenAIProvider")

    Args:
        path (str): A string in the format "module.submodule:ClassName".

    Returns:
        Type[ModelProviderBase]: The provider class.

    Raises:
        ImportError: If the module or class cannot be imported.
    """
    module_path, class_name = path.split(":")
    try:
        module = import_module(module_path)
        return getattr(module, class_name)
    except ImportError as e:
        raise ImportError(
            f"❌ Could not import provider '{path}'. "
            "This may happen if optional dependencies are missing. "
            "Please install the correct extra, e.g.: "
            "pip install 'llm_multiprovider[openai]' / '[groq]' / '[transformers]' ..."
        ) from e


class ModelProviderFactory:
    """Factory class to manage different model providers dynamically."""

    # Instead of directly importing providers at the top,
    # we map provider names to their "module:ClassName" path.
    PROVIDERS: Dict[str, str] = {
        "cerebras": "llm_multiprovider.providers.cerebras:CerebrasProvider",
        "groq": "llm_multiprovider.providers.groq:GroqProvider",
        "local": "llm_multiprovider.providers.local:LocalProvider",
        "ollama": "llm_multiprovider.providers.ollama:OllamaProvider",
        "openai": "llm_multiprovider.providers.openai:OpenAIProvider",
        "runpod_openai": "llm_multiprovider.providers.runpod_openai:RunpodOpenAIProvider",
        "runpod": "llm_multiprovider.providers.runpod:RunpodProvider",
        "together_ai": "llm_multiprovider.providers.together_ai:TogetherAIProvider",
        "openrouter": "llm_multiprovider.providers.openrouter:OpenRouterProvider",
    }

    @staticmethod
    def create_provider(provider_name: str, model_name: str, using_tokenizer: bool = False, tokenizer_name: str = None) -> ModelProviderBase:
        """
        Create an instance of the specified model provider.

        Args:
            provider_name (str): Name of the provider (e.g., "cerebras", "openai").
            model_name (str): Model identifier for the provider.
            using_tokenizer (bool): Optional flag for providers that need tokenizers.

        Returns:
            ModelProviderBase: An instance of the selected provider.

        Raises:
            ValueError: If the provider is unknown.
            ImportError: If the provider’s module is missing or its dependencies are not installed.
        """
        provider_name = provider_name.lower()
        if provider_name not in ModelProviderFactory.PROVIDERS:
            raise ValueError(
                f"❌ Unknown provider: {provider_name}. "
                f"Available providers: {list(ModelProviderFactory.PROVIDERS.keys())}"
            )

        # Lazy load the provider class only when requested
        provider_class = _load(ModelProviderFactory.PROVIDERS[provider_name])

        # Some providers support `using_tokenizer`, some don't → handle gracefully
        try:
            return provider_class(model_name, using_tokenizer=using_tokenizer, tokenizer_name=tokenizer_name)
        except TypeError:
            return provider_class(model_name)


# Example usage
async def main():
    provider_name = "ollama"  # or os.getenv("MODEL_PROVIDER", "openai")
    model_name = "qwen2.5:0.5b"  # or os.getenv("MODEL_NAME", "gpt-4-turbo")

    # Create the provider dynamically
    provider = ModelProviderFactory.create_provider(provider_name, model_name)

    # Use the provider
    response = await provider.generate_text("Hello, how are you?", temperature=0.7)
    print(f"🔹 Response: {response}")


if __name__ == "__main__":
    asyncio.run(main())
