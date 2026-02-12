"""Pricing utilities for estimating API costs.

This module provides utilities to estimate costs for LLM and embedding operations
based on token usage and pricing configuration.
"""

from typing import Any, Dict


def estimate_embedding_cost(num_tokens: int, pricing_config: Dict[str, Any]) -> float:
    """Estimate cost for embedding operation.

    Args:
        num_tokens: Number of tokens to embed
        pricing_config: Pricing configuration dict (from settings.embedding_pricing)

    Returns:
        Estimated cost in USD
    """
    price_per_1m = pricing_config.get("input_per_1m", 0.0)
    return (num_tokens / 1_000_000) * price_per_1m


def estimate_llm_cost(
    input_tokens: int, output_tokens: int, pricing_config: Dict[str, Any]
) -> float:
    """Estimate cost for LLM operation.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        pricing_config: Pricing configuration dict (from settings.llm_pricing or settings.rerank_pricing)

    Returns:
        Estimated cost in USD
    """
    input_price_per_1m = pricing_config.get("input_per_1m", 0.0)
    output_price_per_1m = pricing_config.get("output_per_1m", 0.0)

    input_cost = (input_tokens / 1_000_000) * input_price_per_1m
    output_cost = (output_tokens / 1_000_000) * output_price_per_1m

    return input_cost + output_cost


def format_cost(cost: float) -> str:
    """Format cost as a readable string with 8 decimals and USD indicator.

    Args:
        cost: Cost in USD

    Returns:
        Formatted cost string (e.g., "USD $0.00002800", "USD $0.15000000")
    """
    return f"USD ${cost:.8f}"
