"""
Notification system for registration updates.
"""
from typing import Optional
from aiogram import Bot
from config import ADMIN_IDS
from messages.texts import BotMessages


async def notify_admins_new_registration(
    bot: Bot,
    user_name: str,
    competition_name: str,
    role: str
) -> None:
    """Send notification to all admins about new registration."""
    if not ADMIN_IDS:
        return

    message: str = f"""
📬 Новая заявка!

👤 {user_name}
🏆 {competition_name}
🎭 {role}

Используйте команду /admin для просмотра и утверждения заявки.
    """.strip()

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, message)
        except Exception as e:
            print(f"Error sending notification to admin {admin_id}: {e}")


async def notify_user_approved(bot: Bot, telegram_id: int, competition_name: str) -> None:
    """Notify user about registration approval."""
    message: str = f"""
🎉 Ваша заявка на {competition_name} одобрена!

Добро пожаловать в число участников!
    """.strip()

    try:
        await bot.send_message(telegram_id, message)
    except Exception as e:
        print(f"Error notifying user {telegram_id}: {e}")


async def notify_user_rejected(bot: Bot, telegram_id: int, competition_name: str, reason: Optional[str] = None) -> None:
    """Notify user about registration rejection."""
    message: str = f"""
❌ К сожалению, ваша заявка на {competition_name} отклонена.
    """.strip()

    if reason:
        message += f"\n\nПричина: {reason}"

    try:
        await bot.send_message(telegram_id, message)
    except Exception as e:
        print(f"Error notifying user {telegram_id}: {e}")


async def notify_user_revoked(bot: Bot, telegram_id: int, competition_name: str) -> None:
    """Notify user about registration revocation."""
    message: str = f"""
⚠️ Ваша регистрация на {competition_name} была отозвана администратором.
    """.strip()

    try:
        await bot.send_message(telegram_id, message)
    except Exception as e:
        print(f"Error notifying user {telegram_id}: {e}")
