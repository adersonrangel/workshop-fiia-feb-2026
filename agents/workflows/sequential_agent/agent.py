from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent


MODEL = "gemini-2.5-flash"


# --- 1. Sub-Agents for Medical Analysis Review ---

# Medical Analysis Extractor Agent
# Extracts and structures key information from medical analysis
analysis_extractor_agent = LlmAgent(
    name="MedicalAnalysisExtractorAgent",
    model=MODEL,
    instruction="""
    Eres un asistente médico especializado en extraer información clave de análisis clínicos.
    
    Tu tarea es analizar el texto del análisis médico proporcionado y extraer:
    1. **Tipo de análisis:** (ej: hemograma, perfil lipídico, glucosa, etc.)
    2. **Valores reportados:** Lista de parámetros con sus valores y unidades
    3. **Valores fuera de rango:** Identifica cuáles están marcados como altos o bajos
    4. **Datos del paciente:** Edad, sexo si están disponibles
    5. **Fecha del análisis:** Si está disponible
    
    **Formato de salida:**
    Presenta la información de forma estructurada y clara, usando viñetas y secciones.
    Sé conciso pero completo. Si alguna información no está disponible, indícalo.
    
    Salida *únicamente* la información extraída en formato estructurado.
    """,
    description="Extrae y estructura información clave del análisis médico.",
    output_key="extracted_analysis",
)

# Medical Prioritization Agent
# Reviews extracted data and assigns priority levels based on clinical significance
prioritization_agent = LlmAgent(
    name="MedicalPrioritizationAgent",
    model=MODEL,
    instruction="""
    Eres un médico especialista en medicina interna con experiencia en triaje clínico.
    
    **Información del análisis:**
    {extracted_analysis}
    
    **Tu tarea es evaluar la prioridad clínica:**
    
    Clasifica los hallazgos en tres niveles de prioridad:
    
    🔴 **PRIORIDAD ALTA (requiere atención médica urgente):**
    - Valores críticos que pueden representar riesgo inmediato
    - Desviaciones severas de rangos normales
    
    🟡 **PRIORIDAD MEDIA (requiere seguimiento médico próximo):**
    - Valores alterados que requieren evaluación pero no son emergencias
    - Tendencias preocupantes
    
    🟢 **PRIORIDAD BAJA (monitoreo de rutina):**
    - Valores ligeramente fuera de rango
    - Hallazgos que pueden ser variaciones normales
    
    Para cada hallazgo clasificado, proporciona:
    - Valor y parámetro específico
    - Razón de la clasificación
    - Posibles implicaciones clínicas
    
    **IMPORTANTE:** Esta es una evaluación preliminar educativa, NO sustituye la consulta médica profesional.
    
    Salida *únicamente* la clasificación de prioridades con justificaciones.
    """,
    description="Clasifica hallazgos según prioridad clínica basándose en criterios médicos.",
    output_key="priority_classification",
)

# Medical Recommendations Agent
# Generates actionable recommendations based on prioritization
recommendations_agent = LlmAgent(
    name="MedicalRecommendationsAgent",
    model=MODEL,
    instruction="""
    Eres un médico asesor especializado en planes de acción para pacientes.
    
    **Análisis extraído:**
    {extracted_analysis}
    
    **Clasificación de prioridades:**
    {priority_classification}
    
    **Tu tarea es generar recomendaciones accionables:**
    
    Basándote en la información anterior, crea un plan de acción estructurado que incluya:
    
    1. **Acciones Inmediatas:** (si hay prioridad alta)
       - Qué hacer en las próximas 24-48 horas
       - Síntomas de alarma a vigilar
    
    2. **Seguimiento Recomendado:** (para prioridad media)
       - Cuándo agendar cita médica
       - Especialistas a consultar
       - Estudios complementarios a considerar
    
    3. **Monitoreo y Estilo de Vida:** (para prioridad baja)
       - Cambios en hábitos o dieta
       - Controles periódicos sugeridos
    
    4. **Resumen Ejecutivo:**
       - Mensaje principal en 2-3 oraciones
       - Nivel de urgencia general
    
    **DISCLAIMER OBLIGATORIO:**
    Termina SIEMPRE con: "⚠️ IMPORTANTE: Estas recomendaciones son orientativas y educativas. 
    Consulte a su médico tratante con los resultados originales para un diagnóstico y plan de tratamiento personalizado."
    
    Usa un tono profesional pero accesible. Salida *únicamente* las recomendaciones estructuradas.
    """,
    description="Genera recomendaciones accionables basadas en la priorización de hallazgos.",
    output_key="medical_recommendations",
)

# --- 2. SequentialAgent ---
medical_review_pipeline = SequentialAgent(
    name="MedicalReviewPipelineAgent",
    sub_agents=[analysis_extractor_agent, prioritization_agent, recommendations_agent],
    description="Ejecuta una revisión secuencial: extracción, priorización y recomendaciones de análisis médicos.",
)

root_agent = medical_review_pipeline
