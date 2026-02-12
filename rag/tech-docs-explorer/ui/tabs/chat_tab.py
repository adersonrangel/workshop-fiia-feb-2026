"""Chat tab UI for RAG queries."""

import html

import streamlit as st

from config import get_settings
from core.helpers.pricing import format_cost
from core.retrieval import RAGConfig, query


def render_chat_tab() -> None:
    """Render the chat interface for RAG queries."""
    # Initialize session state
    if "rag_response" not in st.session_state:
        st.session_state.rag_response = None
    if "pending_query" not in st.session_state:
        st.session_state.pending_query = None
    if "pending_config" not in st.session_state:
        st.session_state.pending_config = None

    # Get settings for defaults
    settings = get_settings()

    st.subheader("💬 Consulta tus Documentos")

    # Configuration RAG
    st.markdown("#### ⚙️ Configuración RAG")
    col1, col2 = st.columns(2)

    with col1:
        similarity_threshold = st.slider(
            "Umbral de Similitud",
            min_value=0.0,
            max_value=1.0,
            value=settings.default_threshold,
            step=0.05,
            help="Umbral mínimo de similitud para incluir chunks",
        )

    with col2:
        top_k = st.slider(
            "Top K",
            min_value=1,
            max_value=20,
            value=settings.default_top_k,
            step=1,
            help="Número máximo de chunks a recuperar",
        )

    # Advanced options (3 checkboxes in columns)
    col1, col2, col3 = st.columns(3)
    with col1:
        use_hyde = st.checkbox(
            "🔮 HyDE",
            value=settings.hyde_enabled,
            help="Query transformation para mejor retrieval",
        )
    with col2:
        use_reranking = st.checkbox(
            "📊 Rerank",
            value=settings.reranking_enabled,
            help="Re-ordenar chunks por relevancia LLM",
        )
    with col3:
        debug_mode = st.checkbox(
            "🐛 Debug", value=False, help="Mostrar info detallada del proceso"
        )

    st.divider()

    # Question input
    prompt = st.text_area(
        "Escribe tu pregunta:",
        height=100,
    )

    # Search button
    if st.button("🔍 Buscar Respuesta", type="primary"):
        if not prompt:
            st.warning("⚠️ Por favor, escribe una pregunta.")
        else:
            # Clear response and schedule query for next render
            st.session_state.rag_response = None
            st.session_state.pending_query = prompt
            st.session_state.last_query = prompt  # Save for debug display
            st.session_state.pending_config = RAGConfig(
                similarity_threshold=similarity_threshold,
                top_k=top_k,
                use_hyde=use_hyde,
                use_reranking=use_reranking,
                debug_mode=debug_mode,
            )
            st.rerun()

    # Execute pending query (after rerun, UI is clean)
    if st.session_state.pending_query:
        try:
            with st.spinner("Buscando respuesta..."):
                st.session_state.rag_response = query(
                    st.session_state.pending_query,
                    st.session_state.pending_config,
                )
        except ValueError as e:
            st.error(f"❌ Error: {e}")
        except Exception as e:
            st.error(f"❌ Error inesperado: {e}")
        finally:
            # Clear pending query
            st.session_state.pending_query = None
            st.session_state.pending_config = None

    # Show response (persists across slider changes)
    if st.session_state.rag_response:
        response = st.session_state.rag_response

        st.divider()
        st.markdown("### Respuesta")

        # Translate LlamaIndex's "Empty Response" to Spanish
        answer = response.answer
        if answer.strip() == "Empty Response":
            answer = "Respuesta Vacía"
        st.markdown(answer)

        # Metrics (collapsible)
        with st.expander("📊 Métricas", expanded=False):
            m = response.metrics
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Tiempo Total", f"{m.total_time_ms:.0f} ms")
            c2.metric("Chunks Recuperados", m.chunks_retrieved)
            c3.metric("Chunks Filtrados", m.chunks_after_filter)
            c4.metric(
                "💰 Costo Estimado",
                format_cost(m.estimated_cost),
                help=f"Query: {m.query_tokens} tokens | LLM: {m.llm_input_tokens} in + {m.llm_output_tokens} out",
            )

        # All chunks (collapsible) - shows which were used
        if response.all_chunks:
            used_count = len(response.source_chunks)
            total_count = len(response.all_chunks)
            with st.expander(
                f"📦 Chunks Recuperados ({total_count} total / {used_count} usados)",
                expanded=False,
            ):
                for i, chunk in enumerate(response.all_chunks, 1):
                    # Visual indicator: green if used, red if filtered out
                    if chunk.used:
                        status = "✅ Usado"
                        bg_color = "#d4edda"  # light green
                        border_color = "#28a745"
                    else:
                        status = "❌ Filtrado"
                        bg_color = "#f8d7da"  # light red
                        border_color = "#dc3545"

                    st.markdown(f"**Chunk {i}** | Score: {chunk.score:.3f} | {status}")

                    # Source metadata line (prefer original_filename for PDFs)
                    source = (
                        chunk.metadata.get("source_url")
                        or chunk.metadata.get("original_filename")
                        or chunk.metadata.get("filename")
                        or chunk.metadata.get("file_path", "Fuente desconocida")
                    )
                    stack = chunk.metadata.get("stack", "")
                    meta_parts = [f"📍 {source}"]
                    if stack:
                        meta_parts.append(f"🏷️ {stack}")
                    st.markdown(
                        f'<div style="font-size: 0.85em; color: #666;">'
                        f"{'  |  '.join(meta_parts)}</div>",
                        unsafe_allow_html=True,
                    )

                    # Scrollable container for full chunk text
                    with st.container(height=250, border=True):
                        # Escape HTML to prevent link auto-conversion
                        escaped_text = html.escape(chunk.text)
                        st.markdown(
                            f'<div style="font-size: 0.9em; background-color: {bg_color}; '
                            f"padding: 10px; border-radius: 5px; "
                            f"border-left: 4px solid {border_color}; "
                            f'min-height: 100%; box-sizing: border-box; white-space: pre-wrap;">'
                            f"<style>a {{ pointer-events: none; text-decoration: none; color: inherit; }}</style>"
                            f"{escaped_text}</div>",
                            unsafe_allow_html=True,
                        )

                    if i < len(response.all_chunks):
                        st.divider()

        # Debug panel (only visible if debug_mode was enabled) - AT THE END
        if response.metrics.debug_mode:
            with st.expander("🐛 Info de Debug", expanded=False):
                st.markdown("**Pipeline RAG (orden de ejecución):**")

                # Pipeline order visualization (dynamic based on enabled features)
                pipeline_stages = []

                if response.metrics.use_hyde:
                    pipeline_stages.append("🔮 **HyDE**")

                pipeline_stages.append("🔍 **Retrieval**")
                pipeline_stages.append("🔬 **Filtrado**")

                if response.metrics.use_reranking:
                    pipeline_stages.append("📊 **Reranking**")

                pipeline_stages.append("🤖 **LLM**")

                pipeline_text = " → ".join(pipeline_stages)
                st.info(pipeline_text)

                st.markdown("---")

                # HyDE transformation details
                if response.metrics.use_hyde and response.hyde_query:
                    st.markdown("**🔮 Transformación HyDE (ANTES de retrieval):**")
                    st.success(
                        "HyDE genera un documento hipotético que se embediza para mejorar la búsqueda"
                    )
                    with st.expander(
                        "Ver documento hipotético generado", expanded=False
                    ):
                        st.markdown("**Query original:**")
                        st.code(st.session_state.get("last_query", "N/A"))
                        st.markdown("**Documento hipotético (usado para retrieval):**")
                        st.text_area(
                            "Hypothetical doc",
                            value=response.hyde_query,
                            height=150,
                            disabled=True,
                            label_visibility="collapsed",
                        )
                    st.markdown("---")

                # Visual pipeline metrics
                st.markdown("**Métricas del Pipeline:**")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("1️⃣ Chunks Recuperados", response.metrics.chunks_retrieved)
                with col2:
                    st.metric(
                        "2️⃣ Chunks Filtrados", response.metrics.chunks_after_filter
                    )
                with col3:
                    rerank_indicator = (
                        "✅ Aplicado"
                        if response.metrics.use_reranking
                        else "⚪ No activado"
                    )
                    st.metric("3️⃣ Reranking", rerank_indicator)
                with col4:
                    hyde_indicator = (
                        "✅ Aplicado" if response.metrics.use_hyde else "⚪ No activado"
                    )
                    st.metric("🔮 HyDE", hyde_indicator)

                st.markdown("---")

                # Show top 3 final chunks (after all transformations)
                st.markdown(
                    "**Top 3 Chunks Finales** (después de todas las transformaciones):"
                )
                top_3 = response.source_chunks[:3]
                if not top_3:
                    st.info("No hay chunks que cumplan el umbral de similitud")
                else:
                    for i, chunk in enumerate(top_3, 1):
                        source = (
                            chunk.metadata.get("source_url")
                            or chunk.metadata.get("original_filename")
                            or chunk.metadata.get("filename")
                            or chunk.metadata.get("file_path", "")
                        )
                        source_label = f" | 📍 {source}" if source else ""
                        st.markdown(
                            f"**#{i}** - Score: `{chunk.score:.3f}`{source_label}"
                        )
                        # Scrollable container for full chunk text
                        with st.container(height=150, border=True):
                            st.text(chunk.text)
