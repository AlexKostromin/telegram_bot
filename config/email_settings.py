"""
Email configuration for broadcast system and notifications.

Supports multiple SMTP providers:
- Mailtrap (for testing)
- Gmail (requires app password)
- Yandex Mail
- Custom SMTP servers
"""
import os
from typing import Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

class SMTPConfig:
    """SMTP configuration for email sending."""

    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.mailtrap.io")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "True").lower() == "true"

    SUPPORT_EMAIL: Optional[str] = os.getenv("SUPPORT_EMAIL", None)

    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "USN Competitions")

    SUPPORT_TELEGRAM_ID: Optional[int] = (
        int(os.getenv("SUPPORT_TELEGRAM_ID", 0))
        if os.getenv("SUPPORT_TELEGRAM_ID")
        else None
    )

    @classmethod
    def get_from_address(cls) -> str:
        """Get the 'from' address for email notifications.

        Uses SUPPORT_EMAIL if configured, otherwise falls back to default.
        """
        return cls.SUPPORT_EMAIL or "noreply@example.com"

    @classmethod
    def is_configured(cls) -> bool:
        """Check if SMTP is configured with all required settings."""
        return bool(
            cls.SMTP_HOST
            and cls.SMTP_USERNAME
            and cls.SMTP_PASSWORD
            and cls.SUPPORT_EMAIL
        )

    @classmethod
    def is_support_configured(cls) -> bool:
        """Check if support email is configured."""
        return bool(cls.SUPPORT_EMAIL or cls.SUPPORT_TELEGRAM_ID)

    @classmethod
    def validate(cls) -> bool:
        """Validate SMTP configuration."""
        if not cls.is_configured():
            logger.warning(
                "⚠️  SMTP not fully configured. Email notifications will be disabled. "
                "Set SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM_ADDRESS in .env"
            )
            return False

        if cls.SMTP_PORT < 0 or cls.SMTP_PORT > 65535:
            logger.warning(f"❌ Invalid SMTP_PORT: {cls.SMTP_PORT}")
            return False

        return True

    @classmethod
    def get_summary(cls) -> str:
        """Get configuration summary for logging."""
        status = "✅ Configured" if cls.is_configured() else "⚠️  Not configured"
        support_status = "✅ Configured" if cls.is_support_configured() else "❌ Not configured"

        return f"""
Email Configuration Summary:
├─ Status: {status}
├─ SMTP Host: {cls.SMTP_HOST}
├─ SMTP Port: {cls.SMTP_PORT}
├─ Use TLS: {cls.SMTP_USE_TLS}
├─ Primary Email (for sending & support): {cls.SUPPORT_EMAIL or 'Not set'}
├─ Email Display Name: {cls.EMAIL_FROM_NAME}
└─ Support: {support_status}
   ├─ Email: {cls.SUPPORT_EMAIL or 'Not set'}
   └─ Telegram ID: {cls.SUPPORT_TELEGRAM_ID or 'Not set'}
        """

if __name__ != "__main__":
    SMTPConfig.validate()
