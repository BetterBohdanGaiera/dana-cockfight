"""Configuration module for Dana CockFight Telegram Bot.

Loads and validates configuration from environment variables.
Provides centralized access to API keys and model configurations.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file in project root
load_dotenv(Path(__file__).parent.parent / ".env")

# API Keys
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Model configurations
GEMINI_MODEL = "gemini-3-pro-image-preview"  # For image generation
GEMINI_TEXT_MODEL = "gemini-2.0-flash"  # For text generation (trash-talk, dialogue)


def validate_config() -> bool:
    """Validate that all required config values are present.

    Raises:
        ValueError: If any required API key is missing or not set.

    Returns:
        bool: True if all required configuration values are present.
    """
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env file")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in .env file")
    return True
