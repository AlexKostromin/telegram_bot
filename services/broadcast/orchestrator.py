from typing import Dict, Any, List, Optional, Tuple
import logging
import asyncio
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Broadcast, BroadcastRecipient, MessageTemplate, BroadcastStatus
from .channels import NotificationChannel, DeliveryResult
from .telegram_channel import TelegramChannel
from .email_channel import EmailChannel
from .template_renderer import TemplateRenderer
from .recipient_filter import RecipientFilter

logger = logging.getLogger(__name__)

class BroadcastOrchestrator:
    """
    Orchestrator for executing broadcast campaigns.

    Coordinates all components of the broadcast system:
    - Loads broadcast configuration and template
    - Filters target recipients
    - Renders templates for each recipient
    - Sends via notification channels (Telegram, Email)
    - Tracks delivery status
    - Provides statistics

    Uses Facade pattern to hide complexity from caller.

    Example:
        >>> from aiogram import Bot
        >>> bot = Bot(token='YOUR_TOKEN')
        >>> orchestrator = BroadcastOrchestrator(session, bot)
        >>> stats = await orchestrator.execute_broadcast(broadcast_id=1)
        >>> print(f"Sent: {stats['sent']}, Failed: {stats['failed']}")
    """

    def __init__(
        self,
        session: AsyncSession,
        bot=None,
    ):
        """
        Initialize orchestrator.

        Args:
            session: SQLAlchemy AsyncSession
            bot: aiogram Bot instance for Telegram sending
        """
        self.session = session
        self.bot = bot
        self.renderer = TemplateRenderer()
        self.recipient_filter = RecipientFilter(session)

        self.channels: Dict[str, NotificationChannel] = {}

        if bot:
            self.channels['telegram'] = TelegramChannel(bot)

        self.channels['email'] = EmailChannel()

    async def preview_broadcast(
        self,
        broadcast_id: int,
        sample_size: int = 5
    ) -> Dict[str, Any]:
        """
        Preview broadcast without sending.

        Args:
            broadcast_id: ID of broadcast to preview
            sample_size: Number of sample recipients to show

        Returns:
            Dictionary with broadcast info and sample renderings

        Example:
            >>> preview = await orchestrator.preview_broadcast(broadcast_id=1)
            >>> print(f"Targeting {preview['total_recipients']} users")
            >>> for sample in preview['samples']:
            ...     print(sample['rendered_subject'])
        """
        try:

            broadcast = await self._load_broadcast(broadcast_id)
            if not broadcast:
                return {'error': f'Broadcast {broadcast_id} not found'}

            template = broadcast.template

            total = await self.recipient_filter.count_recipients(**broadcast.filters)

            samples_data = await self.recipient_filter.get_recipients(
                limit=sample_size,
                **broadcast.filters
            )

            samples = []
            for recipient in samples_data:
                subject = self.renderer.render(template.subject, recipient)
                body_tg = self.renderer.render(template.body_telegram, recipient)
                body_email = self.renderer.render(template.body_email, recipient)

                samples.append({
                    'telegram_id': recipient['telegram_id'],
                    'email': recipient['email'],
                    'first_name': recipient['first_name'],
                    'rendered_subject': subject,
                    'rendered_body_telegram': body_tg,
                    'rendered_body_email': body_email,
                })

            return {
                'broadcast_id': broadcast.id,
                'name': broadcast.name,
                'template_name': template.name,
                'total_recipients': total,
                'filters': broadcast.filters,
                'send_telegram': broadcast.send_telegram,
                'send_email': broadcast.send_email,
                'samples': samples,
            }

        except Exception as e:
            logger.error(f"❌ Preview failed: {e}")
            return {'error': str(e)}

    async def execute_broadcast(
        self,
        broadcast_id: int,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Execute broadcast campaign.

        Main workflow:
        1. Load broadcast and template
        2. Get recipients matching filters
        3. Create BroadcastRecipient records
        4. Render templates for each recipient
        5. Send via enabled channels (parallel)
        6. Update delivery statuses
        7. Return statistics

        Args:
            broadcast_id: ID of broadcast to execute
            dry_run: If True, don't actually send (just preview)

        Returns:
            Dictionary with execution statistics

        Example:
            >>> stats = await orchestrator.execute_broadcast(broadcast_id=1)
            >>> print(f"Sent {stats['sent']} messages")
            >>> print(f"Failed {stats['failed']} messages")
        """
        try:

            broadcast = await self._load_broadcast(broadcast_id)
            if not broadcast:
                logger.error(f"❌ Broadcast {broadcast_id} not found")
                return {'error': f'Broadcast not found', 'broadcast_id': broadcast_id}

            template = broadcast.template
            logger.info(f"📢 Starting broadcast '{broadcast.name}' (template: {template.name})")

            if not dry_run:
                broadcast.status = BroadcastStatus.in_progress
                broadcast.started_at = datetime.utcnow()
                await self.session.merge(broadcast)
                await self.session.commit()

            recipients = await self.recipient_filter.get_recipients(**broadcast.filters)
            logger.info(f"📋 Found {len(recipients)} recipients")

            broadcast.total_recipients = len(recipients)

            if not recipients:
                logger.warning("⚠️  No recipients found for broadcast")
                if not dry_run:
                    broadcast.status = BroadcastStatus.completed
                    broadcast.completed_at = datetime.utcnow()
                    await self.session.merge(broadcast)
                    await self.session.commit()
                return {
                    'broadcast_id': broadcast.id,
                    'total_recipients': 0,
                    'sent': 0,
                    'failed': 0,
                    'error': 'No recipients found'
                }

            if not dry_run:
                for recipient in recipients:
                    broadcast_recipient = BroadcastRecipient(
                        broadcast_id=broadcast.id,
                        user_id=recipient['user_id'],
                        telegram_id=recipient['telegram_id'],
                        email_address=recipient['email'],
                    )
                    self.session.add(broadcast_recipient)

                await self.session.commit()
                logger.info(f"✅ Created {len(recipients)} BroadcastRecipient records")

            sent_count = 0
            failed_count = 0
            results = []

            for recipient in recipients:
                result = await self._send_to_recipient(
                    broadcast,
                    template,
                    recipient,
                    dry_run=dry_run
                )

                results.append(result)

                if result['success']:
                    sent_count += 1
                else:
                    failed_count += 1

            if not dry_run:
                broadcast.sent_count = sent_count
                broadcast.failed_count = failed_count
                broadcast.status = BroadcastStatus.completed
                broadcast.completed_at = datetime.utcnow()
                await self.session.merge(broadcast)
                await self.session.commit()

            logger.info(f"✅ Broadcast completed: {sent_count} sent, {failed_count} failed")

            return {
                'broadcast_id': broadcast.id,
                'total_recipients': len(recipients),
                'sent': sent_count,
                'failed': failed_count,
                'details': results,
            }

        except Exception as e:
            logger.error(f"❌ Broadcast execution failed: {e}")
            return {'error': str(e), 'broadcast_id': broadcast_id}

    async def _send_to_recipient(
        self,
        broadcast: Broadcast,
        template: MessageTemplate,
        recipient: Dict[str, Any],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Send message to single recipient via enabled channels.

        Sends in parallel to Telegram and Email (if enabled).
        Updates BroadcastRecipient records with delivery status.

        Args:
            broadcast: Broadcast object
            template: MessageTemplate object
            recipient: Recipient dictionary
            dry_run: If True, don't actually send

        Returns:
            Result dictionary with delivery status for each channel
        """

        try:
            subject = self.renderer.render(template.subject, recipient)
            body_telegram = self.renderer.render(template.body_telegram, recipient)
            body_email = self.renderer.render(template.body_email, recipient)
        except Exception as e:
            logger.error(f"❌ Template rendering failed for {recipient['user_id']}: {e}")
            return {
                'user_id': recipient['user_id'],
                'success': False,
                'error': f'Rendering failed: {str(e)}'
            }

        result = {
            'user_id': recipient['user_id'],
            'telegram_id': recipient['telegram_id'],
            'success': False,
            'channels': {},
        }

        if broadcast.send_telegram and self._channel_enabled('telegram'):
            if dry_run:
                result['channels']['telegram'] = {'status': 'simulated'}
            else:
                tg_result = await self._send_telegram(
                    recipient,
                    body_telegram,
                    broadcast.id
                )
                result['channels']['telegram'] = tg_result

        if broadcast.send_email and self._channel_enabled('email'):
            if dry_run:
                result['channels']['email'] = {'status': 'simulated'}
            else:
                email_result = await self._send_email(
                    recipient,
                    subject,
                    body_email,
                    broadcast.id
                )
                result['channels']['email'] = email_result

        result['success'] = any(
            ch.get('success', False)
            for ch in result['channels'].values()
        )

        return result

    async def _send_telegram(
        self,
        recipient: Dict[str, Any],
        body: str,
        broadcast_id: int
    ) -> Dict[str, Any]:
        """Send via Telegram channel and update database."""
        try:
            channel = self.channels.get('telegram')
            if not channel:
                return {'status': 'disabled'}

            delivery = await channel.send(recipient, '', body)

            if delivery.success:
                await self._update_recipient_status(
                    broadcast_id,
                    recipient['user_id'],
                    'telegram',
                    'sent',
                    message_id=delivery.message_id
                )
            else:
                await self._update_recipient_status(
                    broadcast_id,
                    recipient['user_id'],
                    'telegram',
                    delivery.status,
                    error=delivery.error
                )

            return {
                'success': delivery.success,
                'status': delivery.status,
                'error': delivery.error,
            }

        except Exception as e:
            logger.error(f"❌ Telegram send failed: {e}")
            return {
                'success': False,
                'status': 'failed',
                'error': str(e),
            }

    async def _send_email(
        self,
        recipient: Dict[str, Any],
        subject: str,
        body: str,
        broadcast_id: int
    ) -> Dict[str, Any]:
        """Send via Email channel and update database."""
        try:
            channel = self.channels.get('email')
            if not channel:
                return {'status': 'disabled'}

            delivery = await channel.send(recipient, subject, body)

            if delivery.success:
                await self._update_recipient_status(
                    broadcast_id,
                    recipient['user_id'],
                    'email',
                    'sent'
                )
            else:
                await self._update_recipient_status(
                    broadcast_id,
                    recipient['user_id'],
                    'email',
                    delivery.status,
                    error=delivery.error
                )

            return {
                'success': delivery.success,
                'status': delivery.status,
                'error': delivery.error,
            }

        except Exception as e:
            logger.error(f"❌ Email send failed: {e}")
            return {
                'success': False,
                'status': 'failed',
                'error': str(e),
            }

    def _channel_enabled(self, channel_name: str) -> bool:
        """Check if channel is available."""
        return channel_name in self.channels

    async def _load_broadcast(self, broadcast_id: int) -> Optional[Broadcast]:
        """Load broadcast with template from database."""
        result = await self.session.execute(
            select(Broadcast).where(Broadcast.id == broadcast_id)
        )
        return result.scalar()

    async def _update_recipient_status(
        self,
        broadcast_id: int,
        user_id: int,
        channel: str,
        status: str,
        message_id: Optional[str] = None,
        error: Optional[str] = None
    ):
        """Update BroadcastRecipient delivery status."""
        try:
            result = await self.session.execute(
                select(BroadcastRecipient).where(
                    (BroadcastRecipient.broadcast_id == broadcast_id) &
                    (BroadcastRecipient.user_id == user_id)
                )
            )
            recipient = result.scalar()

            if recipient:
                if channel == 'telegram':
                    recipient.telegram_status = status
                    recipient.telegram_sent_at = datetime.utcnow()
                    recipient.telegram_error = error
                    if message_id:
                        recipient.telegram_message_id = int(message_id)
                elif channel == 'email':
                    recipient.email_status = status
                    recipient.email_sent_at = datetime.utcnow()
                    recipient.email_error = error

                await self.session.merge(recipient)
                await self.session.commit()

        except Exception as e:
            logger.error(f"❌ Failed to update recipient status: {e}")

