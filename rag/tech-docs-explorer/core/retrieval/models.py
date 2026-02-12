"""Data models for RAG retrieval operations."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RAGConfig:
    """Configuration for RAG query execution.

    Attributes:
        similarity_threshold: Minimum similarity score for chunk inclusion (0.0-1.0)
        top_k: Maximum number of chunks to retrieve
        use_hyde: Enable HyDE (Hypothetical Document Embeddings) query transformation
        use_reranking: Enable LLM-based reranking of retrieved chunks
        debug_mode: Enable debug information in response
    """

    similarity_threshold: float = 0.45
    top_k: int = 5
    use_hyde: bool = False
    use_reranking: bool = False
    debug_mode: bool = False


@dataclass
class ChunkInfo:
    """Information about a retrieved chunk.

    Attributes:
        text: Content of the chunk
        score: Similarity score (0.0-1.0)
        metadata: Additional metadata (source, stack, etc.)
        used: Whether this chunk was used in the response (passed threshold filter)
    """

    text: str
    score: float
    metadata: dict = field(default_factory=dict)
    used: bool = True


@dataclass
class ResponseMetrics:
    """Performance metrics for RAG query execution.

    Attributes:
        retrieval_time_ms: Time spent on retrieval (milliseconds)
        llm_time_ms: Time spent on LLM generation (milliseconds)
        total_time_ms: Total query execution time (milliseconds)
        chunks_retrieved: Number of chunks retrieved before filtering
        chunks_after_filter: Number of chunks after similarity filtering
        debug_mode: Whether debug mode was enabled for this query
        use_hyde: Whether HyDE was enabled for this query
        use_reranking: Whether reranking was enabled for this query
        query_tokens: Tokens in the query (for embedding)
        llm_input_tokens: Tokens in LLM input (estimated)
        llm_output_tokens: Tokens in LLM output (estimated)
        estimated_cost: Estimated total cost in USD
    """

    retrieval_time_ms: float
    llm_time_ms: float
    total_time_ms: float
    chunks_retrieved: int
    chunks_after_filter: int
    debug_mode: bool = False
    use_hyde: bool = False
    use_reranking: bool = False
    query_tokens: int = 0
    llm_input_tokens: int = 0
    llm_output_tokens: int = 0
    estimated_cost: float = 0.0


@dataclass
class RAGResponse:
    """Complete response from RAG query.

    Attributes:
        answer: Generated answer from LLM
        source_chunks: List of chunks used to generate the answer (passed filter)
        all_chunks: List of all retrieved chunks with used flag
        metrics: Performance metrics for the query
        hyde_query: Transformed query if HyDE was used
    """

    answer: str
    source_chunks: list[ChunkInfo]
    all_chunks: list[ChunkInfo]
    metrics: ResponseMetrics
    hyde_query: Optional[str] = None
