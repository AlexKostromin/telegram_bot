# Broadcast System - Quick Reference Guide

**For Developers Implementing Tasks #1-13**

---

## 📌 At a Glance

| Task | File | Type | Lines | Time |
|------|------|------|-------|------|
| #1 | models/broadcast.py | Models | 150 | 1-2h |
| #1 | migrations/006_create_broadcast_tables.py | Migration | 100 | |
| #2 | config/email_settings.py | Config | 30 | 30m |
| #3 | services/broadcast/channels.py | Abstract | 40 | 1h |
| #4 | services/broadcast/telegram_channel.py | Channel | 120 | 1.5h |
| #5 | services/broadcast/email_channel.py | Channel | 140 | 1.5h |
| #6 | services/broadcast/template_renderer.py | Service | 100 | 1h |
| #7 | services/broadcast/recipient_filter.py | Service | 150 | 1.5h |
| #8 | services/broadcast/orchestrator.py | Orchestrator | 250 | 2h |
| #9 | utils/database.py | Extension | +50 | 1h |
| #10 | admin_panel/apps/BotDataApp/broadcast_models.py | Django | 80 | 1h |
| #11 | admin_panel/apps/BotDataApp/broadcast_admin.py | Admin | 200 | 2h |
| #12 | admin_panel/apps/BotDataApp/templates/admin/broadcast/ | HTML | 150 | 1.5h |
| #13 | (tests) | Testing | - | 2h |

**Total**: 1,370 lines of code, 16-17 hours work (with testing)

---

## 🎯 Core Concepts

### 1. Message Template
A reusable message with variables:
```python
template = MessageTemplate(
    name="Registration Confirmation",
    subject="Welcome to {{competition_name}}",
    body_telegram="Hi {{first_name}}, you're registered!",
    body_email="<html><p>Hi {{first_name}}</p></html>",
    available_variables={"first_name": "str", "competition_name": "str"}
)
```

### 2. Broadcast
A broadcast job targeting recipients:
```python
broadcast = Broadcast(
    name="Notify all players in Chess 2026",
    template_id=1,
    filters={"competition_ids": [1], "roles": ["player"]},
    send_telegram=True,
    send_email=True,
    status="draft"  # draft → in_progress → completed
)
```

### 3. Broadcast Recipients
Delivery tracking for each recipient:
```python
recipient = BroadcastRecipient(
    broadcast_id=1,
    user_id=123,
    telegram_id=987654321,
    email_address="user@example.com",
    telegram_status="sent",  # pending/sent/delivered/failed/blocked
    email_status="sent"
)
```

### 4. Delivery Result
Return value from channel send():
```python
result = DeliveryResult(
    success=True,
    status="sent",
    message_id="123456789",
    error=None,
    sent_at=datetime.utcnow()
)
```

---

## 🔧 Implementation Patterns

### Pattern: Abstract Channel
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class DeliveryResult:
    success: bool
    status: str
    message_id: Optional[str] = None
    error: Optional[str] = None

class NotificationChannel(ABC):
    @abstractmethod
    async def send(self, recipient: Dict[str, Any], subject: str, body: str) -> DeliveryResult:
        pass

    @abstractmethod
    async def validate_recipient(self, recipient: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def get_channel_name(self) -> str:
        pass
```

### Pattern: Concrete Channel Implementation
```python
class TelegramChannel(NotificationChannel):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send(self, recipient: Dict[str, Any], subject: str, body: str) -> DeliveryResult:
        try:
            message = await self.bot.send_message(
                chat_id=recipient['telegram_id'],
                text=body
            )
            return DeliveryResult(success=True, status="sent", message_id=message.message_id)
        except TelegramForbiddenError:
            return DeliveryResult(success=False, status="blocked", error="Bot blocked by user")
        except Exception as e:
            return DeliveryResult(success=False, status="failed", error=str(e))

    async def validate_recipient(self, recipient: Dict[str, Any]) -> bool:
        return 'telegram_id' in recipient and recipient['telegram_id'] > 0

    def get_channel_name(self) -> str:
        return "telegram"
```

### Pattern: Template Rendering
```python
from jinja2 import Template

class TemplateRenderer:
    DEFAULT_VARIABLES = {
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        # ... more variables
    }

    def render(self, template_text: str, variables: Dict[str, Any]) -> str:
        try:
            template = Template(template_text)
            return template.render(**variables)
        except Exception as e:
            logger.error(f"Template render error: {e}")
            raise

    def extract_variables(self, template_text: str) -> List[str]:
        import re
        # Find {{variable}} patterns
        return re.findall(r'\{\{\s*(\w+)\s*\}\}', template_text)
```

### Pattern: SQLAlchemy Query with JOIN
```python
async def get_recipients(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    async with self.session() as session:
        query = select(
            UserModel.id,
            UserModel.telegram_id,
            UserModel.email,
            UserModel.first_name,
            UserModel.last_name,
            CompetitionModel.name.label('competition_name'),
            RegistrationModel.role
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

        result = await session.execute(query)
        return [dict(row._mapping) for row in result.fetchall()]
```

### Pattern: Async SMTP Email
```python
import aiosmtplib
from email.mime.text import MIMEText

class EmailChannel(NotificationChannel):
    async def send(self, recipient: Dict[str, Any], subject: str, body: str) -> DeliveryResult:
        try:
            async with aiosmtplib.SMTP(hostname=self.config.SMTP_HOST, port=self.config.SMTP_PORT) as smtp:
                if self.config.SMTP_USE_TLS:
                    await smtp.starttls()

                await smtp.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)

                message = MIMEText(body, 'html')
                message['Subject'] = subject
                message['From'] = self.config.EMAIL_FROM_ADDRESS
                message['To'] = recipient['email']

                result = await smtp.send_message(message)
                return DeliveryResult(success=True, status="sent")
        except Exception as e:
            return DeliveryResult(success=False, status="failed", error=str(e))
```

---

## 📋 Database Operations

### Creating a Broadcast
```python
# In BroadcastOrchestrator.execute_broadcast():
async def execute_broadcast(self, broadcast_id: int) -> Dict[str, Any]:
    # 1. Load broadcast and template
    broadcast = await self.db.get_broadcast_by_id(broadcast_id)
    template = await self.db.get_message_template(broadcast.template_id)

    # 2. Get recipients
    recipients = await self.filter.get_recipients(broadcast.filters)

    # 3. Create recipient entries
    for recipient in recipients:
        broadcast_recipient = BroadcastRecipient(
            broadcast_id=broadcast_id,
            user_id=recipient['user_id'],
            telegram_id=recipient['telegram_id'],
            email_address=recipient['email']
        )
        await self.db.session.add(broadcast_recipient)

    # 4. Update broadcast status
    broadcast.status = 'in_progress'
    broadcast.total_recipients = len(recipients)
    broadcast.started_at = datetime.utcnow()
    await self.db.session.commit()

    # 5. Send messages
    # ... (more below)
```

### Sending in Parallel
```python
import asyncio

async def _send_to_channels(self, recipient: Dict, template: MessageTemplate) -> Tuple[DeliveryResult, DeliveryResult]:
    # Render templates for this recipient
    subject = self.renderer.render(template.subject, recipient)
    body_tg = self.renderer.render(template.body_telegram, recipient)
    body_email = self.renderer.render(template.body_email, recipient)

    # Send to both channels in parallel
    tasks = []
    if self.broadcast.send_telegram:
        tasks.append(self.telegram_channel.send(recipient, subject, body_tg))
    if self.broadcast.send_email:
        tasks.append(self.email_channel.send(recipient, subject, body_email))

    results = await asyncio.gather(*tasks)
    return results
```

---

## 🧪 Testing Checklist

### Unit Tests (Per Component)
- [ ] TemplateRenderer.render() with sample data
- [ ] TemplateRenderer.extract_variables() finds all {{var}} patterns
- [ ] RecipientFilter.get_recipients() returns correct data structure
- [ ] RecipientFilter applies filters correctly
- [ ] TelegramChannel.validate_recipient() checks telegram_id
- [ ] EmailChannel.validate_recipient() checks email format
- [ ] DeliveryResult dataclass initializes correctly

### Integration Tests
- [ ] BroadcastOrchestrator.preview_broadcast() returns sample data
- [ ] BroadcastOrchestrator.execute_broadcast() creates BroadcastRecipient rows
- [ ] Delivery statuses are tracked in database
- [ ] Error messages are saved on failure
- [ ] Broadcast status transitions: draft → in_progress → completed

### End-to-End Tests
- [ ] Create template in Django admin
- [ ] Create broadcast in Django admin
- [ ] Execute broadcast (if test SMTP configured)
- [ ] Verify email delivery (check spam folder)
- [ ] Verify Telegram delivery (check test bot)
- [ ] Check statistics in admin panel

### Error Scenarios
- [ ] User with blocked bot (telegram_status='blocked')
- [ ] Invalid email (email_status='failed')
- [ ] Template with undefined variable (graceful error)
- [ ] SMTP connection failure (error logged, status='failed')
- [ ] Rate limiting respected (0.05s between Telegram messages)

---

## 🚀 Quick Start Template

### Create MessageTemplate
```python
# In Django admin:
Name: "Chess 2026 Start Notification"
Subject: "🏁 {{competition_name}} starts tomorrow!"
Body Telegram: """
Привет, {{first_name}}! 👋

Соревнование {{competition_name}} начинается завтра!
Ваша роль: {{role}}
Статус: {{registration_status}}

С нетерпением ждем вас!
"""
Body Email: """
<html>
<body>
<p>Привет, {{first_name}} {{last_name}}!</p>
<p>Соревнование <strong>{{competition_name}}</strong> начинается завтра!</p>
<p>Ваша роль: {{role}}</p>
<p>Статус: {{registration_status}}</p>
<p>С нетерпением ждем вас!</p>
</body>
</html>
"""
```

### Create Broadcast
```python
# In Django admin:
Name: "Chess 2026 - All Players Notification"
Template: "Chess 2026 Start Notification"
Filters (JSON): {
  "competition_ids": [1],
  "roles": ["player"],
  "statuses": ["approved"]
}
Send Telegram: ✓
Send Email: ✓
```

### Execute
```python
# In Django admin action or button:
broadcast = Broadcast.objects.get(id=1)
orchestrator = BroadcastOrchestrator(db, bot, email_settings)
await orchestrator.execute_broadcast(broadcast.id)
```

---

## 📊 Database Query Examples

### Get All Pending Deliveries
```sql
SELECT * FROM broadcast_recipients
WHERE telegram_status='pending' OR email_status='pending'
ORDER BY created_at DESC;
```

### Broadcast Statistics
```sql
SELECT
  b.name,
  COUNT(*) as total,
  SUM(CASE WHEN br.telegram_status='sent' THEN 1 ELSE 0 END) as tg_sent,
  SUM(CASE WHEN br.email_status='sent' THEN 1 ELSE 0 END) as email_sent,
  b.status,
  b.started_at
FROM broadcasts b
LEFT JOIN broadcast_recipients br ON b.id = br.broadcast_id
GROUP BY b.id
ORDER BY b.created_at DESC;
```

### Failed Deliveries
```sql
SELECT
  br.broadcast_id,
  br.user_id,
  br.telegram_status,
  br.telegram_error,
  br.email_status,
  br.email_error
FROM broadcast_recipients br
WHERE br.telegram_status='failed' OR br.email_status='failed'
ORDER BY br.created_at DESC;
```

---

## 🔍 Debugging Tips

### Common Issues

**Template Variables Not Substituting**:
- Check template syntax: `{{variable}}` (with spaces inside)
- Verify variable exists in recipient dict
- Check for typos in variable names

**Email Not Sending**:
- Verify SMTP credentials in .env
- Check for firewall blocking SMTP port
- Look for TLS/SSL errors in logs
- Test with: `aiosmtplib` example script

**Telegram Messages Not Arriving**:
- Check if bot token is valid
- Verify telegram_id is correct (positive integer)
- Check if user hasn't blocked bot (status='blocked')
- Look for API rate limiting errors

**Slow Performance**:
- Add indexes to broadcast_recipients (broadcast_id, user_id)
- Use pagination for large broadcasts
- Consider Celery for async execution (Phase 2)

---

## 📚 File Dependencies

```
models/broadcast.py
├─ depends: models/user.py (Base, UserModel)
└─ depends: models/competition.py, models/registration.py

migrations/006_create_broadcast_tables.py
├─ depends: models/broadcast.py (table structure)
└─ runs: after migrations 001-005

config/email_settings.py
├─ depends: python-dotenv
└─ imported by: email_channel.py

services/broadcast/
├─ __init__.py (exports all)
├─ channels.py (ABC, DeliveryResult)
├─ telegram_channel.py (depends: aiogram, channels.py)
├─ email_channel.py (depends: aiosmtplib, config/email_settings.py, channels.py)
├─ template_renderer.py (depends: jinja2)
├─ recipient_filter.py (depends: sqlalchemy, models/)
└─ orchestrator.py (depends: all above)

utils/database.py
├─ add methods for: broadcast.py models
└─ called by: orchestrator.py

admin_panel/apps/BotDataApp/
├─ broadcast_models.py (Django ORM, managed=False)
├─ broadcast_admin.py (depends: broadcast_models.py, orchestrator.py)
└─ admin.py (register broadcast_admin.py)
```

---

## ✨ Pro Tips

1. **Use asyncio.gather()** for parallel channel sending
2. **Always validate recipients** before sending (check email format, telegram_id > 0)
3. **Log everything** - especially failures and duration
4. **Use transaction rollback** if any channel fails (optional)
5. **Rate limit Telegram** to avoid hitting API limits
6. **Cache template compilation** for repeated renders
7. **Index database** on frequently filtered columns
8. **Use connection pooling** for database and SMTP
9. **Monitor delivery rates** - alert if failure % too high
10. **Test with small batches** before full broadcast

---

*Quick Reference v1.0 - 2026-02-09*
