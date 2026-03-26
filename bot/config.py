"""Configuration module for the bot.

Loads environment variables from .env.bot.secret file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_config() -> dict:
    """Load configuration from environment variables.
    
    Returns:
        dict: Configuration dictionary with all required settings.
    """
    # Find the .env.bot.secret file in the bot directory
    bot_dir = Path(__file__).parent
    env_file = bot_dir / ".env.bot.secret"
    
    # Load environment variables from file
    if env_file.exists():
        load_dotenv(env_file)
    
    return {
        "bot_token": os.getenv("BOT_TOKEN", ""),
        "lms_api_url": os.getenv("LMS_API_URL", "http://localhost:42002"),
        "lms_api_key": os.getenv("LMS_API_KEY", ""),
        "llm_api_key": os.getenv("LLM_API_KEY", ""),
        "llm_api_base_url": os.getenv("LLM_API_BASE_URL", "http://localhost:42005/v1"),
        "llm_api_model": os.getenv("LLM_API_MODEL", "coder-model"),
    }
