# Ejemplos de Introducción a LLMs

Este directorio contiene ejemplos prácticos para aprender a trabajar con APIs de Large Language Models (LLMs).

## Requisitos Previos

- Python 3.12+
- API keys de los proveedores que desees usar (OpenAI, Anthropic, Google)

## Configuración

### 1. Crear entorno virtual

```bash
python -m venv venv
```

Activar el entorno virtual:

**macOS / Linux:**
```bash
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

> Si tienes problemas de permisos en PowerShell, ejecuta primero:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copia el archivo de ejemplo:

**macOS / Linux:**
```bash
cp .env.example .env
```

**Windows (Command Prompt):**
```cmd
copy .env.example .env
```

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

Edita `.env` con tus claves:

```
OPENAI_API_KEY=tu_clave_de_openai
ANTHROPIC_API_KEY=tu_clave_de_anthropic
GEMINI_API_KEY=tu_clave_de_gemini
```

## Ejemplos

### 01 - Primera Llamada a un LLM

Ejemplos básicos de cómo hacer tu primera llamada a diferentes proveedores de LLMs.

```bash
# Usando OpenAI SDK
python 01-first-call/openai_first_call.py

# Usando OpenAI REST API directamente
python 01-first-call/openai_first_call_rest_api.py

# Usando Anthropic (Claude)
python 01-first-call/anthropic_first_call.py

# Usando Google Gemini
python 01-first-call/gemini_first_call.py
```

### 02 - Tokens y Costos

Aprende cómo funcionan los tokens y cómo calcular el costo de las llamadas.

```bash
python 02-tokens.py
```

Este script muestra:
- Conteo de tokens de entrada y salida
- Cálculo de costos basado en precios por millón de tokens

### 03 - Temperatura

Explora cómo el parámetro de temperatura afecta las respuestas del modelo.

```bash
# Comparar diferentes valores de temperatura (0.0, 0.5, 1.0, 1.5)
python 03-temperature/temperature.py

# Ejemplo con modelos de razonamiento
python 03-temperature/reasoning.py
```

- **Temperatura baja (0.0-0.5)**: Respuestas más deterministas y consistentes
- **Temperatura alta (1.0-1.5)**: Respuestas más creativas y variadas

### 04 - Streaming

Compara el comportamiento con y sin streaming de respuestas.

```bash
# Sin streaming - espera la respuesta completa
python 04-streaming/without_streaming.py

# Con streaming - recibe tokens en tiempo real
python 04-streaming/with_streaming.py
```

El streaming permite mostrar respuestas progresivamente al usuario, mejorando la experiencia en aplicaciones interactivas.

### 05 - Salida Estructurada

Aprende a obtener respuestas en formatos estructurados usando Pydantic.

```bash
# Sin structured output (solo prompting)
python 05-structured-output/without_structured_output.py

# Con structured output (usando Pydantic)
python 05-structured-output/with_structured_output.py
```

El archivo `schema.py` define el esquema de datos esperado usando Pydantic, garantizando que la respuesta del modelo siempre tenga el formato correcto.

## Estructura del Proyecto

```
examples/
├── .env.example          # Plantilla de variables de entorno
├── requirements.txt      # Dependencias de Python
├── 01-first-call/        # Primeras llamadas a APIs
├── 02-tokens.py          # Tokens y costos
├── 03-temperature/       # Efectos de temperatura
├── 04-streaming/         # Streaming de respuestas
└── 05-structured-output/ # Salidas estructuradas con Pydantic
```

## Notas

- Asegúrate de tener saldo suficiente en tu cuenta del proveedor antes de ejecutar los ejemplos
- Los costos mostrados son aproximados y pueden variar según los precios actuales