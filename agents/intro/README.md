# Ejemplos de Agentes con Google ADK

Este directorio contiene ejemplos prácticos para aprender a trabajar con Google Agent Development Kit (ADK) para construir agentes de IA.

## Requisitos Previos

- Python 3.12+
- `uv` instalado (gestor de paquetes Python moderno)
- Google API Key (Gemini)

## Configuración

### 1. Navegar al directorio de agentes

```bash
cd agents
```

### 2. Sincronizar dependencias con uv

```bash
uv sync
```

Esto instalará automáticamente todas las dependencias definidas en `pyproject.toml`, incluyendo:
- `google-adk` - Framework para desarrollo de agentes
- `litellm` - Interfaz unificada para múltiples LLM providers

### 3. Configurar variables de entorno

Cada agente tiene su propia configuración. Navega al directorio del agente específico y configura su `.env`:

```bash
# Ejemplo para structured_output_agent
cd intro/structured_output_agent
cp .env.example .env
```

Edita `.env` con tu clave de Google:

```env
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=tu_clave_de_google_aqui
```

## Ejecutar Agentes

Para ejecutar cualquiera de los agentes de ejemplo:

```bash
cd agents/intro
adk web
```

Esto abrirá una interfaz web interactiva donde podrás seleccionar y probar los diferentes agentes.

**Para más detalles sobre la ejecución, consulta la [guía oficial de Google ADK](https://google.github.io/adk-docs/get-started/python/#run-your-agent).**

## Ejemplos

### 01 - Basic Agent

Agente básico que saluda al usuario y mantiene una conversación simple.

### 02 - Tool Agent

Agente que puede usar herramientas externas (como `google_search` o funciones personalizadas) para extender sus capacidades.

### 03 - Structured Output Agent

Agente que retorna respuestas en formatos estructurados validados usando Pydantic. Ejemplo de analizador de issues técnicos que extrae información estructurada (prioridad, tipo, áreas afectadas, complejidad).

### 04 - Multimodel Agent

Agente que demuestra cómo usar múltiples modelos LLM (OpenAI y Gemini) configurados a través de LiteLLM.

## Estructura del Proyecto

```
intro/
├── README.md                    # Este archivo
├── basic_agent/
│   ├── __init__.py
│   └── agent.py                 # Agente de saludo simple
├── tool_agent/
│   ├── __init__.py
│   └── agent.py                 # Agente con herramientas
├── structured_output_agent/
│   ├── .env.example             
│   ├── __init__.py
│   ├── agent.py                 # Agente con Pydantic schema
└── multimodel_agent/
    ├── .env.example             
    ├── __init__.py
    └── agent.py                 # Agente con múltiples modelos LLM
```

## Recursos Adicionales

- [Google ADK Documentation](https://google.github.io/adk/)
