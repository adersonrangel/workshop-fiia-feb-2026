"""Main entry point for Tech Docs Explorer - Streamlit application."""

import streamlit as st

from config import get_settings
from ui.pricing_display import render_pricing_table
from ui.tabs.chat_tab import render_chat_tab
from ui.tabs.explorer_tab import render_explorer_tab
from ui.tabs.indexing_tab import render_indexing_tab


def init_session_state():
    """Initialize Streamlit session state variables."""
    if "resources" not in st.session_state:
        st.session_state.resources = []


def main():
    """Run the Tech Docs Explorer Streamlit application."""
    # Configure page
    st.set_page_config(
        page_title="Tech Docs Explorer",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Load settings
    settings = get_settings()

    # Initialize session state
    init_session_state()

    # Header
    st.title("🔍 Tech Docs Explorer")
    st.markdown(
        """
        **Aplicación Educativa RAG** - Explora documentación técnica con IA
        
        Esta aplicación demuestra Generación Aumentada por Recuperación (RAG) para documentación técnica.
        Indexa URLs y PDFs, luego haz preguntas para obtener respuestas impulsadas por IA basadas en el contenido indexado.
        """
    )

    # Display configuration info in sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        st.info(f"**Proveedor LLM:** {settings.llm_provider}")

        with st.expander("📋 Información de la App"):
            st.write(f"**Nombre:** {settings.app_name}")
            st.write(f"**Ruta ChromaDB:** {settings.get_chroma_path()}")

        # Pricing table in sidebar (informational, applies to all tabs)
        with st.expander("💰 Precios por Modelo", expanded=False):
            render_pricing_table()

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📥 Indexación", "💬 Chat", "📂 Explorador"])

    with tab1:
        render_indexing_tab()

    with tab2:
        render_chat_tab()

    with tab3:
        render_explorer_tab()


if __name__ == "__main__":
    main()
