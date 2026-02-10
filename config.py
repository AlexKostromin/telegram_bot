import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./bot_database.db")

def get_database_type() -> str:
    """Определить тип БД из DATABASE_URL."""
    if DATABASE_URL.startswith("postgresql"):
        return "postgresql"
    elif DATABASE_URL.startswith("sqlite"):
        return "sqlite"
    else:
        raise ValueError(f"Unsupported database URL: {DATABASE_URL}")

DB_TYPE: str = get_database_type()

PG_POOL_SIZE: int = int(os.getenv("PG_POOL_SIZE", "10"))
PG_MAX_OVERFLOW: int = int(os.getenv("PG_MAX_OVERFLOW", "20"))

DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
LOGGING_LEVEL: str = os.getenv("LOGGING_LEVEL", "INFO")

ADMIN_IDS_STR: str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: List[int] = [int(id.strip()) for id in ADMIN_IDS_STR.split(",") if id.strip()]

