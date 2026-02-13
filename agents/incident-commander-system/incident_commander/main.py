"""Custom FastAPI server for Incident Commander.

This is an optional entry point that demonstrates how to extend the ADK
auto-generated FastAPI server with custom endpoints.

Usage:
    uvicorn main:app --reload --port 8000

For basic usage, prefer the built-in commands:
    adk web incident-commander/
    adk run incident-commander/
    adk api_server incident-commander/
"""

import os

from google.adk.cli.fast_api import get_fast_api_app

# Path to the incident-commander agent directory
AGENT_DIR = os.path.dirname(__file__)

# Create FastAPI app with ADK agent auto-discovery
app = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=None,
    allow_origins=["*"],
    web=True,  # Enable Dev UI at /dev-ui/
)


# Custom endpoint example
@app.get("/health")
async def health():
    """Health check endpoint for monitoring."""
    return {
        "status": "ok",
        "service": "incident-commander",
        "agents": ["diagnostic_agent", "logs_agent", "postmortem_agent"],
    }


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Incident Commander",
        "description": "Multi-agent system for production incident investigation",
        "endpoints": {
            "health": "/health",
            "dev_ui": "/dev-ui/",
            "api_docs": "/docs",
        },
    }
