"""
Base loader interface for document loading.

Defines the contract for all document loaders to ensure consistent behavior
across different source types (web, PDF, markdown, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any, List

from llama_index.core.schema import Document


class BaseLoader(ABC):
    """
    Abstract base class for document loaders.

    All loader implementations must inherit from this class and implement
    the abstract methods to ensure compatibility with the indexing pipeline.
    """

    @abstractmethod
    def load(self, source: Any) -> List[Document]:
        """
        Load documents from the specified source.

        Args:
            source: The source to load from (URL, file path, etc.).
                   Type depends on the specific loader implementation.

        Returns:
            List of Document objects with content and metadata.

        Raises:
            Exception: If loading fails, should raise descriptive error.
        """
        pass

    @abstractmethod
    def get_source_type(self) -> str:
        """
        Get the type of source this loader handles.

        Returns:
            String identifying the source type (e.g., "web", "pdf", "markdown").
        """
        pass
