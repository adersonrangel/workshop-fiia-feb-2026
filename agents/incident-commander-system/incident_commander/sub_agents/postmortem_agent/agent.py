"""Postmortem Agent - Especialista en generar reportes de postmortem estructurados."""

import os

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from incident_commander.models import MODEL
from .prompts import DESCRIPTION, INSTRUCTION
from .tools import get_runbook

# Get absolute path to reports directory (will be created by MCP server on first write)
REPORTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "reports")
)

# MCP filesystem toolset for write_file
mcp_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                REPORTS_DIR,
            ],
        ),
    ),
    tool_filter=["write_file"],
)

postmortem_agent = LlmAgent(
    name="postmortem_agent",
    model=MODEL,
    tools=[get_runbook, mcp_tools],
    description=DESCRIPTION,
    instruction=INSTRUCTION,
)
