"""Incident Commander - Root agent entry point.

Orchestrator agent that coordinates 3 specialized worker agents to investigate
production incidents.
"""

from google.adk.agents.llm_agent import LlmAgent

from .models import MODEL
from .prompts import DESCRIPTION, INSTRUCTION
from .sub_agents.diagnostic_agent.agent import diagnostic_agent
from .sub_agents.logs_agent.agent import logs_agent
from .sub_agents.postmortem_agent.agent import postmortem_agent

# Define incident_commander directly as root_agent
root_agent = LlmAgent(
    name="incident_commander",
    model=MODEL,
    sub_agents=[diagnostic_agent, logs_agent, postmortem_agent],
    description=DESCRIPTION,
    instruction=INSTRUCTION,
)
