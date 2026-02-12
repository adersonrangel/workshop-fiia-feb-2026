"""Explorer tab UI for browsing ChromaDB documents and chunks."""

import html
import time

import pandas as pd
import streamlit as st

from core.indexing import get_all_documents_summary, get_chunks_for_document
from core.storage import clear_database, invalidate_client


def render_explorer_tab() -> None:
    """Render the explorer interface for browsing indexed documents."""
    st.header("🔍 Explorador de ChromaDB")
    st.markdown(
        "Explora los documentos indexados, visualiza sus chunks y gestiona la base de datos."
    )

    # Load documents
    try:
        documents = get_all_documents_summary()
    except Exception as e:
        st.error(f"❌ Error al cargar documentos: {e}")
        documents = []

    if not documents:
        st.info(
            "📭 No hay documentos indexados. Ve al tab **Indexación** para agregar contenido."
        )
        # Show clear database section even when empty (in case of orphaned data)
        st.divider()
        _render_clear_database_section()
        return

    # Statistics banner
    total_chunks = sum(doc.num_chunks for doc in documents)
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("📚 Documentos", len(documents))
    with col_stat2:
        st.metric("🧩 Chunks Totales", total_chunks)
    with col_stat3:
        avg_chunks = total_chunks / len(documents) if documents else 0
        st.metric("📊 Promedio Chunks/Doc", f"{avg_chunks:.1f}")

    st.divider()

    # Documents table section
    st.subheader("📚 Documentos Indexados")
    st.caption("👆 Haz clic en una fila para ver los detalles del documento")

    # Create DataFrame for display
    df = pd.DataFrame(
        [
            {
                "Documento": doc.name,
                "Tipo": doc.doc_type,
                "Stack": doc.stack,
                "Chunks": doc.num_chunks,
                "Fecha Indexación": doc.indexed_at,
            }
            for doc in documents
        ]
    )

    # Display table with single-row selection
    selection = st.dataframe(
        df,
        width="stretch",
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        key="doc_table_selection",
        column_config={
            "Documento": st.column_config.TextColumn("📄 Documento", width="large"),
            "Tipo": st.column_config.TextColumn("📁 Tipo", width="small"),
            "Stack": st.column_config.TextColumn("🏷️ Stack", width="medium"),
            "Chunks": st.column_config.NumberColumn("🧩 Chunks", width="small"),
            "Fecha Indexación": st.column_config.TextColumn(
                "📅 Indexado", width="medium"
            ),
        },
    )

    # Check if a row is selected
    selected_rows = selection.selection.rows if selection.selection else []

    if selected_rows:
        selected_idx = selected_rows[0]
        selected_doc = documents[selected_idx]

        # Document details section
        st.divider()
        _render_document_details(selected_doc, selected_idx)
    else:
        st.divider()
        st.info("👆 Selecciona un documento de la tabla para ver sus detalles y chunks")

    # Clear database section at the bottom
    st.divider()
    _render_clear_database_section()


def _render_document_details(selected_doc, selected_idx: int) -> None:
    """Render the details section for a selected document."""
    # Header with document name
    st.subheader("📋 Detalles del Documento")

    # Info card with document metadata
    with st.container(border=True):
        # Document name prominently displayed
        st.markdown(f"### {selected_doc.name}")

        # Metadata in columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("**📁 Tipo**")
            st.code(selected_doc.doc_type, language=None)
        with col2:
            st.markdown("**🏷️ Stack**")
            st.code(selected_doc.stack, language=None)
        with col3:
            st.markdown("**🧩 Chunks**")
            st.code(str(selected_doc.num_chunks), language=None)
        with col4:
            st.markdown("**📅 Indexado**")
            st.code(selected_doc.indexed_at, language=None)

    # Chunks section
    st.divider()
    st.subheader("🧩 Chunks del Documento")

    # Get chunks for selected document
    try:
        chunks = get_chunks_for_document(selected_doc.name)
    except Exception as e:
        st.error(f"❌ Error al cargar chunks: {e}")
        chunks = []

    if not chunks:
        st.warning("⚠️ No se encontraron chunks para este documento.")
        return

    # Pagination controls
    chunks_per_page = 5
    total_pages = (len(chunks) + chunks_per_page - 1) // chunks_per_page

    # Initialize page in session state
    page_key = f"chunk_page_{selected_idx}"
    if page_key not in st.session_state:
        st.session_state[page_key] = 0

    # Reset page if out of bounds
    if st.session_state[page_key] >= total_pages:
        st.session_state[page_key] = 0

    # Page info and navigation
    start_chunk = st.session_state[page_key] * chunks_per_page + 1
    end_chunk = min((st.session_state[page_key] + 1) * chunks_per_page, len(chunks))
    st.caption(f"Mostrando chunks {start_chunk}-{end_chunk} de {len(chunks)}")

    if total_pages > 1:
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
        with nav_col1:
            if st.button(
                "⬅️ Anterior",
                disabled=st.session_state[page_key] == 0,
                width="stretch",
                key="prev_chunk_page",
            ):
                st.session_state[page_key] -= 1
                st.rerun()
        with nav_col2:
            st.markdown(
                f"<p style='text-align: center; padding-top: 8px; font-weight: bold;'>"
                f"Página {st.session_state[page_key] + 1} de {total_pages}</p>",
                unsafe_allow_html=True,
            )
        with nav_col3:
            if st.button(
                "Siguiente ➡️",
                disabled=st.session_state[page_key] >= total_pages - 1,
                width="stretch",
                key="next_chunk_page",
            ):
                st.session_state[page_key] += 1
                st.rerun()

    # Display current page of chunks
    start_idx = st.session_state[page_key] * chunks_per_page
    end_idx = min(start_idx + chunks_per_page, len(chunks))

    for i, chunk in enumerate(chunks[start_idx:end_idx], start=start_idx + 1):
        with st.expander(f"📝 Chunk {i} de {len(chunks)}", expanded=False):
            # Chunk ID
            st.caption(f"ID: `{chunk.chunk_id[:60]}...`")

            # Chunk content in scrollable container
            with st.container(height=250, border=True):
                escaped_text = html.escape(chunk.text)
                st.markdown(
                    f'<div style="font-size: 0.9em; padding: 10px; '
                    f'min-height: 100%; box-sizing: border-box; white-space: pre-wrap;">'
                    f"<style>a {{ pointer-events: none; text-decoration: none; color: inherit; }}</style>"
                    f"{escaped_text}</div>",
                    unsafe_allow_html=True,
                )

            # Metadata section
            if chunk.metadata:
                with st.popover("📊 Ver Metadata"):
                    _render_metadata_table(chunk.metadata)

            # Embedding section
            if chunk.embedding is not None:
                with st.popover("🧠 Ver Embedding"):
                    _render_embedding_info(chunk.embedding)


def _render_clear_database_section() -> None:
    """Render the clear database section with confirmation dialog."""
    st.subheader("🗑️ Gestión de Base de Datos")

    @st.dialog("Confirmar limpieza de base de datos")
    def confirm_clear_database():
        st.warning(
            "⚠️ **Esta acción eliminará TODOS los documentos indexados en ChromaDB.**"
        )
        st.write("")
        st.write("Esta operación es irreversible y borrará permanentemente:")
        st.markdown("""
        - Todos los embeddings generados
        - Todos los chunks de documentos
        - Toda la metadata asociada
        """)
        st.write("")
        st.write("**¿Estás seguro de que deseas continuar?**")

        st.divider()

        confirm_col, cancel_col = st.columns(2)
        with confirm_col:
            confirm_clicked = st.button(
                "✅ Sí, limpiar todo", type="primary", width="stretch"
            )
        with cancel_col:
            cancel_clicked = st.button("❌ Cancelar", width="stretch")

        if confirm_clicked:
            with st.spinner("Limpiando base de datos..."):
                result = clear_database()
                invalidate_client()

            if result.get("success"):
                st.success(f"✅ {result['message']}")
            else:
                st.error(f"❌ {result.get('message', 'Error desconocido')}")

            time.sleep(1.5)
            st.rerun()

        if cancel_clicked:
            st.rerun()

    st.caption("Elimina todos los documentos y embeddings de la base de datos.")
    if st.button(
        "🗑️ Limpiar Base de Datos",
        help="Eliminar todos los documentos indexados",
        type="secondary",
    ):
        confirm_clear_database()


def _render_metadata_table(metadata: dict) -> None:
    """Render metadata as a clean table with readable field names."""
    # Fields to exclude (internal LlamaIndex fields)
    exclude_fields = {
        "doc_id",
        "document_id",
        "ref_doc_id",
        "_node_content",
        "_node_type",
        "relationships",
        "hash",
        "class_name",
        "metadata_template",
        "metadata_separator",
        "text_template",
        "excluded_embed_metadata_keys",
        "excluded_llm_metadata_keys",
    }

    # Field name translations with icons
    field_labels = {
        "source_url": "📍 Fuente (URL)",
        "original_filename": "📄 Archivo Original",
        "file_path": "📍 Fuente (Archivo)",
        "filename": "📄 Nombre archivo",
        "source_type": "📁 Tipo",
        "stack": "🏷️ Stack",
        "indexed_at": "📅 Indexado",
        "url": "🔗 URL",
    }

    # Hide file_path when original_filename is available (avoids showing temp paths)
    if "original_filename" in metadata:
        exclude_fields.add("file_path")

    # Build rows for display
    rows = []
    for key, value in metadata.items():
        if key not in exclude_fields:
            label = field_labels.get(key, key.replace("_", " ").title())
            rows.append({"Campo": label, "Valor": str(value)})

    if rows:
        # Display as DataFrame table (wider for better readability)
        df = pd.DataFrame(rows)
        st.dataframe(df, hide_index=True, width=700)
    else:
        st.info("No hay metadata disponible para mostrar")


def _render_embedding_info(embedding: list[float]) -> None:
    """Render embedding information with dimension and preview."""
    dimension = len(embedding)
    st.markdown(f"**Dimensión:** `{dimension}`")

    # Preview first 50 values
    preview_count = min(50, dimension)
    preview_values = ", ".join(f"{v:.4f}" for v in embedding[:preview_count])
    st.markdown(f"**Preview (primeros {preview_count} valores):**")
    st.code(f"[{preview_values}, ...]", language=None)
