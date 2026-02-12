"""Indexing Tab - UI for adding and processing URLs and PDFs."""

import os
import shutil
import tempfile
import time
from pathlib import Path

import streamlit as st

from core.indexing import index_documents
from core.loaders import PDFLoader, WebLoader
from ui.streamlit_helpers import (
    display_index_stats,
    save_uploaded_file,
    validate_url,
)


def render_indexing_tab() -> None:
    """Renders the indexing tab with all its functionalities."""

    # Section 1: Add URL
    with st.expander("🌐 Agregar URL", expanded=True):
        with st.form("add_url_form", clear_on_submit=True):
            url = st.text_input(
                "URL",
                placeholder="https://docs.python.org/3/tutorial/index.html",
                help="URL de la documentación técnica a indexar",
            )
            stack = st.text_input(
                "Stack *",
                placeholder="python, django, fastapi...",
                help="Stack tecnológico (requerido)",
            )
            submitted = st.form_submit_button("➕ Agregar URL", type="primary")

            if submitted:
                # Validation
                if not url.strip():
                    st.error("❌ La URL no puede estar vacía")
                elif not stack.strip():
                    st.error("❌ El campo Stack es requerido")
                elif not validate_url(url):
                    st.error("❌ URL inválida. Debe comenzar con http:// o https://")
                else:
                    # Add to resources
                    new_resource = {
                        "type": "url",
                        "source": url.strip(),
                        "stack": stack.strip(),
                    }
                    st.session_state.resources.append(new_resource)
                    st.success(f"✅ URL agregada: {url}")
                    st.rerun()

    # Section 2: Upload PDFs
    with st.expander("📄 Subir PDFs", expanded=True):
        uploaded_files = st.file_uploader(
            "Archivos PDF",
            type=["pdf"],
            accept_multiple_files=True,
            help="Selecciona uno o más archivos PDF",
        )

        if uploaded_files:
            st.write(f"**{len(uploaded_files)} archivo(s) seleccionado(s)**")

            # Form to assign stacks to each PDF
            with st.form("add_pdf_form"):
                pdf_stacks = {}
                for uploaded_file in uploaded_files:
                    pdf_stacks[uploaded_file.name] = st.text_input(
                        f"Stack para {uploaded_file.name} *",
                        key=f"stack_{uploaded_file.name}",
                        placeholder="python, react, nodejs...",
                    )

                add_pdfs = st.form_submit_button("➕ Agregar PDFs", type="primary")

                if add_pdfs:
                    # Validate that all have stack assigned
                    missing_stacks = [
                        name for name, stack in pdf_stacks.items() if not stack.strip()
                    ]

                    if missing_stacks:
                        st.error(
                            f"❌ Los siguientes PDFs requieren stack: {', '.join(missing_stacks)}"
                        )
                    else:
                        # Save PDFs temporarily and add to resources
                        # Note: Temp files will be cleaned up after indexing
                        for uploaded_file in uploaded_files:
                            with save_uploaded_file(uploaded_file) as temp_path:
                                # Copy to a persistent temp location that we control
                                fd, persistent_path = tempfile.mkstemp(
                                    suffix=Path(uploaded_file.name).suffix
                                )
                                try:
                                    os.close(fd)  # Close the file descriptor
                                    shutil.copy2(temp_path, persistent_path)
                                    new_resource = {
                                        "type": "pdf",
                                        "source": persistent_path,
                                        "stack": pdf_stacks[uploaded_file.name].strip(),
                                        "filename": uploaded_file.name,
                                    }
                                    st.session_state.resources.append(new_resource)
                                except Exception:
                                    # Clean up temp file if something goes wrong
                                    Path(persistent_path).unlink(missing_ok=True)
                                    raise

                        st.success(f"✅ {len(uploaded_files)} PDF(s) agregado(s)")
                        st.rerun()

    st.divider()

    # Section 3: Resources table
    if st.session_state.resources:
        st.subheader("📋 Recursos para Indexar")

        # Display table in container with border
        with st.container(border=True):
            # Convert to DataFrame for display with delete buttons
            for idx, resource in enumerate(st.session_state.resources):
                col1, col2, col3, col4 = st.columns([1, 4, 2, 1])

                with col1:
                    resource_type = "🌐 URL" if resource["type"] == "url" else "📄 PDF"
                    st.write(resource_type)

                with col2:
                    source = (
                        resource["source"]
                        if resource["type"] == "url"
                        else resource.get("filename", resource["source"])
                    )
                    st.write(source)

                with col3:
                    st.write(resource["stack"])

                with col4:
                    if st.button("🗑️", key=f"delete_{idx}", help="Eliminar recurso"):
                        # Clean up temp file if it's a PDF
                        if st.session_state.resources[idx]["type"] == "pdf":
                            try:
                                Path(st.session_state.resources[idx]["source"]).unlink(
                                    missing_ok=True
                                )
                            except Exception:
                                pass  # Best effort cleanup

                        st.session_state.resources.pop(idx)
                        st.rerun()

                # Add visual separator between rows
                if idx < len(st.session_state.resources) - 1:
                    st.divider()

        st.divider()

        # Section 4: Indexing action (only when resources exist)
        if st.button(
            "🚀 Indexar",
            type="primary",
            help="Indexar todos los recursos agregados",
            width="stretch",
        ):
            st.session_state.start_indexing = True
            st.rerun()

        # Section 5: Indexing process
        if st.session_state.get("start_indexing", False):
            _perform_indexing()

    else:
        st.info("👆 Comienza agregando URLs o PDFs usando los formularios de arriba")


def _perform_indexing() -> None:
    """Executes the indexing process with progress indicators."""
    all_documents = []
    total_resources = len(st.session_state.resources)

    with st.status("🔄 Indexando documentos...", expanded=True) as status_widget:
        # Step 1: Load documents
        st.write("📥 **Paso 1/4:** Cargando documentos...")
        start_time = time.time()

        for idx, resource in enumerate(st.session_state.resources, 1):
            try:
                if resource["type"] == "url":
                    st.write(
                        f"   → Cargando URL {idx}/{total_resources}: {resource['source'][:50]}..."
                    )
                    loader = WebLoader()
                    documents = loader.load(resource["source"])
                else:  # PDF
                    st.write(
                        f"   → Cargando PDF {idx}/{total_resources}: {resource.get('filename', 'archivo')}..."
                    )
                    loader = PDFLoader()
                    documents = loader.load(resource["source"])

                # Add stack to metadata of each document
                for doc in documents:
                    doc.metadata["stack"] = resource["stack"]
                    doc.metadata["source_type"] = resource["type"]
                    # Override filename for PDFs with original name (preserves user's filename)
                    if resource["type"] == "pdf" and "filename" in resource:
                        doc.metadata["filename"] = resource["filename"]
                        doc.metadata["original_filename"] = resource["filename"]

                all_documents.extend(documents)

            except Exception as e:
                st.warning(f"   ⚠️ Error cargando {resource['source']}: {str(e)}")

        load_time = time.time() - start_time
        st.write(f"✅ {len(all_documents)} documento(s) cargado(s) en {load_time:.2f}s")

        if not all_documents:
            st.error("❌ No se pudo cargar ningún documento")
            status_widget.update(label="❌ Indexación fallida", state="error")
            st.session_state.start_indexing = False
            return

        # Step 2: Split into chunks
        st.write("✂️ **Paso 2/4:** Dividiendo en chunks...")
        # (The index_documents function does this internally)
        st.write("   → Aplicando SentenceSplitter...")

        # Step 3: Generate embeddings and index
        st.write("🧠 **Paso 3/4:** Generando embeddings e indexando...")
        index_start_time = time.time()

        try:
            # Collect all unique stacks from resources as comma-separated string
            stacks = list(
                set(resource["stack"] for resource in st.session_state.resources)
            )
            metadata = {
                "stacks": ", ".join(stacks),  # Convert to string for ChromaDB
                "indexed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            index_stats = index_documents(all_documents, metadata)
            index_time = time.time() - index_start_time
            st.write(f"✅ Indexación completada en {index_time:.2f}s")

            # Step 4: Save results
            st.write("💾 **Paso 4/4:** Guardando en ChromaDB...")
            st.write("✅ Datos persistidos correctamente")

            # Update final status
            total_time = time.time() - start_time
            status_widget.update(
                label=f"✅ Indexación completada en {total_time:.2f}s",
                state="complete",
            )

            # Display statistics
            st.success("🎉 **Indexación exitosa!**")
            display_index_stats(index_stats)

            # Clean up temporary PDF files
            _cleanup_temp_files()

            # Clear resources after successful indexing
            st.session_state.resources = []
            st.session_state.start_indexing = False

        except Exception as e:
            st.error(f"❌ Error durante la indexación: {str(e)}")
            status_widget.update(label="❌ Indexación fallida", state="error")
            st.session_state.start_indexing = False


def _cleanup_temp_files() -> None:
    """Clean up temporary PDF files stored in resources."""
    for resource in st.session_state.resources:
        if resource["type"] == "pdf":
            try:
                Path(resource["source"]).unlink(missing_ok=True)
            except Exception as e:
                # Best effort cleanup - don't fail if cleanup fails
                print(f"Warning: Could not delete temp file {resource['source']}: {e}")
