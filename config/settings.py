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


def get_database_type() -> str:
    """Определить тип БД из DATABASE_URL."""
    if DATABASE_URL.startswith("postgresql"):
        return "postgresql"
    elif DATABASE_URL.startswith("sqlite"):
        return "sqlite"
    else:
        raise ValueError(f"Unsupported database URL: {DATABASE_URL}")


DB_TYPE: str = get_database_type()

# PostgreSQL Pool Settings
PG_POOL_SIZE: int = int(os.getenv("PG_POOL_SIZE", "10"))
PG_MAX_OVERFLOW: int = int(os.getenv("PG_MAX_OVERFLOW", "20"))

# Application Configuration
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")

# Admin Configuration
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []

# Message Configuration
MESSAGE_CONTACT_EMAIL = "contact@usn.example.com"
MESSAGE_CONTACT_PHONE = "+7 (XXX) XXX-XX-XX"
