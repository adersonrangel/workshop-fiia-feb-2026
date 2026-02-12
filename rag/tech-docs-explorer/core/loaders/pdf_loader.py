"""
PDF document loader for loading content from PDF files.

Uses LlamaIndex's SimpleDirectoryReader to parse PDF files.
"""

from pathlib import Path
from typing import List

from llama_index.core import SimpleDirectoryReader
from llama_index.core.schema import Document

from core.loaders.base import BaseLoader


class PDFLoader(BaseLoader):
    """
    Loader for PDF documents.

    Uses SimpleDirectoryReader with PDF filtering to extract text content
    from PDF files. Automatically adds metadata for source tracking.
    """

    def __init__(self):
        """
        Initialize the PDF loader.
        """
        pass

    def load(self, file_path: str) -> List[Document]:
        """
        Load a document from a PDF file.

        Args:
            file_path: Path to the PDF file to load.

        Returns:
            List of Document objects with content and metadata.

        Raises:
            ValueError: If file path is empty or file doesn't exist.
            Exception: If loading fails (invalid PDF, permission error, etc.).

        Examples:
            >>> loader = PDFLoader()
            >>> docs = loader.load("/path/to/document.pdf")
            >>> print(f"Loaded {len(docs)} documents from PDF")
        """
        if not file_path or not file_path.strip():
            raise ValueError("File path cannot be empty")

        path = Path(file_path)

        if not path.exists():
            raise ValueError(f"File not found: {file_path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        if path.suffix.lower() != ".pdf":
            raise ValueError(f"File is not a PDF: {file_path}")

        try:
            # Load PDF using SimpleDirectoryReader
            reader = SimpleDirectoryReader(
                input_files=[str(path)],
                required_exts=[".pdf"],
            )
            documents = reader.load_data()

            # Add metadata to each document
            for doc in documents:
                doc.metadata["source_type"] = self.get_source_type()
                doc.metadata["filename"] = path.name
                doc.metadata["file_path"] = str(path.absolute())

            return documents

        except Exception as e:
            raise Exception(f"Failed to load PDF from '{file_path}': {str(e)}") from e

    def get_source_type(self) -> str:
        """
        Get the source type identifier.

        Returns:
            String "pdf" identifying this as a PDF source.
        """
        return "pdf"
