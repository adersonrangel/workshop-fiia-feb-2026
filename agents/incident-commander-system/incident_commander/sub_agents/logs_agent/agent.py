"""Logs Agent - Especialista en analizar entradas de log y patrones de error."""

from google.adk.agents.llm_agent import LlmAgent

from incident_commander.models import MODEL
from .prompts import DESCRIPTION, INSTRUCTION
from .tools import search_logs

logs_agent = LlmAgent(
    name="logs_agent",
    model=MODEL,
    tools=[search_logs],
    description=DESCRIPTION,
    instruction=INSTRUCTION,
)
