"""
Email notification channel for broadcast system.

Uses smtplib for async SMTP email delivery.
Supports both plain text and HTML emails with proper MIME formatting.
"""
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
    """
    Notification channel for sending emails via SMTP.

    Features:
    - HTML and plain text email support
    - Automatic configuration validation
    - Detailed error handling
    - MIME message construction
    - TLS/SSL support

    Example:
        >>> channel = EmailChannel()
        >>> if await channel.validate_configuration():
        ...     result = await channel.send(
        ...         recipient={'email': 'user@example.com', 'first_name': 'John'},
        ...         subject='Hello!',
        ...         body='<b>Welcome</b> to our service'
        ...     )
        ...     print(result.status)
    """

    def __init__(self):
        """Initialize Email channel with SMTP configuration."""
        self.config = SMTPConfig()

    def get_channel_name(self) -> str:
        """Get channel name."""
        return "Email"

    async def validate_configuration(self) -> bool:
        """
        Check if SMTP is properly configured.

        Returns:
            True if all required settings present, False otherwise

        Example:
            >>> if await email_channel.validate_configuration():
            ...     print("Email ready to send")
        """
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
        """
        Check if recipient has valid email address.

        Args:
            recipient: Recipient dictionary with 'email' key

        Returns:
            True if has valid email, False otherwise

        Example:
            >>> await email_channel.validate_recipient({'email': 'user@example.com'})
            True
            >>> await email_channel.validate_recipient({'telegram_id': 123})
            False
        """
        email_addr = recipient.get("email", "")
        if not email_addr:
            return False
        return self._is_valid_email(email_addr)

    @staticmethod
    def _is_valid_email(email_addr: str) -> bool:
        """
        Validate email address format.

        Args:
            email_addr: Email address to validate

        Returns:
            True if valid format, False otherwise

        Example:
            >>> EmailChannel._is_valid_email('user@example.com')
            True
            >>> EmailChannel._is_valid_email('invalid-email')
            False
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email_addr))

    def _create_message(
        self,
        recipient_email: str,
        subject: str,
        body: str
    ) -> MIMEMultipart:
        """
        Create MIME email message.

        Args:
            recipient_email: Recipient's email address
            subject: Email subject
            body: Email body (HTML or plain text)

        Returns:
            MIMEMultipart message ready to send

        Example:
            >>> msg = channel._create_message(
            ...     'user@example.com',
            ...     'Welcome!',
            ...     '<p>Hello!</p>'
            ... )
            >>> msg['Subject']
            'Welcome!'
        """

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
        """
        Send email message to recipient.

        Args:
            recipient: Recipient dict with 'email' key
            subject: Email subject
            body: Email body (HTML or plain text)

        Returns:
            DeliveryResult with status and error details if any

        Example:
            >>> result = await email_channel.send(
            ...     {'email': 'user@example.com', 'first_name': 'John'},
            ...     'Welcome to USN',
            ...     '<b>Hello John!</b>'
            ... )
            >>> print(result.status)
            sent
        """

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
        """
        Test SMTP connection without sending.

        Returns:
            True if can connect to SMTP server, False otherwise

        Example:
            >>> if await email_channel.test_connection():
            ...     print("SMTP server responding")
        """
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
        """Detailed representation."""
        server = f"{self.config.SMTP_HOST}:{self.config.SMTP_PORT}" if self.config.is_configured() else "unconfigured"
        return f"<EmailChannel smtp={server}>"
