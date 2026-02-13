"""Diagnostic Agent - Especialista en verificar estado de servicios y métricas."""

from google.adk.agents.llm_agent import LlmAgent

from incident_commander.models import MODEL
from .prompts import DESCRIPTION, INSTRUCTION
from .tools import check_metrics, check_service_status

diagnostic_agent = LlmAgent(
    name="diagnostic_agent",
    model=MODEL,
    tools=[check_service_status, check_metrics],
    description=DESCRIPTION,
    instruction=INSTRUCTION,
)
