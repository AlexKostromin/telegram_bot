from typing import Dict, Any, Optional
from datetime import datetime
import logging
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import smtplib
import asyncio

from config.email_settings import SMTPConfig
from .channels import NotificationChannel, DeliveryResult

logger = logging.getLogger(__name__)

class EmailChannel(NotificationChannel):

    def __init__(self):
        self.config = SMTPConfig()

    def get_channel_name(self) -> str:
        return "Email"

    async def validate_configuration(self) -> bool:
        if not self.config.is_configured():
            logger.warning(
                "❌ Email: SMTP not configured. "
                "Set SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, SUPPORT_EMAIL"
            )
            return False

        from_address = self.config.get_from_address()
        if not self._is_valid_email(from_address):
            logger.error(f"❌ Email: Invalid email address: {from_address}")
            return False

        logger.info(f"✅ Email configured: from {from_address}")
        return True

    async def validate_recipient(self, recipient: Dict[str, Any]) -> bool:
        email_addr = recipient.get("email", "")
        if not email_addr:
            return False
        return self._is_valid_email(email_addr)

    @staticmethod
    def _is_valid_email(email_addr: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email_addr))

    def _create_message(
        self,
        recipient_email: str,
        subject: str,
        body: str
    ) -> MIMEMultipart:

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        from_address = self.config.get_from_address()
        msg["From"] = f"{self.config.EMAIL_FROM_NAME} <{from_address}>"
        msg["To"] = recipient_email
        msg["X-Mailer"] = "USN Broadcast System"

        is_html = body.lower().startswith("<html") or "<p>" in body.lower() or "<b>" in body.lower()

        if is_html:

            part = MIMEText(body, "html", _charset="utf-8")
        else:

            part = MIMEText(body, "plain", _charset="utf-8")

        msg.attach(part)
        return msg

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
                error="Invalid recipient: missing or invalid email"
            )

        recipient_email = recipient["email"]

        try:

            if not await self.validate_configuration():
                return DeliveryResult(
                    success=False,
                    status="failed",
                    error="SMTP not configured"
                )

            msg = self._create_message(recipient_email, subject, body)

            def send_smtp():

                server = smtplib.SMTP(
                    self.config.SMTP_HOST,
                    self.config.SMTP_PORT,
                    timeout=10
                )

                if self.config.SMTP_USE_TLS:
                    server.starttls()

                server.login(
                    self.config.SMTP_USERNAME,
                    self.config.SMTP_PASSWORD
                )
                server.send_message(msg)
                server.quit()

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, send_smtp)

            logger.info(f"✅ Email sent to {recipient_email}: {subject}")

            return DeliveryResult(
                success=True,
                status="sent",
                sent_at=datetime.utcnow()
            )

        except TimeoutError:
            error_msg = f"Timeout connecting to SMTP server {self.config.SMTP_HOST}:{self.config.SMTP_PORT}"
            logger.error(f"❌ {error_msg}")
            return DeliveryResult(
                success=False,
                status="failed",
                error=error_msg
            )

        except ConnectionError as e:
            error_msg = f"Connection error to SMTP server: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return DeliveryResult(
                success=False,
                status="failed",
                error=error_msg
            )

        except Exception as e:
            error_msg = f"Error sending email to {recipient_email}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return DeliveryResult(
                success=False,
                status="failed",
                error=error_msg
            )

    async def test_connection(self) -> bool:
        try:
            if not await self.validate_configuration():
                return False

            def test_smtp():
                server = smtplib.SMTP(
                    self.config.SMTP_HOST,
                    self.config.SMTP_PORT,
                    timeout=5
                )

                if self.config.SMTP_USE_TLS:
                    server.starttls()

                server.login(
                    self.config.SMTP_USERNAME,
                    self.config.SMTP_PASSWORD
                )
                server.quit()
                return True

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, test_smtp)

            logger.info("✅ Email SMTP connection successful")
            return True

        except Exception as e:
            logger.error(f"❌ Email SMTP connection failed: {e}")
            return False

    def __repr__(self) -> str:
        server = f"{self.config.SMTP_HOST}:{self.config.SMTP_PORT}" if self.config.is_configured() else "unconfigured"
        return f"<EmailChannel smtp={server}>"
