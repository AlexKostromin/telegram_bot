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

    RATE_LIMIT_DELAY: float = 0.05

    def __init__(self, bot: Bot):
        self.bot = bot
        self._last_send_time: float = 0

    def get_channel_name(self) -> str:
        return "Telegram"

    async def validate_configuration(self) -> bool:
        try:
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
        if not isinstance(recipient.get("telegram_id"), int):
            return False
        return recipient["telegram_id"] > 0

    async def _apply_rate_limit(self):
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
        if not await self.validate_recipient(recipient):
            return DeliveryResult(
                success=False,
                status="blocked",
                error="Invalid recipient: missing or invalid telegram_id"
            )

        telegram_id = recipient["telegram_id"]

        try:
            await self._apply_rate_limit()

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
            error_msg = f"Bot blocked by user {telegram_id}"
            logger.warning(f"⚠️  {error_msg}")
            return DeliveryResult(
                success=False,
                status="blocked",
                error=error_msg
            )

        except TelegramBadRequest as e:
            error_msg = f"Bad request for user {telegram_id}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return DeliveryResult(
                success=False,
                status="failed",
                error=error_msg
            )

        except TelegramServerError as e:
            error_msg = f"Telegram server error for user {telegram_id}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return DeliveryResult(
                success=False,
                status="failed",
                error=error_msg
            )

        except Exception as e:
            error_msg = f"Unexpected error sending to {telegram_id}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return DeliveryResult(
                success=False,
                status="failed",
                error=error_msg
            )

    async def test_connection(self) -> bool:
        return await self.validate_configuration()

    def __repr__(self) -> str:
        username = "unknown"
        try:

            username = f"@{self.bot.session}"
        except Exception:
            pass
        return f"<TelegramChannel bot={username}>"
