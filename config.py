"""Configuration management for the AI Inbox Assistant.

Loads configuration from environment variables and provides validated settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-2.5-flash")


def get_gemini_api_key() -> str:
    """Retrieve and validate the Gemini API key from environment variables.

    Returns:
        str: Validated Gemini API key.

    Raises:
        ValueError: If GEMINI_API_KEY is missing or empty.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not api_key.strip():
        raise ValueError(
            "GEMINI_API_KEY is missing or empty. "
            "Please configure GEMINI_API_KEY in your .env file or system environment."
        )
    return api_key.strip()


def __getattr__(name: str):
    """Module-level attribute lookup to enforce validation when accessed.

    Allows importing or accessing GEMINI_API_KEY dynamically while raising
    a descriptive ValueError if the key is missing or empty.
    """
    if name == "GEMINI_API_KEY":
        return get_gemini_api_key()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = ["GEMINI_API_KEY", "MODEL_NAME", "get_gemini_api_key"]
