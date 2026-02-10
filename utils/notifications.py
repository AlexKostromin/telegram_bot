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
    import logging
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"📤 Отправляю сообщение пользователю {telegram_id}...")
        result = await bot.send_message(telegram_id, message)
        logger.info(f"✅ Сообщение отправлено пользователю {telegram_id}, message_id={result.message_id}")
        print(f"✅ Notification sent to {telegram_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки сообщения пользователю {telegram_id}: {e}")
        print(f"❌ Error sending notification to user {telegram_id}: {e}")
        raise

async def notify_admins_new_registration(
    bot: Bot,
    user_name: str,
    competition_name: str,
    role: str
) -> None:
    if not ADMIN_IDS:
        return


    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, message)
        except Exception as e:
            print(f"Error sending notification to admin {admin_id}: {e}")

async def notify_user_approved(bot: Bot, telegram_id: int, competition_name: str) -> None:

    try:
        await bot.send_message(telegram_id, message)
    except Exception as e:
        print(f"Error notifying user {telegram_id}: {e}")

async def notify_user_rejected(bot: Bot, telegram_id: int, competition_name: str, reason: Optional[str] = None) -> None:

    if reason:
        message += f"\n\nПричина: {reason}"

    try:
        await bot.send_message(telegram_id, message)
    except Exception as e:
        print(f"Error notifying user {telegram_id}: {e}")

async def notify_user_revoked(bot: Bot, telegram_id: int, competition_name: str) -> None:

    try:
        await bot.send_message(telegram_id, message)
    except Exception as e:
        print(f"Error notifying user {telegram_id}: {e}")

async def send_email(
    email_address: str,
    subject: str,
    body: str
) -> None:
    import os
    import asyncio
    import smtplib
    from dotenv import load_dotenv
    from email.mime.text import MIMEText

    load_dotenv()

    SMTP_HOST = os.getenv('SMTP_HOST')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'True').lower() == 'true'
    EMAIL_FROM = os.getenv('SUPPORT_EMAIL') or os.getenv('EMAIL_FROM_ADDRESS', 'noreply@example.com')

    if not all([SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD]):
        logger.warning("SMTP not configured, skipping email")
        print("⚠️  SMTP not configured")
        return

    try:
        logger.info(f"📧 Отправляю email на {email_address}...")

        message = MIMEText(body, 'html')
        message['Subject'] = subject
        message['From'] = EMAIL_FROM
        message['To'] = email_address

        def send_smtp() -> None:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)

            if SMTP_USE_TLS:
                server.starttls()

            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)
            server.quit()

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, send_smtp)

        logger.info(f"✅ Email отправлен на {email_address}")
        print(f"✅ Email sent to {email_address}")

    except Exception as e:
        logger.error(f"❌ Ошибка отправки email на {email_address}: {e}")
        print(f"❌ Error sending email to {email_address}: {e}")
