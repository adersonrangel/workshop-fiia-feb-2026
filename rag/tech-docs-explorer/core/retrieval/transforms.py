"""Query transformation and post-processing functions for advanced RAG."""

from llama_index.core.postprocessor import LLMRerank


def apply_reranking(nodes: list, query_str: str, llm, top_n: int = 5) -> list:
    """Rerank retrieved nodes using LLM for improved relevance.

    Uses a dedicated LLM to re-score and reorder chunks based on semantic
    relevance to the query, beyond simple embedding similarity.

    Args:
        nodes: List of retrieved nodes from initial retrieval
        query_str: Original query string
        llm: LLM instance to use for reranking (should have callback_manager configured)
        top_n: Maximum number of nodes to return after reranking (default: 5)

    Returns:
        List of reranked nodes, ordered by LLM-assessed relevance

    Example:
        >>> rerank_llm = llm_provider.get_rerank_llm()
        >>> rerank_llm.callback_manager = callback_manager
        >>> filtered_nodes = apply_reranking(nodes, "dependency injection", rerank_llm, top_n=5)
    """
    # Create reranker with provided LLM (which has callback_manager for token tracking)
    reranker = LLMRerank(llm=llm, top_n=top_n)

    # Apply reranking to nodes
    reranked_nodes = reranker.postprocess_nodes(nodes, query_str=query_str)

    return reranked_nodes
