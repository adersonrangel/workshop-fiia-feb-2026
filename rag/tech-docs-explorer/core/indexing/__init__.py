"""Indexing module for processing and storing documents.

This module provides:
- Data models for indexing operations (IndexStats, DocumentInfo, ChunkInfo, DocumentSummary, ChunkDetail)
- Document indexing pipeline (index_documents)
- Query functions for retrieving indexed documents and chunks
"""

from .models import (
    ChunkDetail,
    ChunkInfo,
    DocumentInfo,
    DocumentSummary,
    IndexStats,
)
from .pipeline import index_documents
from .queries import (
    get_all_documents_summary,
    get_chunks_for_document,
    get_document_chunks,
    get_indexed_documents,
)

__all__ = [
    # Models
    "IndexStats",
    "DocumentInfo",
    "ChunkInfo",
    "DocumentSummary",
    "ChunkDetail",
    # Pipeline
    "index_documents",
    # Queries
    "get_indexed_documents",
    "get_document_chunks",
    "get_all_documents_summary",
    "get_chunks_for_document",
]
