"""
Document loaders for various file types and sources.

This module provides loaders for different document types:
- WebLoader: Load content from URLs
- PDFLoader: Load content from PDF files
- BaseLoader: Abstract base class for custom loaders
"""

from pathlib import Path
from typing import Union

from core.loaders.base import BaseLoader
from core.loaders.pdf_loader import PDFLoader
from core.loaders.web_loader import WebLoader


def get_loader(source: Union[str, Path]) -> BaseLoader:
    """
    Auto-detect and return the appropriate loader for a source.

    Args:
        source: URL string or file path to load from.

    Returns:
        Appropriate loader instance (WebLoader or PDFLoader).

    Raises:
        ValueError: If source type cannot be determined.

    Examples:
        >>> loader = get_loader("https://example.com")
        >>> isinstance(loader, WebLoader)
        True

        >>> loader = get_loader("/path/to/doc.pdf")
        >>> isinstance(loader, PDFLoader)
        True
    """
    source_str = str(source)

    # Check if it's a URL
    if source_str.startswith(("http://", "https://")):
        return WebLoader()

    # Check if it's a PDF file
    path = Path(source_str)
    if path.suffix.lower() == ".pdf":
        return PDFLoader()

    raise ValueError(
        f"Cannot determine loader type for source: {source_str}. "
        "Supported types: URLs (http/https) and PDF files (.pdf)"
    )


__all__ = [
    "BaseLoader",
    "WebLoader",
    "PDFLoader",
    "get_loader",
]
