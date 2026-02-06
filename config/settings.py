"""
Конфигурация приложения Telegram бота USN.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./bot_database.db")

# Application Configuration
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")

# Admin Configuration
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []

# Message Configuration
MESSAGE_CONTACT_EMAIL = "contact@usn.example.com"
MESSAGE_CONTACT_PHONE = "+7 (XXX) XXX-XX-XX"
