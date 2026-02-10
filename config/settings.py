import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./bot_database.db")

def get_database_type() -> str:
    if DATABASE_URL.startswith("postgresql"):
        return "postgresql"
    elif DATABASE_URL.startswith("sqlite"):
        return "sqlite"
    else:
        raise ValueError(f"Unsupported database URL: {DATABASE_URL}")

DB_TYPE: str = get_database_type()

PG_POOL_SIZE: int = int(os.getenv("PG_POOL_SIZE", "10"))
PG_MAX_OVERFLOW: int = int(os.getenv("PG_MAX_OVERFLOW", "20"))

DEBUG = os.getenv("DEBUG", "True").lower() == "true"
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")

ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []

MESSAGE_CONTACT_EMAIL = "contact@usn.example.com"
MESSAGE_CONTACT_PHONE = "+7 (XXX) XXX-XX-XX"
