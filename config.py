# Backward compatibility - import from new Pydantic settings
from settings import (
    settings,
    BOT_TOKEN,
    DATABASE_URL,
    PG_POOL_SIZE,
    PG_MAX_OVERFLOW,
    DEBUG,
    LOGGING_LEVEL,
    ADMIN_IDS,
)

__all__ = [
    "settings",
    "BOT_TOKEN",
    "DATABASE_URL",
    "PG_POOL_SIZE",
    "PG_MAX_OVERFLOW",
    "DEBUG",
    "LOGGING_LEVEL",
    "ADMIN_IDS",
]
