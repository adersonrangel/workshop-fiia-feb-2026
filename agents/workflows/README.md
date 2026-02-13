# Patrones de Workflows con Google ADK

Este directorio contiene ejemplos avanzados de patrones de orquestación multi-agente usando Google Agent Development Kit (ADK). Cada workflow demuestra un patrón arquitectónico diferente para coordinar múltiples agentes especializados.

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

Cada workflow tiene su propia configuración. Navega al directorio del workflow específico y configura su `.env`:

```bash
# Ejemplo para sequential_agent
cd workflows/sequential_agent
cp .env.example .env
```

Edita `.env` con tu clave de Google:

```env
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=tu_clave_de_google_aqui
```

## Ejecutar Workflows

Para ejecutar cualquiera de los workflows:

```bash
cd agents/workflows/
adk web
```

Esto abrirá una interfaz web interactiva donde podrás probar el workflow seleccionado.

**Para más detalles sobre la ejecución, consulta la [guía oficial de Google ADK](https://google.github.io/adk-docs/get-started/python/#run-your-agent).**

## Patrones de Workflow

### 01 - Sequential Agent (Pipeline Lineal)

**Use Case:** Pipeline de Revisión de Análisis Médicos

Sistema que ejecuta agentes en **secuencia lineal**, donde cada agente procesa el output del anterior para generar insights progresivamente más refinados.

**Arquitectura:**
```
Extractor → Prioritization → Recommendations → Output
```

📖 **[Ver documentación completa](./sequential_agent/README.md)**

---

### 02 - Parallel Agent (Ejecución Simultánea)

**Use Case:** Sistema de Planificación de Presupuestos de Viaje

Sistema que ejecuta múltiples agentes **simultáneamente** para investigar aspectos independientes, luego sintetiza resultados en un output unificado.

**Arquitectura:**
```
                    ┌─ Flight Research ─┐
                    ├─ Accommodation ───┤
Input → Parallel ───┼─ Daily Expenses ──┼→ Synthesis → Output
                    └─ Special Costs ───┘
```

📖 **[Ver documentación completa](./parallel_agent/README.md)**

---

### 03 - Evaluator-Optimizer Agent (Loop Iterativo)

**Use Case:** Generador de Planes de Estudio Personalizados

Sistema con **ciclo de retroalimentación** (loop) donde agentes evaluadores y refinadores iteran hasta alcanzar criterios de calidad o límite de iteraciones.

**Arquitectura:**
```
                    ┌──────────────────┐
                    │                  │
Generator → Loop ───┤ Evaluator        │
             ↑      │    ↓             │
             └──────┤ Refiner ─→ exit? │→ Output
                    └──────────────────┘
                    (max_iterations=2)
```

📖 **[Ver documentación completa](./evaluator_optimizer_agent/README.md)**

---

## Estructura del Proyecto

```
workflows/
├── README.md                           # Este archivo
├── sequential_agent/
│   ├── .env.example
│   ├── agent.py                        # Pipeline médico (3 agentes)
│   └── README.md                       # Documentación completa
├── parallel_agent/
│   ├── .env.example
│   ├── agent.py                        # Budget planner (5 agentes)
│   └── README.md                       # Documentación completa
└── evaluator_optimizer_agent/
    ├── .env.example
    ├── agent.py                        # Study plan generator (3 agentes + loop)
    └── README.md                       # Documentación completa
```

## Recursos Adicionales

- [Google ADK Documentation](https://google.github.io/adk/)
- [Building Effective Agents - Anthropic](https://www.anthropic.com/engineering/building-effective-agents)
