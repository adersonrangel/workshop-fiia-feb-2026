import datetime

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import google_search


def get_current_time() -> dict:
    """
    Get the current time in the format YYYY-MM-DD HH:MM:SS
    """
    return {
        "current_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


root_agent = LlmAgent(
    name="tool_agent",
    model="gemini-2.5-flash",
    description="Tool Agent",
    instruction="""
    Eres un asistente útil que puede usar las siguientes herramientas:
    - get_current_time
    """,
    tools=[google_search],
    # tools=[get_current_time],
)
