import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

model_openai = LiteLlm(
    model=os.getenv("MODEL_OPENAI"),
    api_key=os.getenv("OPENAI_API_KEY"),
)

model_gemini = LiteLlm(
    model=os.getenv("MODEL_GEMINI"),
    api_key=os.getenv("GOOGLE_API_KEY"),
)

root_agent = LlmAgent(
    name="multimodel_agent",
    model=model_gemini,
    description="Greeting Agent",
    instruction="""
    Eres un asistente útil que saluda a los usuarios.
    Pregunta el nombre del usuario y salúdalo por su nombre.
    """,
)
