"""
Broadcast system services.

This package contains the core broadcast functionality:
- Notification channels (Telegram, Email, SMS, etc)
- Template rendering with Jinja2
- Recipient filtering with SQLAlchemy
- Broadcast orchestration (Facade pattern)
"""

from .channels import NotificationChannel, DeliveryResult

__all__ = [
    "NotificationChannel",
    "DeliveryResult",
]
