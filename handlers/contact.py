import logging
from aiogram import Router, Bot
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

    user_message: str = message.text
    user_id: int = message.from_user.id
    username: str = message.from_user.username or "Неизвестно"
    first_name: str = message.from_user.first_name or "Unknown"
    last_name: str = message.from_user.last_name or ""

    smtp_config = SMTPConfig()
    support_email = smtp_config.SUPPORT_EMAIL
    support_telegram_id = smtp_config.SUPPORT_TELEGRAM_ID

    logger.info(f"📧 Support message from user {user_id} (@{username})")

    email_body: str = (
        f"Сообщение от пользователя:\n"
        f"Имя: {first_name} {last_name}\n"
        f"Telegram: @{username} (ID: {user_id})\n\n"
        f"{user_message}"
    )

    telegram_message: str = (
        f"<b>📧 Сообщение из поддержки</b>\n\n"
        f"👤 {first_name} {last_name} (@{username})\n"
        f"🆔 ID: {user_id}\n\n"
        f"💬 {user_message}"
    )

    delivery_success = False

    if support_email:
        try:
            email_subject = f"Сообщение из поддержки бота от @{username}"
            await send_email(support_email, email_subject, email_body)
            logger.info(f"Support email sent to {support_email}")
            delivery_success = True
        except Exception as e:
            logger.error(f"Error sending support email: {e}")

    if support_telegram_id and support_telegram_id > 0:
        try:
            await bot.send_message(
                chat_id=support_telegram_id,
                text=telegram_message,
                parse_mode="HTML"
            )
            logger.info(f"Support message sent to Telegram ID {support_telegram_id}")
            delivery_success = True
        except Exception as e:
            logger.error(f"Error sending support message to Telegram: {e}")

    if delivery_success:
        await message.answer(
            BotMessages.CONTACT_SUCCESS,
            reply_markup=InlineKeyboards.main_menu_keyboard(),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            "К сожалению, не удалось отправить сообщение. Попробуйте позже.",
            reply_markup=InlineKeyboards.main_menu_keyboard(),
            parse_mode="HTML",
        )

    await state.clear()
