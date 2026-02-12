"""Data models for indexing operations.

This module contains dataclasses representing:
- Indexing statistics (IndexStats)
- Document information (DocumentInfo)
- Chunk information (ChunkInfo)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class IndexStats:
    """Statistics from document indexing operation.

    Attributes:
        num_chunks: Number of chunks created
        time_taken: Total time in seconds
        documents_processed: Number of documents processed
        embedding_tokens: Total tokens used for embeddings (estimated)
        estimated_cost: Estimated cost in USD for the indexing operation
    """

    num_chunks: int
    time_taken: float
    documents_processed: int
    embedding_tokens: int = 0
    estimated_cost: float = 0.0


@dataclass
class DocumentInfo:
    """Summary information about an indexed document.

    Attributes:
        name: Document name (filename or URL)
        doc_type: Type of document (pdf, web, etc.)
        stack: Technology stack tag
        indexed_at: Timestamp when indexed
        num_chunks: Number of chunks for this document
        doc_id: Unique identifier for the document
    """

    name: str
    doc_type: str
    stack: str
    indexed_at: str
    num_chunks: int
    doc_id: str


@dataclass
class ChunkInfo:
    """Detailed information about a document chunk.

    Attributes:
        chunk_id: Unique identifier for the chunk
        text: Chunk text content (may be truncated)
        metadata: Full metadata dictionary
        score: Optional similarity score (for search results)
    """

    chunk_id: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    score: Optional[float] = None


@dataclass
class DocumentSummary:
    """Summary information for document explorer view.

    Attributes:
        name: Document name (filename or URL)
        doc_type: Type of document (pdf, web, etc.)
        stack: Technology stack tag
        indexed_at: Timestamp when indexed
        num_chunks: Number of chunks for this document
    """

    name: str
    doc_type: str
    stack: str
    indexed_at: str
    num_chunks: int


@dataclass
class ChunkDetail:
    """Detailed chunk information for explorer view.

    Attributes:
        chunk_id: Unique identifier for the chunk
        text: Full or preview text (first 300 chars)
        metadata: Complete metadata dictionary
        embedding: Optional embedding vector from ChromaDB
    """

    chunk_id: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[list[float]] = None


__all__ = ["IndexStats", "DocumentInfo", "ChunkInfo", "DocumentSummary", "ChunkDetail"]
