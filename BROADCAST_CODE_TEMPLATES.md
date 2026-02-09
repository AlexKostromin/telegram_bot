# Broadcast System - Code Templates & Snippets

**Copy-paste starter code for each module**

---

## 📄 Task #1: models/broadcast.py

```python
"""
Broadcast system models for mass messaging.
"""
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, JSON
from models.user import Base


class BroadcastStatus(str, Enum):
    """Status of a broadcast."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class DeliveryStatus(str, Enum):
    """Status of individual message delivery."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BLOCKED = "blocked"


class MessageTemplate(Base):
    """Reusable message template with variables."""

    __tablename__: str = "message_templates"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(255), unique=True, nullable=False, index=True)
    description: Optional[str] = Column(Text, nullable=True)
    subject: str = Column(String(500), nullable=False)
    body_telegram: str = Column(Text, nullable=False)
    body_email: str = Column(Text, nullable=False)
    available_variables: Dict[str, str] = Column(JSON, nullable=False)
    is_active: bool = Column(Boolean, default=True)
    created_by: Optional[int] = Column(Integer, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __str__(self) -> str:
        """String representation."""
        return f"MessageTemplate: {self.name}"


class Broadcast(Base):
    """Broadcast job configuration."""

    __tablename__: str = "broadcasts"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(255), nullable=False, index=True)
    template_id: int = Column(Integer, ForeignKey("message_templates.id"), nullable=False)
    filters: Dict[str, Any] = Column(JSON, nullable=False)
    send_telegram: bool = Column(Boolean, default=True)
    send_email: bool = Column(Boolean, default=True)
    scheduled_at: Optional[datetime] = Column(DateTime, nullable=True)
    status: str = Column(String(20), default=BroadcastStatus.DRAFT.value, index=True)
    total_recipients: int = Column(Integer, default=0)
    sent_count: int = Column(Integer, default=0)
    failed_count: int = Column(Integer, default=0)
    started_at: Optional[datetime] = Column(DateTime, nullable=True)
    completed_at: Optional[datetime] = Column(DateTime, nullable=True)
    created_by: int = Column(Integer, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __str__(self) -> str:
        """String representation."""
        return f"Broadcast: {self.name} ({self.status})"

    def get_progress_percentage(self) -> int:
        """Get completion percentage."""
        if self.total_recipients == 0:
            return 0
        return int((self.sent_count / self.total_recipients) * 100)


class BroadcastRecipient(Base):
    """Individual delivery tracking per recipient."""

    __tablename__: str = "broadcast_recipients"

    id: int = Column(Integer, primary_key=True)
    broadcast_id: int = Column(Integer, ForeignKey("broadcasts.id"), nullable=False, index=True)
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    telegram_id: int = Column(Integer, nullable=False)

    # Telegram delivery
    telegram_status: str = Column(String(20), default=DeliveryStatus.PENDING.value, index=True)
    telegram_sent_at: Optional[datetime] = Column(DateTime, nullable=True)
    telegram_error: Optional[str] = Column(Text, nullable=True)
    telegram_message_id: Optional[int] = Column(Integer, nullable=True)

    # Email delivery
    email_status: str = Column(String(20), default=DeliveryStatus.PENDING.value, index=True)
    email_sent_at: Optional[datetime] = Column(DateTime, nullable=True)
    email_error: Optional[str] = Column(Text, nullable=True)
    email_address: Optional[str] = Column(String(255), nullable=True)

    # Rendered content (audit trail)
    rendered_subject: Optional[str] = Column(String(500), nullable=True)
    rendered_body: Optional[str] = Column(Text, nullable=True)

    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __str__(self) -> str:
        """String representation."""
        return f"Recipient {self.telegram_id} (TG:{self.telegram_status}, Email:{self.email_status})"

    def is_delivery_complete(self) -> bool:
        """Check if delivery complete on at least one channel."""
        return self.telegram_status in [DeliveryStatus.SENT.value, DeliveryStatus.DELIVERED.value] or \
               self.email_status in [DeliveryStatus.SENT.value, DeliveryStatus.DELIVERED.value]
```

---

## 📄 Task #2: config/email_settings.py

```python
"""
Email configuration for broadcast system.
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class EmailConfig:
    """SMTP configuration."""

    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "True").lower() == "true"

    EMAIL_FROM_ADDRESS: str = os.getenv("EMAIL_FROM_ADDRESS", "noreply@example.com")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "USN Competitions")

    @classmethod
    def is_configured(cls) -> bool:
        """Check if SMTP is properly configured."""
        return bool(cls.SMTP_USERNAME and cls.SMTP_PASSWORD)

    @classmethod
    def get_from_header(cls) -> str:
        """Get From header."""
        return f"{cls.EMAIL_FROM_NAME} <{cls.EMAIL_FROM_ADDRESS}>"


email_config = EmailConfig()
```

---

## 📄 Task #3: services/broadcast/channels.py

```python
"""
Abstract notification channel interface.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class DeliveryResult:
    """Result of message delivery attempt."""
    success: bool
    status: str  # sent, delivered, failed, blocked
    message_id: Optional[str] = None
    error: Optional[str] = None
    sent_at: Optional[datetime] = field(default_factory=datetime.utcnow)

    def __str__(self) -> str:
        """String representation."""
        if self.success:
            return f"DeliveryResult(✓ {self.status})"
        return f"DeliveryResult(✗ {self.status}: {self.error})"


class NotificationChannel(ABC):
    """Abstract base class for notification channels."""

    @abstractmethod
    async def send(
        self,
        recipient: Dict[str, Any],
        subject: str,
        body: str
    ) -> DeliveryResult:
        """
        Send notification to recipient.

        Args:
            recipient: Dictionary with recipient data (must include required fields)
            subject: Message subject (for email)
            body: Message body (Telegram text or Email HTML)

        Returns:
            DeliveryResult with success/failure status
        """
        pass

    @abstractmethod
    async def validate_recipient(self, recipient: Dict[str, Any]) -> bool:
        """
        Validate recipient data.

        Args:
            recipient: Dictionary with recipient data

        Returns:
            True if valid, False otherwise
        """
        pass

    @abstractmethod
    def get_channel_name(self) -> str:
        """
        Get channel identifier.

        Returns:
            Channel name (e.g., 'telegram', 'email')
        """
        pass
```

---

## 📄 Task #4: services/broadcast/telegram_channel.py

```python
"""
Telegram notification channel implementation.
"""
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from .channels import NotificationChannel, DeliveryResult

logger = logging.getLogger(__name__)

# Rate limiting: 0.05 seconds between messages = 20 messages/second
TELEGRAM_RATE_LIMIT_SECONDS = 0.05


class TelegramChannel(NotificationChannel):
    """Telegram notification channel using aiogram."""

    def __init__(self, bot: Bot) -> None:
        """
        Initialize Telegram channel.

        Args:
            bot: aiogram Bot instance
        """
        self.bot: Bot = bot
        self.last_send_time: float = 0

    async def send(
        self,
        recipient: Dict[str, Any],
        subject: str,
        body: str
    ) -> DeliveryResult:
        """
        Send Telegram message with rate limiting.

        Args:
            recipient: Must contain 'telegram_id'
            subject: Ignored (not used in Telegram)
            body: Message text to send

        Returns:
            DeliveryResult with delivery status
        """
        try:
            # Validate recipient
            if not await self.validate_recipient(recipient):
                return DeliveryResult(
                    success=False,
                    status="failed",
                    error="Invalid telegram_id"
                )

            # Apply rate limiting
            await self._rate_limit()

            # Send message
            message = await self.bot.send_message(
                chat_id=recipient['telegram_id'],
                text=body
            )

            logger.info(f"Telegram message sent to {recipient['telegram_id']}, msg_id={message.message_id}")

            return DeliveryResult(
                success=True,
                status="sent",
                message_id=str(message.message_id),
                sent_at=datetime.utcnow()
            )

        except TelegramForbiddenError as e:
            logger.warning(f"User {recipient.get('telegram_id')} blocked bot: {e}")
            return DeliveryResult(
                success=False,
                status="blocked",
                error="User blocked bot"
            )

        except TelegramBadRequest as e:
            logger.warning(f"Bad request for {recipient.get('telegram_id')}: {e}")
            return DeliveryResult(
                success=False,
                status="failed",
                error=str(e)
            )

        except Exception as e:
            logger.error(f"Telegram send error for {recipient.get('telegram_id')}: {e}")
            return DeliveryResult(
                success=False,
                status="failed",
                error=str(e)
            )

    async def validate_recipient(self, recipient: Dict[str, Any]) -> bool:
        """
        Validate Telegram recipient.

        Args:
            recipient: Dictionary with recipient data

        Returns:
            True if telegram_id is valid
        """
        if 'telegram_id' not in recipient:
            return False

        telegram_id = recipient['telegram_id']
        return isinstance(telegram_id, int) and telegram_id > 0

    def get_channel_name(self) -> str:
        """Get channel name."""
        return "telegram"

    async def _rate_limit(self) -> None:
        """Apply rate limiting between messages."""
        import time
        current_time = time.time()
        time_since_last = current_time - self.last_send_time

        if time_since_last < TELEGRAM_RATE_LIMIT_SECONDS:
            await asyncio.sleep(TELEGRAM_RATE_LIMIT_SECONDS - time_since_last)

        self.last_send_time = time.time()
```

---

## 📄 Task #5: services/broadcast/email_channel.py

```python
"""
Email notification channel implementation.
"""
import logging
from typing import Dict, Any
from datetime import datetime
from email.mime.text import MIMEText

import aiosmtplib

from config.email_settings import EmailConfig
from .channels import NotificationChannel, DeliveryResult

logger = logging.getLogger(__name__)


class EmailChannel(NotificationChannel):
    """Email notification channel using aiosmtplib."""

    def __init__(self, email_config: EmailConfig) -> None:
        """
        Initialize Email channel.

        Args:
            email_config: EmailConfig instance with SMTP settings
        """
        self.config: EmailConfig = email_config

    async def send(
        self,
        recipient: Dict[str, Any],
        subject: str,
        body: str
    ) -> DeliveryResult:
        """
        Send email message.

        Args:
            recipient: Must contain 'email'
            subject: Email subject
            body: Email body (HTML or plain text)

        Returns:
            DeliveryResult with delivery status
        """
        try:
            # Validate recipient
            if not await self.validate_recipient(recipient):
                return DeliveryResult(
                    success=False,
                    status="failed",
                    error="Invalid email address"
                )

            email_address = recipient['email']

            # Create message
            message = MIMEText(body, 'html')
            message['Subject'] = subject
            message['From'] = self.config.get_from_header()
            message['To'] = email_address

            # Send via SMTP
            async with aiosmtplib.SMTP(
                hostname=self.config.SMTP_HOST,
                port=self.config.SMTP_PORT
            ) as smtp:
                if self.config.SMTP_USE_TLS:
                    await smtp.starttls()

                await smtp.login(
                    self.config.SMTP_USERNAME,
                    self.config.SMTP_PASSWORD
                )

                await smtp.send_message(message)

            logger.info(f"Email sent to {email_address}")

            return DeliveryResult(
                success=True,
                status="sent",
                sent_at=datetime.utcnow()
            )

        except aiosmtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return DeliveryResult(
                success=False,
                status="failed",
                error="SMTP authentication failed"
            )

        except Exception as e:
            logger.error(f"Email send error to {recipient.get('email')}: {e}")
            return DeliveryResult(
                success=False,
                status="failed",
                error=str(e)
            )

    async def validate_recipient(self, recipient: Dict[str, Any]) -> bool:
        """
        Validate email recipient.

        Args:
            recipient: Dictionary with recipient data

        Returns:
            True if email is valid
        """
        if 'email' not in recipient:
            return False

        email = recipient['email']
        # Simple email validation
        return isinstance(email, str) and '@' in email and '.' in email

    def get_channel_name(self) -> str:
        """Get channel name."""
        return "email"
```

---

## 📄 Task #6: services/broadcast/template_renderer.py

```python
"""
Template rendering with Jinja2.
"""
import logging
from typing import Dict, Any, List, Tuple, Optional

from jinja2 import Template, TemplateSyntaxError, UndefinedError

logger = logging.getLogger(__name__)


class TemplateRenderer:
    """Jinja2 based template renderer for message templates."""

    DEFAULT_VARIABLES: Dict[str, str] = {
        'first_name': 'Имя пользователя',
        'last_name': 'Фамилия пользователя',
        'email': 'Email адрес',
        'phone': 'Телефон',
        'country': 'Страна',
        'city': 'Город',
        'club': 'Клуб/школа',
        'company': 'Компания',
        'position': 'Должность',
        'competition_name': 'Название соревнования',
        'role': 'Роль участника',
        'registration_status': 'Статус регистрации',
        'telegram_username': 'Telegram username',
    }

    def render(
        self,
        template_text: str,
        variables: Dict[str, Any]
    ) -> str:
        """
        Render template with variables.

        Args:
            template_text: Template text with {{variable}} placeholders
            variables: Dictionary of values for substitution

        Returns:
            Rendered text

        Raises:
            TemplateSyntaxError: If template syntax is invalid
        """
        try:
            template = Template(template_text)
            return template.render(**variables)
        except TemplateSyntaxError as e:
            logger.error(f"Template syntax error: {e}")
            raise
        except UndefinedError as e:
            logger.warning(f"Undefined variable in template: {e}")
            # Render with empty string for undefined variables
            template = Template(template_text)
            return template.render(**variables)

    def validate_template(self, template_text: str) -> Tuple[bool, Optional[str]]:
        """
        Validate template syntax.

        Args:
            template_text: Template to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            Template(template_text)
            return True, None
        except TemplateSyntaxError as e:
            return False, str(e)

    def extract_variables(self, template_text: str) -> List[str]:
        """
        Extract variable names from template.

        Args:
            template_text: Template text

        Returns:
            List of variable names found in template
        """
        import re
        # Find {{variable}} patterns
        variables = set(re.findall(r'\{\{\s*(\w+)\s*\}\}', template_text))
        return sorted(list(variables))

    def render_with_defaults(
        self,
        template_text: str,
        user_data: Dict[str, Any]
    ) -> str:
        """
        Render template with user data, using defaults for missing vars.

        Args:
            template_text: Template text
            user_data: User-specific data

        Returns:
            Rendered text
        """
        # Merge defaults with user data
        variables = {**{k: f"[{v}]" for k, v in self.DEFAULT_VARIABLES.items()}, **user_data}
        return self.render(template_text, variables)
```

---

## 📄 Task #7: services/broadcast/recipient_filter.py

```python
"""
Recipient filtering and database queries.
"""
import logging
from typing import Dict, Any, List, Tuple, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import UserModel, CompetitionModel, RegistrationModel

logger = logging.getLogger(__name__)


class RecipientFilter:
    """Filter recipients from database based on criteria."""

    def __init__(self, session_maker) -> None:
        """
        Initialize filter.

        Args:
            session_maker: AsyncSession factory
        """
        self.session_maker = session_maker

    async def get_recipients(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get recipients matching filters.

        Args:
            filters: Filter criteria (competition_ids, roles, statuses, countries, cities, has_email)

        Returns:
            List of recipient dictionaries with all fields
        """
        async with self.session_maker() as session:
            query = select(
                UserModel.id,
                UserModel.telegram_id,
                UserModel.email,
                UserModel.first_name,
                UserModel.last_name,
                UserModel.country,
                UserModel.city,
                UserModel.phone,
                UserModel.club,
                UserModel.company,
                UserModel.position,
                UserModel.telegram_username,
                CompetitionModel.name.label('competition_name'),
                RegistrationModel.role,
                RegistrationModel.status.label('registration_status')
            ).select_from(UserModel).join(
                RegistrationModel, UserModel.id == RegistrationModel.user_id
            ).join(
                CompetitionModel, RegistrationModel.competition_id == CompetitionModel.id
            )

            # Apply filters
            if 'competition_ids' in filters:
                query = query.where(CompetitionModel.id.in_(filters['competition_ids']))

            if 'roles' in filters:
                query = query.where(RegistrationModel.role.in_(filters['roles']))

            if 'statuses' in filters:
                query = query.where(RegistrationModel.status.in_(filters['statuses']))

            if 'countries' in filters:
                query = query.where(UserModel.country.in_(filters['countries']))

            if 'cities' in filters:
                query = query.where(UserModel.city.in_(filters['cities']))

            if filters.get('has_email', False):
                query = query.where(UserModel.email != '')

            result = await session.execute(query)
            return [dict(row._mapping) for row in result.fetchall()]

    async def count_recipients(self, filters: Dict[str, Any]) -> int:
        """
        Count recipients matching filters.

        Args:
            filters: Filter criteria

        Returns:
            Number of matching recipients
        """
        recipients = await self.get_recipients(filters)
        return len(recipients)

    async def get_available_filters(self) -> Dict[str, List[Any]]:
        """
        Get available filter options from database.

        Returns:
            Dictionary with available filter values
        """
        async with self.session_maker() as session:
            # Get unique roles
            result = await session.execute(select(RegistrationModel.role).distinct())
            roles = [row[0] for row in result.fetchall()]

            # Get unique competitions
            result = await session.execute(select(CompetitionModel.id, CompetitionModel.name))
            competitions = [(row[0], row[1]) for row in result.fetchall()]

            # Get unique statuses
            result = await session.execute(select(RegistrationModel.status).distinct())
            statuses = [row[0] for row in result.fetchall()]

            return {
                'roles': roles,
                'competitions': competitions,
                'statuses': statuses,
            }

    def validate_filters(self, filters: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate filter structure.

        Args:
            filters: Filter criteria

        Returns:
            Tuple of (is_valid, error_message)
        """
        allowed_keys = {'competition_ids', 'roles', 'statuses', 'countries', 'cities', 'has_email'}

        for key in filters.keys():
            if key not in allowed_keys:
                return False, f"Unknown filter key: {key}"

        # Validate types
        if 'competition_ids' in filters and not isinstance(filters['competition_ids'], list):
            return False, "competition_ids must be a list"

        if 'roles' in filters and not isinstance(filters['roles'], list):
            return False, "roles must be a list"

        if 'has_email' in filters and not isinstance(filters['has_email'], bool):
            return False, "has_email must be a boolean"

        return True, None
```

---

## 📄 Task #8: services/broadcast/orchestrator.py

```python
"""
Broadcast orchestrator - coordinates entire broadcast workflow.
"""
import asyncio
import logging
from typing import Dict, Any, Tuple, Optional
from datetime import datetime

from aiogram import Bot

from models import MessageTemplate, Broadcast, BroadcastRecipient, BroadcastStatus, DeliveryStatus
from config.email_settings import EmailConfig
from utils.database import DatabaseManager
from .template_renderer import TemplateRenderer
from .recipient_filter import RecipientFilter
from .telegram_channel import TelegramChannel
from .email_channel import EmailChannel
from .channels import NotificationChannel, DeliveryResult

logger = logging.getLogger(__name__)


class BroadcastOrchestrator:
    """Orchestrates broadcast execution."""

    def __init__(
        self,
        db: DatabaseManager,
        bot: Bot,
        email_config: EmailConfig
    ) -> None:
        """
        Initialize orchestrator.

        Args:
            db: DatabaseManager instance
            bot: aiogram Bot instance
            email_config: Email configuration
        """
        self.db: DatabaseManager = db
        self.bot: Bot = bot
        self.email_config: EmailConfig = email_config

        self.renderer: TemplateRenderer = TemplateRenderer()
        self.filter: RecipientFilter = RecipientFilter(db.async_session_maker)
        self.telegram_channel: TelegramChannel = TelegramChannel(bot)
        self.email_channel: EmailChannel = EmailChannel(email_config)

    async def execute_broadcast(self, broadcast_id: int) -> Dict[str, Any]:
        """
        Execute broadcast.

        Args:
            broadcast_id: Broadcast ID

        Returns:
            Statistics dictionary with results
        """
        try:
            # Load broadcast and template
            broadcast = await self.db.get_broadcast_by_id(broadcast_id)
            if not broadcast:
                raise ValueError(f"Broadcast {broadcast_id} not found")

            template = await self.db.get_message_template(broadcast.template_id)
            if not template:
                raise ValueError(f"Template {broadcast.template_id} not found")

            # Get recipients
            logger.info(f"Loading recipients for broadcast {broadcast_id}...")
            recipients = await self.filter.get_recipients(broadcast.filters)
            logger.info(f"Found {len(recipients)} recipients")

            if not recipients:
                return {
                    'success': False,
                    'error': 'No recipients found',
                    'total': 0,
                    'sent': 0,
                    'failed': 0
                }

            # Update broadcast status
            broadcast.status = BroadcastStatus.IN_PROGRESS.value
            broadcast.total_recipients = len(recipients)
            broadcast.started_at = datetime.utcnow()
            await self.db.session.commit()

            # Send to each recipient
            sent_count = 0
            failed_count = 0

            for recipient in recipients:
                try:
                    result = await self._send_to_recipient(broadcast, template, recipient)
                    if result:
                        sent_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"Error sending to recipient {recipient.get('telegram_id')}: {e}")
                    failed_count += 1

            # Update broadcast status
            broadcast.status = BroadcastStatus.COMPLETED.value
            broadcast.sent_count = sent_count
            broadcast.failed_count = failed_count
            broadcast.completed_at = datetime.utcnow()
            await self.db.session.commit()

            logger.info(f"Broadcast {broadcast_id} completed. Sent: {sent_count}, Failed: {failed_count}")

            return {
                'success': True,
                'total': len(recipients),
                'sent': sent_count,
                'failed': failed_count
            }

        except Exception as e:
            logger.error(f"Broadcast execution error: {e}")
            return {
                'success': False,
                'error': str(e),
                'total': 0,
                'sent': 0,
                'failed': 0
            }

    async def preview_broadcast(
        self,
        broadcast_id: int,
        sample_count: int = 3
    ) -> Dict[str, Any]:
        """
        Preview broadcast with sample recipients.

        Args:
            broadcast_id: Broadcast ID
            sample_count: Number of sample recipients

        Returns:
            Preview dictionary with sample rendered messages
        """
        try:
            broadcast = await self.db.get_broadcast_by_id(broadcast_id)
            template = await self.db.get_message_template(broadcast.template_id)

            recipients = await self.filter.get_recipients(broadcast.filters)
            sample_recipients = recipients[:sample_count]

            samples = []
            for recipient in sample_recipients:
                subject = self.renderer.render(template.subject, recipient)
                body_tg = self.renderer.render(template.body_telegram, recipient)
                body_email = self.renderer.render(template.body_email, recipient)

                samples.append({
                    'recipient': f"{recipient.get('first_name')} {recipient.get('last_name')}",
                    'subject': subject,
                    'body_telegram': body_tg,
                    'body_email': body_email
                })

            return {
                'success': True,
                'total_recipients': len(recipients),
                'sample_count': len(sample_recipients),
                'samples': samples
            }

        except Exception as e:
            logger.error(f"Preview error: {e}")
            return {
                'success': False,
                'error': str(e),
                'samples': []
            }

    async def _send_to_recipient(
        self,
        broadcast: Broadcast,
        template: MessageTemplate,
        recipient: Dict[str, Any]
    ) -> bool:
        """
        Send message to single recipient.

        Args:
            broadcast: Broadcast object
            template: MessageTemplate object
            recipient: Recipient data

        Returns:
            True if at least one channel succeeded
        """
        # Render templates
        subject = self.renderer.render(template.subject, recipient)
        body_tg = self.renderer.render(template.body_telegram, recipient)
        body_email = self.renderer.render(template.body_email, recipient)

        # Create recipient record
        recipient_record = BroadcastRecipient(
            broadcast_id=broadcast.id,
            user_id=recipient['id'],
            telegram_id=recipient['telegram_id'],
            email_address=recipient.get('email'),
            rendered_subject=subject,
            rendered_body=body_tg
        )

        # Send to channels in parallel
        tasks = []
        if broadcast.send_telegram:
            tasks.append(self.telegram_channel.send(recipient, subject, body_tg))
        if broadcast.send_email:
            tasks.append(self.email_channel.send(recipient, subject, body_email))

        if not tasks:
            return False

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Update recipient record with results
        if broadcast.send_telegram and len(results) > 0:
            result = results[0]
            if isinstance(result, DeliveryResult):
                recipient_record.telegram_status = result.status
                recipient_record.telegram_error = result.error
                if result.success:
                    recipient_record.telegram_sent_at = datetime.utcnow()

        if broadcast.send_email and len(results) > 1:
            result = results[1]
            if isinstance(result, DeliveryResult):
                recipient_record.email_status = result.status
                recipient_record.email_error = result.error
                if result.success:
                    recipient_record.email_sent_at = datetime.utcnow()

        # Save to database
        async with self.db.get_session() as session:
            session.add(recipient_record)
            await session.commit()

        # Return true if any channel succeeded
        for result in results:
            if isinstance(result, DeliveryResult) and result.success:
                return True

        return False
```

---

## 📄 Task #9: Update utils/database.py

Add these 6 methods to the `DatabaseManager` class:

```python
    async def create_message_template(
        self,
        name: str,
        subject: str,
        body_telegram: str,
        body_email: str,
        available_variables: Optional[Dict[str, str]] = None,
        created_by: Optional[int] = None
    ) -> MessageTemplate:
        """Create a new message template."""
        from models import MessageTemplate

        template = MessageTemplate(
            name=name,
            subject=subject,
            body_telegram=body_telegram,
            body_email=body_email,
            available_variables=available_variables or {},
            created_by=created_by
        )

        async with self.get_session() as session:
            session.add(template)
            await session.commit()
            await session.refresh(template)
            return template

    async def create_broadcast(
        self,
        name: str,
        template_id: int,
        filters: Dict[str, Any],
        send_telegram: bool = True,
        send_email: bool = True,
        created_by: Optional[int] = None
    ) -> Broadcast:
        """Create a new broadcast."""
        from models import Broadcast

        broadcast = Broadcast(
            name=name,
            template_id=template_id,
            filters=filters,
            send_telegram=send_telegram,
            send_email=send_email,
            created_by=created_by or 0
        )

        async with self.get_session() as session:
            session.add(broadcast)
            await session.commit()
            await session.refresh(broadcast)
            return broadcast

    async def get_broadcasts(
        self,
        status: Optional[str] = None
    ) -> List[Broadcast]:
        """Get all broadcasts, optionally filtered by status."""
        from models import Broadcast

        async with self.get_session() as session:
            query = select(Broadcast)
            if status:
                query = query.where(Broadcast.status == status)
            query = query.order_by(Broadcast.created_at.desc())

            result = await session.execute(query)
            return result.scalars().all()

    async def get_broadcast_by_id(self, broadcast_id: int) -> Optional[Broadcast]:
        """Get broadcast by ID."""
        from models import Broadcast

        async with self.get_session() as session:
            result = await session.execute(
                select(Broadcast).where(Broadcast.id == broadcast_id)
            )
            return result.scalar_one_or_none()

    async def get_broadcast_statistics(self, broadcast_id: int) -> Dict[str, Any]:
        """Get statistics for a broadcast."""
        from models import BroadcastRecipient
        from sqlalchemy import func

        async with self.get_session() as session:
            result = await session.execute(
                select(
                    func.count(BroadcastRecipient.id).label('total'),
                    func.sum(case(
                        (BroadcastRecipient.telegram_status == 'sent', 1),
                        else_=0
                    )).label('telegram_sent'),
                    func.sum(case(
                        (BroadcastRecipient.email_status == 'sent', 1),
                        else_=0
                    )).label('email_sent'),
                    func.sum(case(
                        (BroadcastRecipient.telegram_status == 'failed', 1),
                        else_=0
                    )).label('telegram_failed'),
                    func.sum(case(
                        (BroadcastRecipient.email_status == 'failed', 1),
                        else_=0
                    )).label('email_failed'),
                ).where(BroadcastRecipient.broadcast_id == broadcast_id)
            )

            row = result.one()
            return {
                'total': row.total or 0,
                'telegram_sent': row.telegram_sent or 0,
                'email_sent': row.email_sent or 0,
                'telegram_failed': row.telegram_failed or 0,
                'email_failed': row.email_failed or 0,
            }

    async def get_message_templates(self) -> List[MessageTemplate]:
        """Get all active message templates."""
        from models import MessageTemplate

        async with self.get_session() as session:
            result = await session.execute(
                select(MessageTemplate).where(MessageTemplate.is_active == True).order_by(MessageTemplate.name)
            )
            return result.scalars().all()

    async def get_message_template(self, template_id: int) -> Optional[MessageTemplate]:
        """Get message template by ID."""
        from models import MessageTemplate

        async with self.get_session() as session:
            result = await session.execute(
                select(MessageTemplate).where(MessageTemplate.id == template_id)
            )
            return result.scalar_one_or_none()
```

---

## 📄 Task #2 Update: .env.example

```bash
# SMTP Server Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=True

# Email Sender Information
EMAIL_FROM_ADDRESS=noreply@usn.example.com
EMAIL_FROM_NAME=USN Competitions
```

---

## 📄 Task #2 Update: requirements.txt

Add these lines:
```
aiosmtplib==3.0.1
jinja2==3.1.3
```

---

*Code Templates v1.0 - 2026-02-09*
