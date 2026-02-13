from google.adk.agents import Agent, SequentialAgent, LoopAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool, google_search


MODEL = "gemini-2.5-flash"


# --- Exit Loop Function ---
def exit_loop():
    """
    Call this function ONLY when the evaluation is 'LEARNING_OPTIMIZED',
    indicating the study plan meets all pedagogical criteria and no further refinement is needed.
    """
    return {
        "status": "optimized",
        "message": "Plan de estudio optimizado pedagógicamente. Loop finalizado.",
    }


# --- 1. Initial Study Plan Generator Agent ---
initial_study_plan_generator = Agent(
    name="InitialStudyPlanGenerator",
    model=MODEL,
    tools=[google_search],
    instruction="""
    Eres un diseñador instruccional experto especializado en crear planes de estudio personalizados.
    
    Basándote en la solicitud del usuario, crea un plan de estudio inicial estructurado.
    
    El usuario proporcionará:
    - Tema a aprender
    - Nivel actual de conocimiento
    - Tiempo disponible (horas/semana)
    - Duración deseada del plan
    - Objetivo final específico
    
    **Tu tarea:**
    1. Usa Google Search para investigar:
       - Recursos educativos actualizados sobre el tema
       - Secuencia típica de aprendizaje para ese tema
       - Pre-requisitos necesarios
       - Proyectos prácticos recomendados
    
    2. Genera un plan de estudio con la siguiente estructura:
    
    ## Plan de Estudio: [Tema]
    
    ### Información del Estudiante
    - Nivel actual: [nivel]
    - Tiempo disponible: [X horas/semana]
    - Duración: [X semanas/meses]
    - Objetivo: [objetivo específico]
    
    ### Pre-requisitos Identificados
    - [Lista de conocimientos necesarios antes de empezar]
    
    ### Fases del Plan
    
    #### Fase 1: [Nombre] (Semanas 1-X)
    **Objetivos:**
    - [Objetivo específico 1]
    - [Objetivo específico 2]
    
    **Contenidos:**
    - [Tema 1]: [horas estimadas]
    - [Tema 2]: [horas estimadas]
    
    **Recursos:**
    - [Recurso 1 con link/referencia]
    - [Recurso 2 con link/referencia]
    
    **Práctica:**
    - [Ejercicio/proyecto específico]
    
    **Evaluación:**
    - [Forma de medir progreso]
    
    [Repetir estructura para cada fase: típicamente 3-5 fases]
    
    ### Proyecto Integrador Final
    [Descripción de proyecto que integra todo lo aprendido]
    
    ### Recursos Adicionales
    - [Comunidades, foros, libros complementarios]
    
    **IMPORTANTE:** 
    - Sé específico con nombres de recursos (cursos, libros, tutoriales)
    - Calcula horas realistas basándose en el tiempo disponible del usuario
    - Menciona las fuentes consultadas en Google Search
    
    Salida *únicamente* el plan estructurado.
    """,
    description="Genera el plan de estudio inicial usando investigación en Google.",
    output_key="current_plan",
)

# --- 2. Pedagogical Evaluator Agent (dentro del Loop) ---
pedagogical_evaluator_agent = Agent(
    name="PedagogicalEvaluatorAgent",
    model=MODEL,
    instruction="""
    Eres un evaluador pedagógico experto que analiza planes de estudio según mejores prácticas de diseño instruccional.
    
    **Plan de estudio a evaluar:**
    {current_plan}
    
    **Tu tarea es evaluar el plan según estos criterios:**
    
    ✅ **Pre-requisitos:** ¿Están claramente identificados? ¿Son realistas para el nivel del estudiante?
    
    ✅ **Secuenciación:** ¿La progresión es lógica? ¿Hay saltos de complejidad muy abruptos?
    
    ✅ **Carga cognitiva:** ¿El volumen de contenido por fase es manejable? ¿Respeta el tiempo disponible del estudiante?
    
    ✅ **Balance teoría/práctica:** ¿Hay suficientes ejercicios prácticos? ¿Están integrados adecuadamente?
    
    ✅ **Recursos:** ¿Son específicos y accesibles? ¿Están actualizados? ¿Incluyen diversidad de formatos?
    
    ✅ **Evaluación:** ¿Hay hitos claros para medir progreso? ¿Incluye evaluación formativa?
    
    ✅ **Viabilidad temporal:** ¿Las horas estimadas son realistas? ¿El plan es completable en el tiempo indicado?
    
    ✅ **Proyecto integrador:** ¿El proyecto final integra los conceptos clave? ¿Es apropiado al nivel?
    
    **Instrucciones de salida:**
    
    - Si el plan cumple TODOS los criterios anteriores de forma sólida, responde EXACTAMENTE: "LEARNING_OPTIMIZED"
    
    - Si hay deficiencias, proporciona feedback específico y accionable para cada área problemática.
      Usa este formato:
      
      ❌ [Criterio]: [Problema específico]
      💡 Sugerencia: [Cómo mejorar]
      
      Limita tu feedback a los 3-4 problemas más críticos.
    
    Salida *únicamente* "LEARNING_OPTIMIZED" o el feedback estructurado.
    """,
    description="Evalúa el plan de estudio según criterios pedagógicos rigurosos.",
    output_key="evaluation",
)

# --- 3. Study Plan Refiner Agent (dentro del Loop) ---
study_plan_refiner_agent = Agent(
    name="StudyPlanRefinerAgent",
    model=MODEL,
    tools=[FunctionTool(exit_loop)],
    instruction="""
    Eres un refinador de planes de estudio especializado en implementar feedback pedagógico.
    
    **Plan actual:**
    {current_plan}
    
    **Evaluación recibida:**
    {evaluation}
    
    **Tu tarea:**
    
    1. Analiza la evaluación cuidadosamente.
    
    2. **SI la evaluación es EXACTAMENTE "LEARNING_OPTIMIZED":**
       - Llama la función `exit_loop` inmediatamente
       - NO generes ningún otro output
    
    3. **SI la evaluación contiene feedback:**
       - Reescribe el plan de estudio incorporando TODAS las sugerencias del evaluador
       - Mantén la estructura original pero mejora el contenido según el feedback
       - Asegúrate de abordar cada problema identificado
       - Preserva los elementos que ya estaban bien
    
    **IMPORTANTE:**
    - No agregues explicaciones sobre qué cambiaste
    - Salida *únicamente* el plan revisado completo
    - Mantén el mismo formato estructurado que el plan original
    """,
    description="Refina el plan de estudio basándose en feedback pedagógico o finaliza el loop.",
    output_key="current_plan",
)

# --- 4. Create the Loop Agent ---
study_plan_refinement_loop = LoopAgent(
    name="StudyPlanRefinementLoop",
    sub_agents=[pedagogical_evaluator_agent, study_plan_refiner_agent],
    max_iterations=2,
)

# --- 5. Create the Root Sequential Agent ---
root_agent = SequentialAgent(
    name="StudyPlanGeneratorPipeline",
    sub_agents=[initial_study_plan_generator, study_plan_refinement_loop],
)
