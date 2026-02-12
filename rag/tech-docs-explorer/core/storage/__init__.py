"""ChromaDB storage management.

This module provides functions to interact with ChromaDB for vector storage and retrieval:
- Client management (get_chroma_client, invalidate_client)
- Collection operations (get_or_create_collection, clear_database, get_collection_stats)
"""

from .client import get_chroma_client, invalidate_client
from .collections import clear_database, get_collection_stats, get_or_create_collection

__all__ = [
    # Client
    "get_chroma_client",
    "invalidate_client",
    # Collections
    "get_or_create_collection",
    "clear_database",
    "get_collection_stats",
]
