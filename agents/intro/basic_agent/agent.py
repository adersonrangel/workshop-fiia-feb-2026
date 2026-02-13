from google.adk.agents.llm_agent import LlmAgent

root_agent = LlmAgent(
    name="basic_agent",
    model="gemini-2.5-flash",
    description="Greeting Agent",
    instruction="""
    Eres un asistente útil que saluda a los usuarios.
    Pregunta el nombre del usuario y salúdalo por su nombre.
    """,
)
