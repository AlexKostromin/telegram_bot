"""
Configuration module for USN Telegram Bot.
Loads configuration from environment variables.
"""
import os
from typing import List
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Telegram Bot Configuration
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Database Configuration
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./bot_database.db")

# Application Configuration
DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
LOGGING_LEVEL: str = os.getenv("LOGGING_LEVEL", "INFO")

# Admin IDs Configuration
ADMIN_IDS_STR: str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: List[int] = [int(id.strip()) for id in ADMIN_IDS_STR.split(",") if id.strip()]
