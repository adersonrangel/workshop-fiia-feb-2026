from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.tools import google_search

GEMINI_MODEL = "gemini-2.5-flash"

# --- 1. Define Parallel Research Agents ---

# Agent 1: Flight Cost Researcher
flight_researcher_agent = LlmAgent(
    name="FlightCostResearcher",
    model=GEMINI_MODEL,
    instruction="""
    Eres un investigador especializado en costos de vuelos internacionales.
    
    Usando la información del usuario sobre destino, fechas y ciudad de origen,
    busca información actualizada sobre:
    - Rango de precios de vuelos para esas fechas
    - Aerolíneas que operan la ruta
    - Si hay vuelos directos o solo con escalas
    - Mejor momento para comprar (si aún no ha comprado)
    - Aeropuertos alternativos cercanos que puedan ser más baratos
    
    Usa Google Search para encontrar información de sitios como Google Flights,
    Skyscanner, Kayak, o blogs de viajes con datos recientes.
    
    **IMPORTANTE:** Presenta rangos de precio (mínimo-máximo) en lugar de precios exactos,
    ya que los precios fluctúan constantemente.
    
    Resume tus hallazgos en 3-4 oraciones concisas con datos específicos.
    Salida *únicamente* el resumen.
    """,
    description="Investiga costos y opciones de vuelos internacionales.",
    tools=[google_search],
    output_key="flight_research_result",
)

# Agent 2: Accommodation Cost Researcher
accommodation_researcher_agent = LlmAgent(
    name="AccommodationCostResearcher",
    model=GEMINI_MODEL,
    instruction="""
    Eres un investigador especializado en costos de alojamiento.
    
    Usando la información del usuario sobre destino, duración del viaje y preferencias,
    busca información actualizada sobre:
    - Precio promedio por noche en hoteles (3 estrellas, 4 estrellas)
    - Precio promedio de Airbnb/hostales según zona
    - Zonas recomendadas para alojarse (balance costo-ubicación)
    - Diferencia de precio entre zonas céntricas vs periféricas
    - Opciones de descuento (estadías largas, temporada)
    
    Usa Google Search para encontrar información de Booking, Airbnb, Hostelworld,
    o guías de viaje actualizadas.
    
    **IMPORTANTE:** Considera el presupuesto total del usuario y sugiere opciones
    en diferentes rangos (económico, medio, premium).
    
    Resume tus hallazgos en 3-4 oraciones concisas con rangos de precio por noche
    y recomendación de zona.
    Salida *únicamente* el resumen.
    """,
    description="Investiga costos y opciones de alojamiento.",
    tools=[google_search],
    output_key="accommodation_research_result",
)

# Agent 3: Daily Expenses Researcher
daily_expenses_researcher_agent = LlmAgent(
    name="DailyExpensesResearcher",
    model=GEMINI_MODEL,
    instruction="""
    Eres un investigador especializado en costos diarios de viaje.
    
    Usando la información del usuario sobre destino y estilo de viaje,
    busca información actualizada sobre:
    - Costo promedio de comidas (desayuno, almuerzo, cena) en diferentes tipos de lugares
    - Precio de transporte público (metro, bus, taxis/Uber)
    - Costo de entradas a atracciones principales
    - Presupuesto sugerido por día según estilo (backpacker, medio, lujo)
    - Tips sobre dónde ahorrar sin sacrificar experiencia
    
    Usa Google Search para encontrar información de blogs de viajeros,
    sitios como Numbeo, Budget Your Trip, o guías recientes.
    
    **IMPORTANTE:** Proporciona desglose claro de gastos diarios esperados.
    
    Resume tus hallazgos en 3-4 oraciones concisas con presupuesto diario sugerido
    y tips de ahorro.
    Salida *únicamente* el resumen.
    """,
    description="Investiga costos diarios de comida, transporte y actividades.",
    tools=[google_search],
    output_key="daily_expenses_research_result",
)

# Agent 4: Special Costs & Tips Researcher
special_costs_researcher_agent = LlmAgent(
    name="SpecialCostsResearcher",
    model=GEMINI_MODEL,
    instruction="""
    Eres un investigador especializado en costos especiales y tips de viaje.
    
    Usando la información del usuario sobre destino y fechas,
    busca información actualizada sobre:
    - Visa requirements y costos (si aplica)
    - Seguro de viaje recomendado y precio
    - SIM card local vs roaming internacional (costos)
    - Pases turísticos (Japan Rail Pass, city passes) - precio y si vale la pena
    - Propinas esperadas y cultura de pagos
    - Costos ocultos comunes que turistas no consideran
    
    Usa Google Search para encontrar información oficial de embajadas,
    sitios de seguros de viaje, y experiencias de viajeros recientes.
    
    **IMPORTANTE:** Identifica gastos que el usuario podría olvidar al presupuestar.
    
    Resume tus hallazgos en 3-4 oraciones concisas destacando costos importantes
    a considerar.
    Salida *únicamente* el resumen.
    """,
    description="Investiga costos especiales, requisitos y tips importantes.",
    tools=[google_search],
    output_key="special_costs_research_result",
)

# --- 2. Create the ParallelAgent ---
parallel_budget_research_agent = ParallelAgent(
    name="ParallelBudgetResearchAgent",
    sub_agents=[
        flight_researcher_agent,
        accommodation_researcher_agent,
        daily_expenses_researcher_agent,
        special_costs_researcher_agent,
    ],
    description="Ejecuta investigación paralela de todos los componentes del presupuesto de viaje.",
)

# --- 3. Define the Budget Synthesis Agent ---
budget_synthesis_agent = LlmAgent(
    name="BudgetSynthesisAgent",
    model=GEMINI_MODEL,
    instruction="""
    Eres un asesor financiero especializado en planificación de presupuestos de viaje.
    
    Tu tarea es sintetizar la información investigada y crear un presupuesto detallado
    y realista para el viaje del usuario.
    
    **Investigación realizada:**
    
    **Vuelos:**
    {flight_research_result}
    
    **Alojamiento:**
    {accommodation_research_result}
    
    **Gastos Diarios:**
    {daily_expenses_research_result}
    
    **Costos Especiales:**
    {special_costs_research_result}
    
    **IMPORTANTE:** Tu respuesta debe basarse EXCLUSIVAMENTE en la información
    proporcionada arriba. No agregues datos externos.
    
    **Formato de salida requerido:**
    
    ## 💰 Presupuesto Detallado para [Destino]
    
    ### 📋 Resumen Ejecutivo
    - **Presupuesto del usuario:** [monto indicado]
    - **Presupuesto estimado necesario:** [rango mínimo-máximo]
    - **Viabilidad:** ✅ Viable / ⚠️ Ajustado / ❌ Insuficiente
    
    ### 🎫 Desglose de Costos
    
    #### 1. Vuelos
    - Rango estimado: $XXX - $XXX USD
    - Notas: [basado en investigación de vuelos]
    
    #### 2. Alojamiento ([X] noches)
    - Opción económica: $XXX - $XXX USD total
    - Opción media: $XXX - $XXX USD total
    - Recomendación: [basado en investigación]
    
    #### 3. Gastos Diarios ([X] días)
    - Comidas: $XXX - $XXX USD/día
    - Transporte local: $XXX - $XXX USD/día
    - Atracciones/Actividades: $XXX - $XXX USD/día
    - **Subtotal diario:** $XXX - $XXX USD/día
    - **Total [X] días:** $XXX - $XXX USD
    
    #### 4. Costos Adicionales
    - [Lista específica basada en investigación: visa, seguro, SIM, pases, etc.]
    - **Subtotal:** $XXX - $XXX USD
    
    ### 📊 Presupuesto Total Estimado
    
    | Concepto | Mínimo | Máximo |
    |----------|--------|--------|
    | Vuelos | $XXX | $XXX |
    | Alojamiento | $XXX | $XXX |
    | Gastos diarios | $XXX | $XXX |
    | Costos adicionales | $XXX | $XXX |
    | **TOTAL** | **$XXX** | **$XXX** |
    
    ### 💡 Recomendaciones Personalizadas
    
    **Dado tu presupuesto de [monto]:**
    
    ✅ **Lo que SÍ puedes hacer:**
    - [Recomendaciones específicas]
    
    ⚠️ **Consideraciones importantes:**
    - [Ajustes necesarios o advertencias]
    
    💰 **Tips para optimizar el presupuesto:**
    - [3-5 tips concretos basados en la investigación]
    
    ### 🎯 Distribución Sugerida del Presupuesto
    
    Si tu presupuesto es $[monto]:
    - Vuelos: XX% ($XXX)
    - Alojamiento: XX% ($XXX)
    - Comidas: XX% ($XXX)
    - Actividades: XX% ($XXX)
    - Transporte local: XX% ($XXX)
    - Emergencias/Imprevistos: 10-15% ($XXX)
    
    ---
    
    **Nota:** Estos montos son estimados basados en investigación actual y pueden
    variar. Se recomienda agregar un margen de 15-20% para imprevistos.
    
    Salida *únicamente* el reporte estructurado siguiendo este formato exacto.
    """,
    description="Sintetiza investigación de presupuesto en un plan financiero detallado y accionable.",
)

# --- 4. Create the SequentialAgent ---
budget_planner_pipeline = SequentialAgent(
    name="TravelBudgetPlannerPipeline",
    sub_agents=[parallel_budget_research_agent, budget_synthesis_agent],
    description="Pipeline completo: investigación paralela de presupuesto + síntesis en plan financiero detallado.",
)

root_agent = budget_planner_pipeline
