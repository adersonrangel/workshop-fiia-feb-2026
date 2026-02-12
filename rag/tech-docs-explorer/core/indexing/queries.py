"""Query functions for retrieving indexed documents and chunks.

This module provides functionality for:
- Retrieving summaries of all indexed documents
- Getting chunks for specific documents
"""

import hashlib
from typing import Any, Dict, List

from core.storage import get_or_create_collection

from .models import ChunkDetail, ChunkInfo, DocumentInfo, DocumentSummary


def get_indexed_documents() -> List[DocumentInfo]:
    """Retrieve summary information about all indexed documents.

    This function queries ChromaDB to get all document metadata,
    groups chunks by document, and returns summary information.

    Returns:
        List of DocumentInfo objects with document summaries

    Raises:
        RuntimeError: If database query fails

    Example:
        >>> docs = get_indexed_documents()
        >>> for doc in docs:
        ...     print(f"{doc.name}: {doc.num_chunks} chunks")
    """
    try:
        collection = get_or_create_collection("tech_docs")

        # Get all data from collection
        results = collection.get(include=["metadatas"])

        if not results["ids"]:
            return []

        # Group by document (using filename or source_url as identifier)
        doc_groups: Dict[str, Dict[str, Any]] = {}

        for chunk_id, metadata in zip(results["ids"], results["metadatas"]):
            # Determine document identifier (original_filename > filename > source_url)
            doc_name = (
                metadata.get("original_filename")
                or metadata.get("filename")
                or metadata.get("source_url", "Unknown")
            )

            if doc_name not in doc_groups:
                doc_groups[doc_name] = {
                    "name": doc_name,
                    "doc_type": metadata.get("source_type", "unknown"),
                    "stack": metadata.get("stack", ""),
                    "indexed_at": metadata.get("indexed_at", ""),
                    "chunks": [],
                    "doc_id": hashlib.sha256(doc_name.encode()).hexdigest()[:16],
                }

            doc_groups[doc_name]["chunks"].append(chunk_id)

        # Convert to DocumentInfo objects
        documents = [
            DocumentInfo(
                name=info["name"],
                doc_type=info["doc_type"],
                stack=info["stack"],
                indexed_at=info["indexed_at"],
                num_chunks=len(info["chunks"]),
                doc_id=info["doc_id"],
            )
            for info in doc_groups.values()
        ]

        # Sort by indexed_at (most recent first)
        documents.sort(key=lambda x: x.indexed_at, reverse=True)

        return documents

    except Exception as e:
        raise RuntimeError(f"Failed to retrieve indexed documents: {str(e)}") from e


def get_document_chunks(doc_id: str) -> List[ChunkInfo]:
    """Get all chunks for a specific document.

    Args:
        doc_id: Document identifier (hash of document name)

    Returns:
        List of ChunkInfo objects with chunk details

    Raises:
        ValueError: If doc_id is empty
        RuntimeError: If database query fails

    Example:
        >>> docs = get_indexed_documents()
        >>> if docs:
        ...     chunks = get_document_chunks(docs[0].doc_id)
        ...     print(f"Found {len(chunks)} chunks")
    """
    if not doc_id:
        raise ValueError("Document ID cannot be empty")

    try:
        collection = get_or_create_collection("tech_docs")

        # Get all data from collection in a single query
        results = collection.get(include=["metadatas", "documents"])

        if not results["ids"]:
            return []

        # First pass: find the document name that matches the doc_id
        doc_name = None
        for metadata in results["metadatas"]:
            candidate_name = (
                metadata.get("original_filename")
                or metadata.get("filename")
                or metadata.get("source_url", "")
            )
            candidate_id = hashlib.sha256(candidate_name.encode()).hexdigest()[:16]

            if candidate_id == doc_id:
                doc_name = candidate_name
                break

        if not doc_name:
            return []

        # Second pass: collect chunks for the matched document
        chunks = []
        for chunk_id, metadata, document in zip(
            results["ids"], results["metadatas"], results["documents"]
        ):
            chunk_doc_name = (
                metadata.get("original_filename")
                or metadata.get("filename")
                or metadata.get("source_url", "")
            )

            if chunk_doc_name == doc_name:
                # Handle None or missing document text
                if document is None or not document:
                    document = ""

                # Truncate text to 200 characters
                text = document[:200] if len(document) > 200 else document
                if len(document) > 200:
                    text += "..."

                chunks.append(
                    ChunkInfo(chunk_id=chunk_id, text=text, metadata=metadata)
                )

        return chunks

    except Exception as e:
        raise RuntimeError(f"Failed to retrieve document chunks: {str(e)}") from e


def get_all_documents_summary() -> List[DocumentSummary]:
    """Get summary information of all indexed documents for explorer view.

    This function retrieves all documents from ChromaDB and groups them
    by document name, returning simplified summary information optimized
    for the explorer UI.

    Returns:
        List of DocumentSummary objects sorted by indexed_at (newest first)

    Raises:
        RuntimeError: If database query fails

    Example:
        >>> summaries = get_all_documents_summary()
        >>> for doc in summaries:
        ...     print(f"{doc.name} ({doc.doc_type}): {doc.num_chunks} chunks")
    """
    try:
        collection = get_or_create_collection("tech_docs")

        # Get all metadata from collection
        results = collection.get(include=["metadatas"])

        if not results["ids"]:
            return []

        # Group chunks by document identifier
        doc_groups: Dict[str, Dict[str, Any]] = {}

        for metadata in results["metadatas"]:
            # Determine document identifier (original_filename > filename > source_url)
            doc_name = (
                metadata.get("original_filename")
                or metadata.get("filename")
                or metadata.get("source_url", "Unknown")
            )

            if doc_name not in doc_groups:
                doc_groups[doc_name] = {
                    "name": doc_name,
                    "doc_type": metadata.get("source_type", "unknown"),
                    "stack": metadata.get("stack", ""),
                    "indexed_at": metadata.get("indexed_at", ""),
                    "num_chunks": 0,
                }

            doc_groups[doc_name]["num_chunks"] += 1

        # Convert to DocumentSummary objects
        summaries = [
            DocumentSummary(
                name=info["name"],
                doc_type=info["doc_type"],
                stack=info["stack"],
                indexed_at=info["indexed_at"],
                num_chunks=info["num_chunks"],
            )
            for info in doc_groups.values()
        ]

        # Sort by indexed_at (most recent first)
        summaries.sort(key=lambda x: x.indexed_at, reverse=True)

        return summaries

    except Exception as e:
        raise RuntimeError(f"Failed to retrieve document summaries: {str(e)}") from e


def get_chunks_for_document(doc_identifier: str) -> List[ChunkDetail]:
    """Get all chunks for a specific document by its name/URL identifier.

    Args:
        doc_identifier: Document name (filename or source_url)

    Returns:
        List of ChunkDetail objects with chunk text and metadata

    Raises:
        ValueError: If doc_identifier is empty
        RuntimeError: If database query fails

    Example:
        >>> chunks = get_chunks_for_document("https://example.com/docs")
        >>> for chunk in chunks:
        ...     print(f"Chunk {chunk.chunk_id[:8]}: {chunk.text[:50]}...")
    """
    if not doc_identifier:
        raise ValueError("Document identifier cannot be empty")

    try:
        collection = get_or_create_collection("tech_docs")

        # Get all data from collection including embeddings
        results = collection.get(include=["metadatas", "documents", "embeddings"])

        if not results["ids"]:
            return []

        # Filter chunks that belong to this document
        chunks = []
        embeddings = results.get("embeddings", [])
        for idx, (chunk_id, metadata, document) in enumerate(
            zip(results["ids"], results["metadatas"], results["documents"])
        ):
            # Check if this chunk belongs to the target document
            chunk_doc_name = (
                metadata.get("original_filename")
                or metadata.get("filename")
                or metadata.get("source_url", "")
            )

            if chunk_doc_name == doc_identifier:
                # Handle None or missing document text
                text = document if document else ""

                # Get embedding for this chunk (check bounds properly)
                embedding = (
                    embeddings[idx]
                    if embeddings is not None and idx < len(embeddings)
                    else None
                )

                chunks.append(
                    ChunkDetail(
                        chunk_id=chunk_id,
                        text=text,
                        metadata=metadata,
                        embedding=embedding,
                    )
                )

        return chunks

    except Exception as e:
        raise RuntimeError(f"Failed to retrieve chunks for document: {str(e)}") from e


__all__ = [
    "get_indexed_documents",
    "get_document_chunks",
    "get_all_documents_summary",
    "get_chunks_for_document",
]
