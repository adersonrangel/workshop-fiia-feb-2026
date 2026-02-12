"""
OpenAI LLM Provider implementation.

Provides OpenAI-specific implementations for LLM, embeddings, and reranking models.
"""

from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

from config import get_settings
from llm.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI implementation of BaseLLMProvider.

    Uses OpenAI models for text generation, embeddings, and reranking.
    All configuration is loaded from settings (API key, model names).
    """

    def __init__(self):
        """Initialize the provider and load settings."""
        self.settings = get_settings()

    def get_llm(self, model_name: str | None = None) -> OpenAI:
        """
        Get OpenAI LLM instance for text generation.

        Args:
            model_name: Optional model override. If None, uses llm_model from settings.

        Returns:
            OpenAI LLM instance configured with API key and model.
        """
        model = model_name or self.settings.llm_model
        return OpenAI(
            model=model,
            api_key=self.settings.openai_api_key,
            temperature=0.1,  # Low temperature for consistent, factual responses
        )

    def get_embedding_model(self) -> OpenAIEmbedding:
        """
        Get OpenAI embedding model.

        Returns:
            OpenAIEmbedding instance configured with API key and embedding model.
        """
        return OpenAIEmbedding(
            model=self.settings.embedding_model, api_key=self.settings.openai_api_key
        )

    def get_rerank_llm(self) -> OpenAI:
        """
        Get OpenAI LLM for reranking.

        Uses the rerank_model from settings (typically same as main LLM or smaller).

        Returns:
            OpenAI LLM instance for reranking.
        """
        return OpenAI(
            model=self.settings.rerank_model,
            api_key=self.settings.openai_api_key,
            temperature=0.0,  # Deterministic for consistent reranking
        )
