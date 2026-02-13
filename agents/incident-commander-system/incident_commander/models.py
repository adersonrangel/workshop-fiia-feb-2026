"""Model configuration for all agents.

Centralized model setup that reads from environment variables.
All agents import from here to use the same model configuration.
"""

import os

from google.adk.models.lite_llm import LiteLlm

# Read model name from environment, default to gpt-5-nano
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5-nano")

# Create model instance based on provider
# If model starts with "gpt-" or contains "openai", use LiteLlm with OpenAI
# Otherwise use the model name directly (for Gemini, etc.)
if MODEL_NAME.startswith("gpt-") or "openai" in MODEL_NAME.lower():
    MODEL = LiteLlm(
        model=MODEL_NAME,
        api_key=os.getenv("OPENAI_API_KEY"),
    )
else:
    # For Gemini and other providers, use string directly
    MODEL = MODEL_NAME
