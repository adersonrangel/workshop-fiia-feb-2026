"""UI helper for displaying pricing information."""

import streamlit as st

from config import get_settings


def render_pricing_table() -> None:
    """Render pricing information in a compact format for sidebar.

    Displays pricing per 1M tokens for all configured models.
    Uses a vertical layout optimized for narrow sidebars.
    """
    settings = get_settings()

    st.markdown("**Precios OpenAI por 1M tokens**")
    st.caption("Actualiza estos valores en `config.yaml` al cambiar de modelo")

    # LLM Model
    llm_pricing = settings.llm_pricing
    with st.container():
        st.markdown(f"**🤖 LLM:** `{llm_pricing.get('name', 'N/A')}`")
        st.text(f"In:  USD ${llm_pricing.get('input_per_1m', 0):.2f}")
        st.text(f"Out: USD ${llm_pricing.get('output_per_1m', 0):.2f}")

    st.divider()

    # Embedding Model
    embed_pricing = settings.embedding_pricing
    with st.container():
        st.markdown(f"**🧠 Embeddings:** `{embed_pricing.get('name', 'N/A')}`")
        st.text(f"In:  USD ${embed_pricing.get('input_per_1m', 0):.2f}")

    st.divider()

    # Rerank Model
    rerank_pricing = settings.rerank_pricing
    with st.container():
        st.markdown(f"**📊 Rerank:** `{rerank_pricing.get('name', 'N/A')}`")
        st.text(f"In:  USD ${rerank_pricing.get('input_per_1m', 0):.2f}")
        st.text(f"Out: USD ${rerank_pricing.get('output_per_1m', 0):.2f}")

    st.caption(
        "💡 Costos mostrados en la app son **datos reales** de tokens reportados por OpenAI"
    )
