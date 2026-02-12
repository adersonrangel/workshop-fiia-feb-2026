"""Streamlit helper functions for Tech Docs Explorer."""

import re
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Tuple

import streamlit as st
from chromadb import PersistentClient
from streamlit.runtime.uploaded_file_manager import UploadedFile

from config import get_settings
from core.helpers.pricing import format_cost
from core.indexing import IndexStats
from core.storage import get_chroma_client
from llm import get_llm_provider


def validate_url(url: str) -> bool:
    """
    Validate URL format using regex.

    Args:
        url: URL string to validate

    Returns:
        True if URL is valid HTTP/HTTPS, False otherwise
    """
    pattern = r"^https?://.+"
    return bool(re.match(pattern, url))


@contextmanager
def save_uploaded_file(uploaded_file: UploadedFile) -> Generator[str, None, None]:
    """
    Context manager that saves Streamlit UploadedFile to a temporary file.

    The temporary file is automatically deleted when the context exits,
    ensuring proper resource cleanup.

    Args:
        uploaded_file: Streamlit UploadedFile object

    Yields:
        Path to the saved temporary file (str)

    Example:
        >>> with save_uploaded_file(uploaded_file) as tmp_path:
        ...     loader = PDFLoader()
        ...     documents = loader.load(tmp_path)
        ...     # File is automatically deleted after this block
    """
    suffix = Path(uploaded_file.name).suffix
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)

    try:
        tmp_file.write(uploaded_file.getbuffer())
        tmp_file.flush()
        tmp_file.close()
        yield tmp_file.name
    finally:
        # Always close the file handle before attempting to delete
        try:
            tmp_file.close()
        except Exception:
            pass  # File may already be closed

        # Clean up: remove the temporary file
        try:
            Path(tmp_file.name).unlink(missing_ok=True)
        except Exception as e:
            # Log but don't raise - cleanup is best effort
            print(f"Warning: Could not delete temporary file {tmp_file.name}: {e}")


def display_index_stats(stats: IndexStats) -> None:
    """
    Display indexing statistics using Streamlit metrics.

    Args:
        stats: IndexStats object with indexing results
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="📄 Documentos Indexados", value=stats.documents_processed)

    with col2:
        st.metric(label="📦 Chunks Creados", value=stats.num_chunks)

    with col3:
        st.metric(label="⏱️ Tiempo de Procesamiento", value=f"{stats.time_taken:.2f}s")

    with col4:
        st.metric(
            label="💰 Costo Estimado",
            value=format_cost(stats.estimated_cost),
            help=f"Basado en {stats.embedding_tokens:,} tokens de embeddings",
        )


@st.cache_resource
def init_cached_resources() -> Tuple[PersistentClient, object]:
    """
    Initialize and cache ChromaDB client and LLM provider.

    These resources are expensive to create, so we cache them
    using @st.cache_resource to persist across reruns.

    Returns:
        Tuple of (ChromaDB client, LLM provider)
    """
    settings = get_settings()

    # Initialize ChromaDB client
    chroma_client = get_chroma_client()

    # Initialize LLM provider
    llm_provider = get_llm_provider(settings.llm_provider)

    return chroma_client, llm_provider
