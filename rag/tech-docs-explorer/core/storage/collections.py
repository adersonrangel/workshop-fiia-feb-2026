"""ChromaDB collection management.

This module provides functions for:
- Getting or creating collections
- Clearing the database
- Getting collection statistics
"""

import gc
import shutil
import time
from typing import Any, Dict

from chromadb.api.models.Collection import Collection

from config import get_settings

from .client import get_chroma_client, invalidate_client


def get_or_create_collection(name: str = "tech_docs") -> Collection:
    """Get an existing collection or create it if it doesn't exist.

    Args:
        name: Name of the collection. Default is "tech_docs".

    Returns:
        ChromaDB Collection instance.

    Examples:
        >>> collection = get_or_create_collection()
        >>> collection.count()
        42

        >>> collection = get_or_create_collection("custom_collection")
    """
    client = get_chroma_client()

    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},  # Use cosine similarity for retrieval
    )


def clear_database() -> Dict[str, Any]:
    """Clear all data from ChromaDB using proper client invalidation and directory cleanup.

    This will:
    1. Use ChromaDB's reset() method if client exists
    2. Invalidate the client completely
    3. Delete the entire ChromaDB persistence directory
    4. Recreate the directory structure

    WARNING: This operation is irreversible and will delete ALL indexed documents.

    Returns:
        Dictionary with operation status and message.

    Examples:
        >>> result = clear_database()
        >>> print(result["message"])
        "Base de datos limpiada exitosamente. Todos los documentos indexados fueron eliminados."
    """
    settings = get_settings()
    persist_path = settings.get_chroma_path()

    try:
        print(f"[CLEAR_DB] Starting database cleanup at: {persist_path}")

        # Step 1: Invalidate the client (handles reset and cleanup internally)
        invalidate_client()

        # Step 2: Force garbage collection
        gc.collect()
        print("[CLEAR_DB] Garbage collection completed")

        # Step 3: Wait for file handles to be fully released
        time.sleep(1.5)

        # Step 4: Delete persistence directory if it exists
        if persist_path.exists():
            print(f"[CLEAR_DB] Deleting directory: {persist_path}")
            try:
                shutil.rmtree(persist_path)
                print("[CLEAR_DB] Directory deleted successfully")
            except Exception as rm_error:
                print(f"[CLEAR_DB] Warning during directory deletion: {rm_error}")
                # Try again after a short wait
                time.sleep(0.5)
                shutil.rmtree(persist_path, ignore_errors=True)

                # Verify deletion succeeded after retry
                if persist_path.exists():
                    error_msg = (
                        f"Failed to delete ChromaDB directory after retry. "
                        f"Path: {persist_path}, Original error: {rm_error}"
                    )
                    print(f"[CLEAR_DB ERROR] {error_msg}")
                    raise RuntimeError(error_msg) from rm_error
        else:
            print(f"[CLEAR_DB] Directory does not exist: {persist_path}")

        # Step 5: Wait before recreating
        time.sleep(0.5)

        # Step 6: Recreate the directory
        persist_path.mkdir(parents=True, exist_ok=True)
        print(f"[CLEAR_DB] Directory recreated: {persist_path}")

        # Step 7: Final wait to ensure filesystem is ready
        time.sleep(0.3)

        return {
            "success": True,
            "message": "Base de datos limpiada exitosamente. Todos los documentos indexados fueron eliminados.",
            "path": str(persist_path),
        }

    except Exception as e:
        error_msg = f"Error al limpiar base de datos: {str(e)}"
        print(f"[CLEAR_DB ERROR] {error_msg}")
        return {
            "success": False,
            "message": error_msg,
            "path": str(persist_path),
        }


def get_collection_stats(collection_name: str = "tech_docs") -> Dict[str, Any]:
    """Get statistics about a collection.

    Args:
        collection_name: Name of the collection to query.

    Returns:
        Dictionary with collection statistics (count, name, exists).
        - exists: True if collection exists, False otherwise (regardless of count)
        - count: Number of items in collection, or 0 if not found

    Examples:
        >>> stats = get_collection_stats()
        >>> print(f"Documents indexed: {stats['count']}")
        >>> print(f"Collection exists: {stats['exists']}")
    """
    try:
        client = get_chroma_client()

        # Check if collection exists without creating it
        try:
            collection = client.get_collection(collection_name)
            count = collection.count()
            return {"name": collection_name, "count": count, "exists": True}
        except Exception:
            # Collection doesn't exist
            return {"name": collection_name, "count": 0, "exists": False}

    except Exception as e:
        return {"name": collection_name, "count": 0, "exists": False, "error": str(e)}


__all__ = ["get_or_create_collection", "clear_database", "get_collection_stats"]
