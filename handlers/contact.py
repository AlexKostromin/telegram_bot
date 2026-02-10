"""
Обработчик для "Связаться с командой USN".
"""
from typing import Optional
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from messages import BotMessages
from keyboards import InlineKeyboards
from states import ContactStates
from config.email_settings import SMTPConfig
from utils.notifications import send_email

logger = logging.getLogger(__name__)

contact_router = Router()

@contact_router.message(StateFilter(ContactStates.waiting_for_message))
async def contact_message_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Обработчик сообщения для команды USN.
    Отправляет сообщение в поддержку по Email и/или Telegram.

    Args:
        message: Объект сообщения
        state: Контекст FSM
        bot: Telegram бот
    """

    user_message: str = message.text
    user_id: int = message.from_user.id
    username: str = message.from_user.username or "Неизвестно"
    first_name: str = message.from_user.first_name or "Unknown"
    last_name: str = message.from_user.last_name or ""

    smtp_config = SMTPConfig()
    support_email = smtp_config.SUPPORT_EMAIL
    support_telegram_id = smtp_config.SUPPORT_TELEGRAM_ID

    logger.info(f"📧 Support message from user {user_id} (@{username})")

    if support_email:
        try:
            email_subject = f"📧 Сообщение из поддержки бота от @{username}"
            email_body = f"""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>📧 Новое сообщение в поддержку</h2>

    <p><strong>От:</strong> {first_name} {last_name}</p>
    <p><strong>Telegram ID:</strong> {user_id}</p>
    <p><strong>Username:</strong> @{username}</p>
    <p><strong>Дата:</strong> {message.date.isoformat()}</p>

    <hr>

    <h3>Сообщение:</h3>
    <p>{user_message.replace(chr(10), '<br>')}</p>

    <hr>

    <p><small>Это автоматическое письмо от бота регистрации на соревнования USN</small></p>
</body>
</html>
            """

            await send_email(support_email, email_subject, email_body)
            logger.info(f"✅ Support email sent to {support_email}")
        except Exception as e:
            logger.error(f"❌ Error sending support email: {e}")

    if support_telegram_id and support_telegram_id > 0:
        try:
            telegram_message = f"""
📧 <b>Новое сообщение в поддержку</b>

👤 <b>От:</b> {first_name} {last_name}
🔑 <b>Telegram ID:</b> <code>{user_id}</code>
📱 <b>Username:</b> @{username}

<b>Сообщение:</b>
<pre>{user_message}</pre>
            """

            await bot.send_message(
                chat_id=support_telegram_id,
                text=telegram_message,
                parse_mode="HTML"
            )
            logger.info(f"✅ Support message sent to Telegram ID {support_telegram_id}")
        except Exception as e:
            logger.error(f"❌ Error sending support message to Telegram: {e}")

    await message.answer(
        BotMessages.CONTACT_SUCCESS,
        reply_markup=InlineKeyboards.main_menu_keyboard(),
    )

    logger.info(f"✅ Confirmation sent to user {user_id}")

    await state.clear()
