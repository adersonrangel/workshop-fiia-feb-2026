"""
LLM provider module.

Provides a factory function to get LLM providers based on configuration.
"""

from config import get_settings
from llm.base import BaseLLMProvider
from llm.openai_provider import OpenAIProvider


# Registry of available providers
_PROVIDERS = {
    "openai": OpenAIProvider,
}


def get_llm_provider(provider_name: str | None = None) -> BaseLLMProvider:
    """
    Factory function to get an LLM provider instance.

    Args:
        provider_name: Name of the provider to use. If None, uses llm_provider from settings.
                      Supported values: "openai"

    Returns:
        Instance of the requested provider.

    Raises:
        ValueError: If the provider name is not recognized.

    Examples:
        >>> provider = get_llm_provider()  # Uses settings default
        >>> llm = provider.get_llm()

        >>> provider = get_llm_provider("openai")  # Explicit provider
        >>> embeddings = provider.get_embedding_model()
    """
    settings = get_settings()
    provider = provider_name or settings.llm_provider

    if provider not in _PROVIDERS:
        available = ", ".join(_PROVIDERS.keys())
        raise ValueError(
            f"Unknown LLM provider: '{provider}'. Available providers: {available}"
        )

    provider_class = _PROVIDERS[provider]
    return provider_class()


__all__ = [
    "BaseLLMProvider",
    "OpenAIProvider",
    "get_llm_provider",
]
