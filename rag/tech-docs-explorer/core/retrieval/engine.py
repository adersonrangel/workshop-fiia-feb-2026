"""RAG retrieval engine implementation."""

import time

import tiktoken
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from llama_index.core.indices.query.query_transform import HyDEQueryTransform
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import TransformQueryEngine
from llama_index.vector_stores.chroma import ChromaVectorStore

from config.settings import Settings as AppSettings
from core.helpers.pricing import estimate_embedding_cost, estimate_llm_cost
from core.storage import get_or_create_collection
from llm import get_llm_provider

from .models import ChunkInfo, RAGConfig, RAGResponse, ResponseMetrics
from .transforms import apply_reranking


def query(query_str: str, config: RAGConfig) -> RAGResponse:
    """Execute a RAG query against the indexed documents.

    Args:
        query_str: User's query string
        config: RAG configuration (top_k, threshold, etc.)

    Returns:
        RAGResponse with answer, source chunks, and metrics

    Raises:
        ValueError: If database is empty
    """
    start_time = time.time()
    app_settings = AppSettings()

    # Create token counter for tracking all operations
    token_counter = TokenCountingHandler(
        tokenizer=tiktoken.encoding_for_model(app_settings.llm_model).encode
    )
    callback_manager = CallbackManager([token_counter])

    # Get LLM provider
    llm_provider = get_llm_provider(app_settings.llm_provider)
    llm = llm_provider.get_llm()
    llm.callback_manager = callback_manager

    embed_model = llm_provider.get_embedding_model()
    embed_model.callback_manager = callback_manager

    # Create rerank LLM with callback manager (for cost tracking)
    rerank_llm = llm_provider.get_rerank_llm()
    rerank_llm.callback_manager = callback_manager

    # Set global Settings for LlamaIndex (this ensures all components use the same callback)
    Settings.llm = llm
    Settings.embed_model = embed_model
    Settings.callback_manager = callback_manager

    # Load index
    collection = get_or_create_collection("tech_docs")
    count = collection.count()
    if count == 0:
        raise ValueError(
            "La base de datos está vacía. Por favor, indexa algunos documentos primero "
            "usando la pestaña de Indexación."
        )

    vector_store = ChromaVectorStore(chroma_collection=collection)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    # Execute query with timing
    query_start = time.time()

    # Phase 1: Create base query engine (will use Settings.llm and Settings.callback_manager)
    postprocessor = SimilarityPostprocessor(
        similarity_cutoff=config.similarity_threshold
    )

    base_query_engine = index.as_query_engine(
        similarity_top_k=config.top_k,
        node_postprocessors=[postprocessor],
    )

    # Phase 2: Apply HyDE transformation if enabled
    hyde_query = None
    if config.use_hyde:
        hyde_transform = HyDEQueryTransform(include_original=True)  # Uses Settings.llm

        # Generate hypothetical document for debug visibility
        hypothetical_doc = hyde_transform._llm.predict(
            hyde_transform._hyde_prompt, context_str=query_str
        )
        hyde_query = str(hypothetical_doc).strip()

        query_engine = TransformQueryEngine(
            query_engine=base_query_engine,
            query_transform=hyde_transform,
        )
    else:
        query_engine = base_query_engine

    # Phase 3: Execute query
    response = query_engine.query(query_str)

    # Phase 4: Get retrieved nodes for analysis
    retriever = index.as_retriever(similarity_top_k=config.top_k)
    retrieved_nodes = retriever.retrieve(query_str)
    chunks_retrieved = len(retrieved_nodes)

    # Apply same filtering to understand what was used
    filtered_nodes = postprocessor.postprocess_nodes(retrieved_nodes)

    # Phase 5: Apply reranking if enabled (for demo purposes, on filtered nodes)
    if config.use_reranking:
        filtered_nodes = apply_reranking(filtered_nodes, query_str, rerank_llm, top_n=5)

    query_end = time.time()

    # Get IDs of filtered nodes to mark which were used
    filtered_ids = {node.node_id for node in filtered_nodes}

    # Build all_chunks from retrieved_nodes with used flag
    all_chunks = []
    source_chunks = []

    for node in retrieved_nodes:
        is_used = node.node_id in filtered_ids
        chunk_info = ChunkInfo(
            text=node.text,
            score=node.score if node.score is not None else 0.0,
            metadata=node.metadata if node.metadata else {},
            used=is_used,
        )
        all_chunks.append(chunk_info)
        if is_used:
            source_chunks.append(chunk_info)

    # Calculate metrics
    total_time = time.time() - start_time
    query_time = query_end - query_start

    # Approximate split: ~30% retrieval, ~70% LLM (rough estimate)
    # In reality, these happen sequentially but we can't easily separate them
    retrieval_time = query_time * 0.3
    llm_time = query_time * 0.7

    # Get real token usage from callback
    query_tokens = token_counter.total_embedding_token_count
    llm_input_tokens = token_counter.prompt_llm_token_count
    llm_output_tokens = token_counter.completion_llm_token_count

    # Calculate costs with real token counts
    embedding_cost = estimate_embedding_cost(
        query_tokens, app_settings.embedding_pricing
    )
    llm_cost = estimate_llm_cost(
        llm_input_tokens, llm_output_tokens, app_settings.llm_pricing
    )

    # Total cost
    total_cost = embedding_cost + llm_cost

    metrics = ResponseMetrics(
        retrieval_time_ms=retrieval_time * 1000,
        llm_time_ms=llm_time * 1000,
        total_time_ms=total_time * 1000,
        chunks_retrieved=chunks_retrieved,
        chunks_after_filter=len(source_chunks),
        debug_mode=config.debug_mode,
        use_hyde=config.use_hyde,
        use_reranking=config.use_reranking,
        query_tokens=query_tokens,
        llm_input_tokens=llm_input_tokens,
        llm_output_tokens=llm_output_tokens,
        estimated_cost=total_cost,
    )

    # Build RAG response
    rag_response = RAGResponse(
        answer=str(response),
        source_chunks=source_chunks,
        all_chunks=all_chunks,
        metrics=metrics,
        hyde_query=hyde_query,
    )

    return rag_response
