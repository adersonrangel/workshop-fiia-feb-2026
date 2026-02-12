"""
Base LLM Provider interface.

Defines the contract for LLM providers to enable easy switching between different providers
(OpenAI, Google, Ollama, etc.) without changing core application code.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    Any LLM provider implementation must inherit from this class and implement
    all abstract methods to ensure compatibility with the application.
    """

    @abstractmethod
    def get_llm(self, model_name: str | None = None) -> Any:
        """
        Get the main LLM instance for text generation.

        Args:
            model_name: Optional model name override. If None, uses default from settings.

        Returns:
            LLM instance (e.g., OpenAI, Gemini, Ollama).
        """
        pass

    @abstractmethod
    def get_embedding_model(self) -> Any:
        """
        Get the embedding model for vector generation.

        Returns:
            Embedding model instance (e.g., OpenAIEmbedding, GoogleEmbedding).
        """
        pass

    @abstractmethod
    def get_rerank_llm(self) -> Any:
        """
        Get the LLM instance for reranking chunks.

        Reranking typically uses a different (often smaller/cheaper) model than
        the main LLM for cost optimization.

        Returns:
            LLM instance for reranking.
        """
        pass
