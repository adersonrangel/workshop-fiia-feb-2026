"""ChromaDB client management.

This module provides the ChromaDB persistent client with singleton pattern.
"""

import threading
from typing import Optional

import chromadb

from config import get_settings


# Global client instance (singleton pattern)
_chroma_client: Optional[chromadb.PersistentClient] = None
# Flag to track if client was invalidated (e.g., after database clear)
_client_invalidated: bool = False
# Thread lock for safe singleton creation
_chroma_client_lock = threading.Lock()


def invalidate_client() -> None:
    """Mark the current client as invalidated and clear the reference.

    This should be called when the database is cleared to ensure
    a fresh client is created on the next access.

    Thread-safe: Uses the same lock as get_chroma_client() to prevent
    race conditions during invalidation.
    """
    global _chroma_client, _client_invalidated

    print("[CHROMA_CLIENT] Invalidating client...")

    # Thread-safe invalidation using the same lock
    with _chroma_client_lock:
        # Try to close the client properly if it exists
        if _chroma_client is not None:
            try:
                # Clear system cache first (before closing)
                if hasattr(_chroma_client, "clear_system_cache"):
                    _chroma_client.clear_system_cache()
                    print("[CHROMA_CLIENT] System cache cleared")

                # Then close the client if available
                if hasattr(_chroma_client, "close"):
                    _chroma_client.close()
                    print("[CHROMA_CLIENT] Client closed explicitly")
            except Exception as e:
                print(f"[CHROMA_CLIENT] Warning during cleanup: {e}")

        _chroma_client = None
        _client_invalidated = True
        print("[CHROMA_CLIENT] Client invalidated and cleared")


def get_chroma_client() -> chromadb.PersistentClient:
    """Get or create the ChromaDB persistent client.

    Uses a singleton pattern with thread-safe locking to ensure only one
    client instance exists. All access is synchronized to prevent TOCTOU
    race conditions with invalidate_client().

    The client persists data to the directory specified in settings (CHROMA_PERSIST_DIR).

    Returns:
        ChromaDB PersistentClient instance.

    Examples:
        >>> client = get_chroma_client()
        >>> collections = client.list_collections()
    """
    global _chroma_client, _client_invalidated

    # Always acquire lock to prevent TOCTOU races with invalidate_client()
    with _chroma_client_lock:
        # Check if client needs recreation due to invalidation
        if _client_invalidated:
            _chroma_client = None
            _client_invalidated = False
            print("[CHROMA_CLIENT] Forcing client recreation after invalidation")

        # Check if client needs to be created
        if _chroma_client is None:
            settings = get_settings()
            persist_path = settings.get_chroma_path()

            # Ensure the directory exists
            persist_path.mkdir(parents=True, exist_ok=True)

            print(f"[CHROMA_CLIENT] Creating new ChromaDB client at: {persist_path}")

            # Create client with explicit settings to handle SQLite properly
            _chroma_client = chromadb.PersistentClient(
                path=str(persist_path),
                settings=chromadb.Settings(
                    allow_reset=True,
                    anonymized_telemetry=False,
                    is_persistent=True,
                    persist_directory=str(persist_path),
                ),
            )

            print("[CHROMA_CLIENT] Client created successfully")

            # Force a simple operation to ensure client is fully initialized
            try:
                _chroma_client.heartbeat()
                print("[CHROMA_CLIENT] Client heartbeat successful")
            except Exception as e:
                print(f"[CHROMA_CLIENT] Error: heartbeat failed: {e}")
                _chroma_client = None
                raise RuntimeError(f"ChromaDB client initialization failed: {e}") from e

        # Return client while still holding lock to prevent TOCTOU
        return _chroma_client


__all__ = ["get_chroma_client", "invalidate_client"]
