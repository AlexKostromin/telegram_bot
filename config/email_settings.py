# Backward compatibility - import from Pydantic settings
from settings import settings


class SMTPConfig:
    """Backward compatible SMTP configuration wrapper"""

    @classmethod
    def _get_smtp(cls):
        return settings.smtp

    # Properties that map to Pydantic model
    SMTP_HOST = settings.smtp.smtp_host
    SMTP_PORT = settings.smtp.smtp_port
    SMTP_USERNAME = settings.smtp.smtp_username
    SMTP_PASSWORD = settings.smtp.smtp_password
    SMTP_USE_TLS = settings.smtp.smtp_use_tls
    SUPPORT_EMAIL = settings.smtp.support_email
    EMAIL_FROM_NAME = settings.smtp.email_from_name
    SUPPORT_TELEGRAM_ID = settings.smtp.support_telegram_id

    @classmethod
    def get_from_address(cls) -> str:
        return settings.smtp.get_from_address()

    @classmethod
    def is_configured(cls) -> bool:
        return settings.smtp.is_configured()

    @classmethod
    def is_support_configured(cls) -> bool:
        return settings.smtp.is_support_configured()

    @classmethod
    def validate(cls) -> bool:
        return settings.smtp.validate_configuration()

    @classmethod
    def get_summary(cls) -> str:
        status = "✅ Configured" if cls.is_configured() else "⚠️  Not configured"
        support_status = "✅ Configured" if cls.is_support_configured() else "❌ Not configured"
        return f"SMTP: {status}\nSupport: {support_status}"
