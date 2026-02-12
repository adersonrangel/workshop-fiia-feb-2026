"""
Web document loader for loading content from URLs.

Uses LlamaIndex's SimpleWebPageReader to fetch and parse web pages.
"""

from typing import List

from llama_index.core.schema import Document
from llama_index.readers.web import SimpleWebPageReader

from core.loaders.base import BaseLoader


class WebLoader(BaseLoader):
    """
    Loader for web pages via URLs.

    Uses SimpleWebPageReader to fetch HTML content and convert it to Document objects.
    Automatically adds metadata for source tracking.
    """

    def __init__(self, html_to_text: bool = True):
        """
        Initialize the web loader.

        Args:
            html_to_text: Whether to convert HTML to plain text. Default True.
        """
        self.html_to_text = html_to_text
        self.reader = SimpleWebPageReader(html_to_text=html_to_text)

    def load(self, url: str) -> List[Document]:
        """
        Load a document from a URL.

        Args:
            url: The URL to load content from.

        Returns:
            List of Document objects with content and metadata.

        Raises:
            ValueError: If URL is empty or invalid.
            Exception: If loading fails (network error, invalid URL, etc.).

        Examples:
            >>> loader = WebLoader()
            >>> docs = loader.load("https://fastapi.tiangolo.com/tutorial/first-steps/")
            >>> print(f"Loaded {len(docs)} documents")
        """
        if not url or not url.strip():
            raise ValueError("URL cannot be empty")

        try:
            # Load documents from URL
            documents = self.reader.load_data([url])

            # Add metadata to each document
            for doc in documents:
                doc.metadata["source_type"] = self.get_source_type()
                doc.metadata["source_url"] = url

            return documents

        except Exception as e:
            raise Exception(f"Failed to load content from URL '{url}': {str(e)}") from e

    def get_source_type(self) -> str:
        """
        Get the source type identifier.

        Returns:
            String "web" identifying this as a web source.
        """
        return "web"
