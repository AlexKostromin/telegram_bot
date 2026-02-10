"""
Abstract notification channels for broadcast system.

This module defines the base interface for all notification channels (Telegram, Email, SMS, Push, etc).
Follows the Strategy pattern and SOLID principles for easy extensibility.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class DeliveryResult:
    """Result of attempting to deliver a message via a notification channel."""

    success: bool
    status: str
    message_id: Optional[str] = None
    error: Optional[str] = None
    sent_at: Optional[datetime] = None

class NotificationChannel(ABC):
    """
    Abstract base class for notification channels.

    All notification channels (Telegram, Email, SMS, Push) must implement this interface.
    This ensures they're interchangeable and can be used by the BroadcastOrchestrator.

    Example:
        >>> telegram = TelegramChannel(bot)
        >>> email = EmailChannel()
        >>> for channel in [telegram, email]:
        ...     result = await channel.send(recipient, subject, body)
        ...     print(f"{channel.get_channel_name()}: {result.status}")
    """

    @abstractmethod
    async def send(
        self,
        recipient: Dict[str, Any],
        subject: str,
        body: str
    ) -> DeliveryResult:
        """
        Send a message via this channel to a recipient.

        Args:
            recipient: Dictionary with recipient information
                {
                    'telegram_id': 123456789,
                    'email': 'user@example.com',
                    'first_name': 'John',
                    'phone': '+1234567890',
                    ...
                }
            subject: Message subject (used for email, can be ignored for SMS/Telegram)
            body: Message body (plain text or HTML depending on channel)

        Returns:
            DeliveryResult with status of delivery attempt

        Raises:
            Exception: Specific channel exceptions (TelegramError, SMTPError, etc)

        Example:
            >>> result = await telegram.send(
            ...     recipient={'telegram_id': 123, 'first_name': 'John'},
            ...     subject='Test',
            ...     body='Hello!'
            ... )
            >>> if result.success:
            ...     print(f"Sent via Telegram: {result.message_id}")
        """
        pass

    @abstractmethod
    async def validate_recipient(self, recipient: Dict[str, Any]) -> bool:
        """
        Check if recipient is valid for this channel.

        Args:
            recipient: Dictionary with recipient information

        Returns:
            True if recipient can receive via this channel, False otherwise

        Example:
            >>>
            >>> telegram.validate_recipient({'telegram_id': 123})
            >>> telegram.validate_recipient({'email': 'user@example.com'})

            >>>
            >>> email.validate_recipient({'email': 'user@example.com'})
            >>> email.validate_recipient({'telegram_id': 123})
        """
        pass

    @abstractmethod
    def get_channel_name(self) -> str:
        """
        Get human-readable name of this channel.

        Returns:
            Channel name (e.g., 'Telegram', 'Email', 'SMS')

        Example:
            >>> telegram.get_channel_name()
            'Telegram'
        """
        pass

    @abstractmethod
    async def validate_configuration(self) -> bool:
        """
        Check if this channel is properly configured.

        Returns:
            True if configured and ready to send, False otherwise

        Example:
            >>>
            >>> if not await email.validate_configuration():
            ...     logger.warning("Email not configured, skipping email channel")
        """
        pass

    async def test_connection(self) -> bool:
        """
        Test connection to the service (optional).

        Returns:
            True if connection successful, False otherwise

        Note:
            Override this method in subclasses if applicable.

        Example:
            >>> if await telegram.test_connection():
            ...     print("Bot is responding")
        """
        return True

    def __str__(self) -> str:
        """String representation."""
        return f"{self.get_channel_name()}Channel"

    def __repr__(self) -> str:
        """Detailed representation."""
        return f"<{self.get_channel_name()}Channel>"
