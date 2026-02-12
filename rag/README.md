# RAG: Retrieval Augmented Generation

Introducción práctica al patrón RAG (Retrieval-Augmented Generation) para construir aplicaciones que aumentan las capacidades de los LLMs con conocimiento externo y actualizado mediante búsqueda semántica en bases de datos vectoriales.

## Requisitos Previos

- Python 3.12+
- `uv` instalado (gestor de paquetes Python moderno)
- OpenAI API Key

## Configuración

### 1. Navegar al proyecto

```bash
cd rag/tech-docs-explorer
```

### 2. Sincronizar dependencias con uv

```bash
uv sync
```

Esto instalará automáticamente todas las dependencias definidas en `pyproject.toml`, incluyendo:
- `llama-index` - Framework RAG
- `chromadb` - Base de datos vectorial
- `openai` - Cliente OpenAI
- `streamlit` - Interfaz web interactiva

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con tu clave de OpenAI:

```env
OPENAI_API_KEY=sk-tu-api-key-aqui
```

## Ejecutar la Aplicación

Para ejecutar la interfaz web de Tech Docs Explorer:

```bash
cd rag/tech-docs-explorer
uv run streamlit run main.py
```

Esto abrirá una interfaz web interactiva en `http://localhost:8501`.

**Para más detalles, consulta el [README del proyecto](./tech-docs-explorer/README.md).**

## Proyecto

### Tech Docs Explorer - Explorador de Documentación Técnica

**Descripción:** Aplicación RAG completa para explorar y consultar documentación técnica mediante chat conversacional potenciado por búsqueda semántica.

**Características principales:**
- 📥 Indexación multi-fuente (URLs y PDFs)
- 💬 Chat RAG interactivo con parámetros configurables
- 🔮 HyDE (Hypothetical Document Embeddings)
- 📊 LLM Reranking de resultados
- 💰 Tracking de costos en tiempo real (tokens y USD)
- 📈 Métricas de rendimiento y evaluación con RAGAS
- 📂 ChromaDB Explorer para navegación de embeddings

**Arquitectura RAG:**
```
Query → [HyDE Transform] → Embedding → ChromaDB Search
                                            ↓
                                   Retrieved Chunks
                                            ↓
                                    [LLM Reranking]
                                            ↓
                              LLM → Response + Citations
```

📖 **[Ver documentación completa](./tech-docs-explorer/README.md)**

---

## Estructura del Proyecto

```
rag/
├── README.md                    # Este archivo
└── tech-docs-explorer/
    ├── .env.example
    ├── pyproject.toml          # Dependencias del proyecto
    ├── main.py                 # Aplicación Streamlit principal
    ├── config/
    │   ├── config.yaml         # Configuración de la aplicación
    │   └── settings.py         # Gestión de configuración
    ├── core/
    │   ├── indexing/           # Módulos de indexación
    │   ├── loaders/            # Cargadores de documentos
    │   ├── retrieval/          # Estrategias de recuperación
    │   └── storage/            # Gestión de ChromaDB
    ├── llm/                    # Providers LLM
    ├── ui/                     # Componentes Streamlit
    └── data/                   # Almacenamiento de documentos
```

## Recursos Adicionales

- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
