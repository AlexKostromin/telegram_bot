from typing import Optional
import logging
from aiogram import Bot
from config import ADMIN_IDS
from messages.texts import BotMessages

logger = logging.getLogger(__name__)

async def notify_user(
    bot: Bot,
    telegram_id: int,
    message: str
) -> None:
    try:
        logger.info(f"📤 Отправляю сообщение пользователю {telegram_id}...")
        result = await bot.send_message(telegram_id, message)
        logger.info(f"✅ Сообщение отправлено пользователю {telegram_id}, message_id={result.message_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки сообщения пользователю {telegram_id}: {e}")
        raise

async def notify_admins_new_registration(
    bot: Bot,
    user_name: str,
    competition_name: str,
    role: str
) -> None:
    if not ADMIN_IDS:
        return

    message = (
        f"📬 Новая заявка на регистрацию!\n\n"
        f"👤 {user_name}\n"
        f"🏆 {competition_name}\n"
        f"🎭 Роль: {role}"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, message)
        except Exception as e:
            logger.error(f"Error sending notification to admin {admin_id}: {e}")

async def notify_user_approved(bot: Bot, telegram_id: int, competition_name: str) -> None:
    message = f"✅ Ваша заявка на участие в «{competition_name}» одобрена!"

    try:
        await bot.send_message(telegram_id, message)
    except Exception as e:
        logger.error(f"Error notifying user {telegram_id}: {e}")

async def notify_user_rejected(bot: Bot, telegram_id: int, competition_name: str, reason: Optional[str] = None) -> None:
    message = f"❌ Ваша заявка на участие в «{competition_name}» отклонена."

    if reason:
        message += f"\n\nПричина: {reason}"

    try:
        await bot.send_message(telegram_id, message)
    except Exception as e:
        logger.error(f"Error notifying user {telegram_id}: {e}")

async def notify_user_revoked(bot: Bot, telegram_id: int, competition_name: str) -> None:
    message = f"⚠️ Ваша регистрация на «{competition_name}» была отозвана."

    try:
        await bot.send_message(telegram_id, message)
    except Exception as e:
        logger.error(f"Error notifying user {telegram_id}: {e}")

async def send_email(
    email_address: str,
    subject: str,
    body: str
) -> None:
    import asyncio
    import smtplib
    from email.mime.text import MIMEText
    from config.email_settings import SMTPConfig

    smtp_config = SMTPConfig()

    if not smtp_config.is_configured():
        logger.warning("SMTP not configured, skipping email")
        return

    try:
        logger.info(f"Отправляю email на {email_address}...")

        msg = MIMEText(body, 'html')
        msg['Subject'] = subject
        msg['From'] = smtp_config.get_from_address()
        msg['To'] = email_address

        host = smtp_config.SMTP_HOST
        port = smtp_config.SMTP_PORT
        username = smtp_config.SMTP_USERNAME
        password = smtp_config.SMTP_PASSWORD
        use_tls = smtp_config.SMTP_USE_TLS

        def send_smtp() -> None:
            server = smtplib.SMTP(host, port, timeout=15)
            if use_tls:
                server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, send_smtp)

        logger.info(f"Email отправлен на {email_address}")

    except Exception as e:
        logger.error(f"Ошибка отправки email на {email_address}: {e}")
        raise
