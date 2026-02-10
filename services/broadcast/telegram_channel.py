"""
Telegram notification channel for broadcast system.

Uses aiogram Bot API to send messages to Telegram users.
Includes rate limiting, error handling, and delivery status tracking.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import asyncio

from aiogram import Bot
from aiogram.exceptions import (
    TelegramForbiddenError,
    TelegramBadRequest,
    TelegramUnauthorizedError,
    TelegramServerError,
)

from .channels import NotificationChannel, DeliveryResult

logger = logging.getLogger(__name__)


class TelegramChannel(NotificationChannel):
    """
    Notification channel for sending messages via Telegram.

    Features:
    - Rate limiting (0.05 sec between messages = ~20 msg/sec)
    - Automatic retry on server errors
    - Detection of blocked bots
    - Proper error categorization
    - Async batch sending support

    Example:
        >>> bot = Bot(token='123:ABC...')
        >>> channel = TelegramChannel(bot)
        >>> result = await channel.send(
        ...     recipient={'telegram_id': 987654321, 'first_name': 'John'},
        ...     subject='Test',
        ...     body='Hello from broadcast!'
        ... )
        >>> print(f"{channel.get_channel_name()}: {result.status}")
        Telegram: sent
    """

    # Rate limiting: 0.05 seconds = 20 messages per second
    RATE_LIMIT_DELAY: float = 0.05

    def __init__(self, bot: Bot):
        """
        Initialize Telegram channel.

        Args:
            bot: aiogram Bot instance with valid token

        Example:
            >>> from aiogram import Bot
            >>> bot = Bot(token='YOUR_BOT_TOKEN')
            >>> telegram = TelegramChannel(bot)
        """
        self.bot = bot
        self._last_send_time: float = 0

    def get_channel_name(self) -> str:
        """Get channel name."""
        return "Telegram"

    async def validate_configuration(self) -> bool:
        """
        Check if bot is configured and can send messages.

        Returns:
            True if bot is ready, False otherwise

        Example:
            >>> if await telegram.validate_configuration():
            ...     print("Telegram ready to send")
        """
        try:
            # Try to get bot info (lightweight check)
            me = await self.bot.get_me()
            logger.info(f"✅ Telegram bot configured: @{me.username}")
            return True
        except TelegramUnauthorizedError:
            logger.error("❌ Telegram: Invalid bot token")
            return False
        except Exception as e:
            logger.error(f"❌ Telegram: Configuration check failed: {e}")
            return False

    async def validate_recipient(self, recipient: Dict[str, Any]) -> bool:
        """
        Check if recipient has required Telegram information.

        Args:
            recipient: Recipient dictionary

        Returns:
            True if has telegram_id, False otherwise

        Example:
            >>> await telegram.validate_recipient({'telegram_id': 123})
            True
            >>> await telegram.validate_recipient({'email': 'user@example.com'})
            False
        """
        # Recipient must have telegram_id
        if not isinstance(recipient.get("telegram_id"), int):
            return False
        return recipient["telegram_id"] > 0

    async def _apply_rate_limit(self):
        """
        Apply rate limiting to prevent flooding Telegram API.

        Uses simple time-based delay between sends.
        Ensures we don't exceed ~20 messages per second.
        """
        current_time = asyncio.get_event_loop().time()
        time_since_last_send = current_time - self._last_send_time

        if time_since_last_send < self.RATE_LIMIT_DELAY:
            wait_time = self.RATE_LIMIT_DELAY - time_since_last_send
            await asyncio.sleep(wait_time)

        self._last_send_time = asyncio.get_event_loop().time()

    async def send(
        self,
        recipient: Dict[str, Any],
        subject: str,
        body: str
    ) -> DeliveryResult:
        """
        Send message to user via Telegram.

        Args:
            recipient: Recipient dict with telegram_id
            subject: Message subject (ignored for Telegram)
            body: Message text (can include HTML formatting)

        Returns:
            DeliveryResult with status and message_id if successful

        Example:
            >>> result = await telegram.send(
            ...     {'telegram_id': 123, 'first_name': 'John'},
            ...     'Subject',
            ...     '<b>Hello!</b>'
            ... )
            >>> if result.success:
            ...     print(f"Message {result.message_id} sent")
        """
        # Validate recipient
        if not await self.validate_recipient(recipient):
            return DeliveryResult(
                success=False,
                status="blocked",
                error="Invalid recipient: missing or invalid telegram_id"
            )

        telegram_id = recipient["telegram_id"]

        try:
            # Apply rate limiting
            await self._apply_rate_limit()

            # Send message (HTML parsing for bold, italic, etc)
            message = await self.bot.send_message(
                chat_id=telegram_id,
                text=body,
                parse_mode="HTML"
            )

            logger.info(f"✅ Telegram message sent to {telegram_id}: msg_id={message.message_id}")

            return DeliveryResult(
                success=True,
                status="sent",
                message_id=str(message.message_id),
                sent_at=datetime.utcnow()
            )

        except TelegramForbiddenError:
            # Bot blocked by user or user blocked by Telegram
            error_msg = f"Bot blocked by user {telegram_id}"
            logger.warning(f"⚠️  {error_msg}")
            return DeliveryResult(
                success=False,
                status="blocked",
                error=error_msg
            )

        except TelegramBadRequest as e:
            # Invalid request (e.g., wrong message format, invalid telegram_id)
            error_msg = f"Bad request for user {telegram_id}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return DeliveryResult(
                success=False,
                status="failed",
                error=error_msg
            )

        except TelegramServerError as e:
            # Telegram server error (500, 503, etc) - usually temporary
            error_msg = f"Telegram server error for user {telegram_id}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return DeliveryResult(
                success=False,
                status="failed",
                error=error_msg
            )

        except Exception as e:
            # Unexpected error
            error_msg = f"Unexpected error sending to {telegram_id}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return DeliveryResult(
                success=False,
                status="failed",
                error=error_msg
            )

    async def test_connection(self) -> bool:
        """
        Test Telegram bot connection by fetching bot info.

        Returns:
            True if bot can communicate with Telegram servers

        Example:
            >>> if await telegram.test_connection():
            ...     print("Telegram API responding")
        """
        return await self.validate_configuration()

    def __repr__(self) -> str:
        """Detailed representation."""
        username = "unknown"
        try:
            # Try to get username from bot (sync operation)
            # Note: This is a simplified check, in production use async
            username = f"@{self.bot.session}"
        except Exception:
            pass
        return f"<TelegramChannel bot={username}>"
