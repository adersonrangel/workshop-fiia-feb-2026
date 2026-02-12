"""Document indexing pipeline.

This module provides functionality for processing and indexing documents
into the vector database with chunking and metadata.
"""

import hashlib
import time
from datetime import datetime
from typing import Any, Dict, List

import tiktoken
from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore

from config import get_settings
from core.helpers.pricing import estimate_embedding_cost
from core.storage import get_or_create_collection
from llm import get_llm_provider

from .models import IndexStats


def index_documents(documents: List[Document], metadata: Dict[str, Any]) -> IndexStats:
    """Index documents into the vector database with chunking and metadata.

    This function:
    1. Splits documents into chunks using SentenceSplitter
    2. Generates unique IDs for each chunk
    3. Adds user metadata (stack, indexed_at) to each node
    4. Creates embeddings using the configured embedding model
    5. Stores vectors in ChromaDB
    6. Returns indexing statistics

    Args:
        documents: List of LlamaIndex Document objects to index
        metadata: User metadata to add to all chunks (e.g., {"stack": "fastapi"})

    Returns:
        IndexStats with number of chunks, time taken, and documents processed

    Raises:
        ValueError: If documents list is empty
        RuntimeError: If indexing fails

    Example:
        >>> from llama_index.core import Document
        >>> docs = [Document(text="Hello world", metadata={"source": "test.pdf"})]
        >>> stats = index_documents(docs, {"stack": "demo"})
        >>> print(f"Created {stats.num_chunks} chunks")
    """
    if not documents:
        raise ValueError("No documents provided for indexing")

    start_time = time.time()
    settings = get_settings()

    try:
        # Create sentence splitter with config parameters
        splitter = SentenceSplitter(
            chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
        )

        # Split documents into nodes
        nodes = splitter.get_nodes_from_documents(documents)

        # Add timestamp to metadata (create copy to avoid mutating caller's dict)
        indexed_at = datetime.now().isoformat()
        new_metadata = {**metadata, "indexed_at": indexed_at}

        # Generate unique IDs and add metadata to each node
        for idx, node in enumerate(nodes):
            # Generate unique ID based on content hash + index + timestamp
            content_preview = node.get_content()[:100]
            source = node.metadata.get("source_url") or node.metadata.get(
                "file_path", ""
            )
            # Include index and precise timestamp to guarantee uniqueness
            id_string = f"{content_preview}{source}{idx}{time.time()}"
            unique_id = hashlib.sha256(id_string.encode()).hexdigest()[:16]
            node.id_ = unique_id

            # Add user metadata to node
            for key, value in new_metadata.items():
                node.metadata[key] = value

        # Get embedding model from LLM provider with token tracking
        provider = get_llm_provider(settings.llm_provider)

        # Create token counter for tracking embedding tokens
        token_counter = TokenCountingHandler(
            tokenizer=tiktoken.encoding_for_model(settings.embedding_model).encode
        )
        callback_manager = CallbackManager([token_counter])

        embed_model = provider.get_embedding_model()
        embed_model.callback_manager = callback_manager

        # Get or create ChromaDB collection
        collection = get_or_create_collection("tech_docs")

        # Create vector store and storage context
        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Create index and persist with callback manager for token tracking
        VectorStoreIndex(
            nodes=nodes,
            storage_context=storage_context,
            embed_model=embed_model,
            callback_manager=callback_manager,  # Pass callback to index
            show_progress=True,
        )

        # Get real token usage from callback
        total_tokens = token_counter.total_embedding_token_count
        estimated_cost = estimate_embedding_cost(
            total_tokens, settings.embedding_pricing
        )

        # Calculate statistics
        time_taken = time.time() - start_time

        return IndexStats(
            num_chunks=len(nodes),
            time_taken=time_taken,
            documents_processed=len(documents),
            embedding_tokens=total_tokens,
            estimated_cost=estimated_cost,
        )

    except Exception as e:
        raise RuntimeError(f"Failed to index documents: {str(e)}") from e


__all__ = ["index_documents"]
