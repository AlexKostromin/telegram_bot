from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)


class BotConfig(BaseModel):
    """Telegram Bot Configuration"""
    bot_token: str = Field(default_factory=lambda: os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE"), min_length=1, description="Telegram bot token")
    debug: bool = Field(default=False, description="Debug mode")
    logging_level: str = Field(default="INFO", description="Logging level")
    admin_ids: List[int] = Field(default_factory=list, description="Admin user IDs")

    class Config:
        validate_default = True

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, v):
        if v is False:
            return False
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() == "true"
        debug_str = os.getenv("DEBUG", "False")
        return debug_str.lower() == "true"

    @field_validator("logging_level", mode="before")
    @classmethod
    def get_logging_level(cls, v):
        if v:
            return v
        return os.getenv("LOGGING_LEVEL", "INFO")

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        if isinstance(v, list):
            return v
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        if admin_ids_str:
            return [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]
        return []


class DatabaseConfig(BaseModel):
    """Database Configuration"""

    class Config:
        validate_default = True

    database_url: str = Field(
        default="postgresql+asyncpg://usn_bot:secure_password@postgres:5432/usn_bot_db",
        description="Database connection URL"
    )
    pool_size: int = Field(default=10, ge=1, le=100, description="Connection pool size")
    max_overflow: int = Field(default=20, ge=0, le=200, description="Max overflow connections")

    @field_validator("database_url", mode="before")
    @classmethod
    def get_database_url(cls, v):
        return v or os.getenv("DATABASE_URL", "postgresql+asyncpg://usn_bot:secure_password@postgres:5432/usn_bot_db")

    @field_validator("pool_size", mode="before")
    @classmethod
    def get_pool_size(cls, v):
        if isinstance(v, int):
            return v
        return int(os.getenv("PG_POOL_SIZE", "10"))

    @field_validator("max_overflow", mode="before")
    @classmethod
    def get_max_overflow(cls, v):
        if isinstance(v, int):
            return v
        return int(os.getenv("PG_MAX_OVERFLOW", "20"))


class SMTPConfig(BaseModel):
    """Email/SMTP Configuration"""

    class Config:
        validate_default = True

    smtp_host: str = Field(default="smtp.mailtrap.io", description="SMTP server host")
    smtp_port: int = Field(default=587, ge=1, le=65535, description="SMTP server port")
    smtp_username: str = Field(default="", description="SMTP username")
    smtp_password: str = Field(default="", description="SMTP password")
    smtp_use_tls: bool = Field(default=True, description="Use TLS for SMTP")
    support_email: Optional[str] = Field(default=None, description="Support email address")
    email_from_name: str = Field(default="USN Competitions", description="Email sender name")
    support_telegram_id: Optional[int] = Field(default=None, ge=1, description="Support Telegram user ID")

    @field_validator("smtp_host", mode="before")
    @classmethod
    def get_smtp_host(cls, v):
        return os.getenv("SMTP_HOST") or v or "smtp.mailtrap.io"

    @field_validator("smtp_port", mode="before")
    @classmethod
    def get_smtp_port(cls, v):
        env_val = os.getenv("SMTP_PORT")
        if env_val:
            return int(env_val)
        if isinstance(v, int):
            return v
        return 587

    @field_validator("smtp_username", mode="before")
    @classmethod
    def get_smtp_username(cls, v):
        return os.getenv("SMTP_USERNAME") or v or ""

    @field_validator("smtp_password", mode="before")
    @classmethod
    def get_smtp_password(cls, v):
        return os.getenv("SMTP_PASSWORD") or v or ""

    @field_validator("smtp_use_tls", mode="before")
    @classmethod
    def parse_smtp_use_tls(cls, v):
        env_val = os.getenv("SMTP_USE_TLS")
        if env_val is not None:
            return env_val.lower() == "true"
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() == "true"
        return bool(v)

    @field_validator("support_email", mode="before")
    @classmethod
    def get_support_email(cls, v):
        return os.getenv("SUPPORT_EMAIL") or v or None

    @field_validator("email_from_name", mode="before")
    @classmethod
    def get_email_from_name(cls, v):
        return os.getenv("EMAIL_FROM_NAME") or v or "USN Competitions"

    @field_validator("support_telegram_id", mode="before")
    @classmethod
    def parse_support_telegram_id(cls, v):
        telegram_id_str = os.getenv("SUPPORT_TELEGRAM_ID")
        if telegram_id_str:
            try:
                return int(telegram_id_str)
            except (ValueError, TypeError):
                pass
        if isinstance(v, int) and v > 0:
            return v
        return None

    def is_configured(self) -> bool:
        """Check if SMTP is fully configured"""
        return bool(
            self.smtp_host
            and self.smtp_username
            and self.smtp_password
            and self.support_email
        )

    def is_support_configured(self) -> bool:
        """Check if support channel is configured"""
        return bool(self.support_email or self.support_telegram_id)

    def get_from_address(self) -> str:
        """Get the 'From' email address"""
        return self.support_email or "noreply@example.com"

    def validate_configuration(self) -> bool:
        """Validate SMTP configuration"""
        if not self.is_configured():
            logger.warning(
                "⚠️  SMTP not fully configured. Email notifications will be disabled. "
                "Set SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, SUPPORT_EMAIL in .env"
            )
            return False
        return True


class Settings(BaseModel):
    """Combined application settings"""
    bot: BotConfig = Field(default_factory=BotConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    smtp: SMTPConfig = Field(default_factory=SMTPConfig)

    class Config:
        validate_default = True

    def __init__(self, **data):
        super().__init__(**data)
        # Validate SMTP on init
        if not self.smtp.validate_configuration():
            logger.warning("SMTP configuration validation failed")


# Global settings instance
settings = Settings()

# Backward compatibility - expose at module level
BOT_TOKEN = settings.bot.bot_token
DATABASE_URL = settings.database.database_url
PG_POOL_SIZE = settings.database.pool_size
PG_MAX_OVERFLOW = settings.database.max_overflow
DEBUG = settings.bot.debug
LOGGING_LEVEL = settings.bot.logging_level
ADMIN_IDS = settings.bot.admin_ids
