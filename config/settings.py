# All configuration sourced from Pydantic settings (root settings.py)
from settings import settings, BOT_TOKEN, DATABASE_URL, PG_POOL_SIZE, PG_MAX_OVERFLOW, DEBUG, LOGGING_LEVEL, ADMIN_IDS


def get_database_type() -> str:
    if DATABASE_URL.startswith("postgresql"):
        return "postgresql"
    elif DATABASE_URL.startswith("sqlite"):
        return "sqlite"
    else:
        raise ValueError(f"Unsupported database URL: {DATABASE_URL}")


DB_TYPE: str = get_database_type()

MESSAGE_CONTACT_EMAIL: str = "contact@usn.example.com"
MESSAGE_CONTACT_PHONE: str = "+7 (XXX) XXX-XX-XX"
