# Broadcast System Implementation Plan

**Status**: 🔵 PLANNING PHASE COMPLETE
**Created**: 2026-02-09
**Last Updated**: 2026-02-09

---

## 📋 Overview

This document outlines the complete implementation plan for the broadcast system - enabling mass messaging to competition participants through Telegram and Email with template variables, recipient filtering, and delivery tracking.

### Current State
- ✅ Core bot operational (registration, admin panel, database)
- ❌ Broadcast system: NOT IMPLEMENTED
- ❌ Email infrastructure: NOT CONFIGURED
- ✅ Django Admin Panel: READY FOR BROADCAST MODELS

### Goals
1. **Message Templates**: Create reusable templates with variable substitution ({{first_name}}, {{competition_name}}, etc.)
2. **Dual Delivery**: Send same message simultaneously to Telegram AND Email
3. **Smart Filtering**: Target specific users by competition, role, status, geography
4. **Delivery Tracking**: Monitor success/failure status for each recipient
5. **Admin Interface**: Full management through Django Admin Panel
6. **SOLID Architecture**: Clean, testable, maintainable code

---

## 📁 13-Task Implementation Roadmap

### Phase 1: Database Foundation (Task #1)
**Goal**: Create SQLAlchemy models and migration for broadcast tables

**Deliverables**:
- `models/broadcast.py` - 3 models (MessageTemplate, Broadcast, BroadcastRecipient)
- `migrations/006_create_broadcast_tables.py` - migration script
- Updated `models/__init__.py` - exports

**Output**: 3 tables created in SQLite with proper indexes

---

### Phase 2: Configuration (Task #2)
**Goal**: Set up SMTP and dependencies

**Deliverables**:
- `config/email_settings.py` - SMTP configuration
- Updated `.env.example` - 7 new variables
- Updated `requirements.txt` - 2 new packages

**Output**: SMTP settings available, dependencies installed

---

### Phase 3: Service Layer - Channels (Tasks #3-5)
**Goal**: Implement SOLID notification channels

**Deliverables**:
1. `services/broadcast/channels.py` - Abstract base (ABC)
   - DeliveryResult dataclass
   - NotificationChannel abstract class

2. `services/broadcast/telegram_channel.py` - Telegram implementation
   - TelegramChannel class
   - Rate limiting (0.05s between messages)
   - Error handling (blocked, bad request)

3. `services/broadcast/email_channel.py` - Email implementation
   - EmailChannel class
   - SMTP connection with TLS
   - HTML/plain text support
   - Error handling

**Output**: Two fully functional, interchangeable notification channels

---

### Phase 4: Service Layer - Core (Tasks #6-7)
**Goal**: Implement template rendering and recipient filtering

**Deliverables**:
1. `services/broadcast/template_renderer.py` - Jinja2 integration
   - DEFAULT_VARIABLES: 13+ substitution variables
   - Syntax validation
   - Variable extraction
   - Safe rendering with defaults

2. `services/broadcast/recipient_filter.py` - Database querying
   - 6 filter types (competition, roles, status, country, city, has_email)
   - SQLAlchemy JOIN queries (users + registrations)
   - Recipient data enrichment
   - Count and list operations

**Output**: Flexible template system + smart recipient selection

---

### Phase 5: Service Layer - Orchestration (Task #8)
**Goal**: Coordinate entire broadcast workflow

**Deliverables**:
- `services/broadcast/orchestrator.py` - BroadcastOrchestrator class
  - execute_broadcast() - main workflow
  - preview_broadcast() - safe preview
  - Error handling & logging
  - Parallel channel delivery
  - Status tracking

**Output**: Single entry point for all broadcast operations

---

### Phase 6: Database Extensions (Task #9)
**Goal**: Add broadcast methods to DatabaseManager

**Deliverables**:
- Updated `utils/database.py` with 6 methods:
  - create_message_template()
  - create_broadcast()
  - get_broadcasts()
  - get_broadcast_by_id()
  - get_broadcast_statistics()
  - get_message_templates()

**Output**: Full async database access for broadcasts

---

### Phase 7: Django Models (Task #10)
**Goal**: Create Django ORM wrappers for admin interface

**Deliverables**:
- `admin_panel/apps/BotDataApp/broadcast_models.py`
  - 3 Django models with managed=False
  - Status choices enums
  - __str__ methods

**Output**: Django-compatible ORM models for admin

---

### Phase 8: Django Admin Interface (Task #11)
**Goal**: Build complete admin control panel

**Deliverables**:
- `admin_panel/apps/BotDataApp/broadcast_admin.py`
  - MessageTemplateAdmin (create/edit templates)
  - BroadcastAdmin (create/manage broadcasts + actions)
  - BroadcastRecipientAdmin (view delivery tracking)
  - Custom actions: execute, cancel, test
  - Custom views: preview, execute_confirm, stats

**Output**: Full CRUD + execute/preview capabilities in Django admin

---

### Phase 9: HTML Templates (Task #12)
**Goal**: Create beautiful admin UI components

**Deliverables**:
- `preview_template.html` - Template preview with sample data
- `execute_confirm.html` - Confirmation dialog with stats
- `stats.html` - Live statistics and delivery tracking

**Output**: Professional admin interface for broadcasts

---

### Phase 10: Testing & Validation (Task #13)
**Goal**: Verify all components work together

**Test Scenarios**:
1. Database: Tables created, migration applied
2. Services: Each component tested independently
3. Integration: End-to-end broadcast execution
4. Error handling: Blocked users, invalid emails, template errors
5. Django admin: CRUD operations, actions, stats

**Output**: All green ✅ - System ready for production

---

## 🏗️ Architecture Overview

```
User (Django Admin)
    ↓
BroadcastAdmin (View)
    ↓
BroadcastOrchestrator (Facade)
    ↓
├─ TemplateRenderer (Jinja2)
├─ RecipientFilter (SQLAlchemy)
├─ TelegramChannel (aiogram)
└─ EmailChannel (aiosmtplib)
    ↓
Database (SQLite)
```

### Key SOLID Principles

**Single Responsibility**:
- TelegramChannel: Only Telegram logic
- EmailChannel: Only Email logic
- TemplateRenderer: Only template rendering
- RecipientFilter: Only database queries
- BroadcastOrchestrator: Only orchestration

**Open/Closed**:
- NotificationChannel ABC allows easy addition of SMS, Push, Slack, etc.
- Template variables expandable without code changes

**Liskov Substitution**:
- Both TelegramChannel and EmailChannel implement NotificationChannel interface
- Can be used interchangeably

**Interface Segregation**:
- Minimal interface: send(), validate_recipient(), get_channel_name()
- Clients don't depend on methods they don't use

**Dependency Inversion**:
- BroadcastOrchestrator depends on abstractions (NotificationChannel)
- Not on concrete implementations

---

## 📊 Database Schema

### message_templates
```
id INTEGER PRIMARY KEY
name VARCHAR(255) UNIQUE NOT NULL
description TEXT
subject VARCHAR(500) NOT NULL
body_telegram TEXT NOT NULL
body_email TEXT NOT NULL
available_variables JSON NOT NULL
is_active BOOLEAN DEFAULT 1
created_by INTEGER
created_at DATETIME
updated_at DATETIME
```

### broadcasts
```
id INTEGER PRIMARY KEY
name VARCHAR(255) NOT NULL
template_id INTEGER NOT NULL
filters JSON NOT NULL
send_telegram BOOLEAN DEFAULT 1
send_email BOOLEAN DEFAULT 1
scheduled_at DATETIME
status VARCHAR(20) DEFAULT 'draft'
total_recipients INTEGER DEFAULT 0
sent_count INTEGER DEFAULT 0
failed_count INTEGER DEFAULT 0
started_at DATETIME
completed_at DATETIME
created_by INTEGER NOT NULL
created_at DATETIME
updated_at DATETIME
FOREIGN KEY (template_id) REFERENCES message_templates(id)
```

### broadcast_recipients
```
id INTEGER PRIMARY KEY
broadcast_id INTEGER NOT NULL
user_id INTEGER NOT NULL
telegram_id BIGINT NOT NULL
telegram_status VARCHAR(20) DEFAULT 'pending'
telegram_sent_at DATETIME
telegram_error TEXT
telegram_message_id INTEGER
email_status VARCHAR(20) DEFAULT 'pending'
email_sent_at DATETIME
email_error TEXT
email_address VARCHAR(255)
rendered_subject VARCHAR(500)
rendered_body TEXT
created_at DATETIME
updated_at DATETIME
FOREIGN KEY (broadcast_id) REFERENCES broadcasts(id)
FOREIGN KEY (user_id) REFERENCES users(id)
```

---

## 🔤 Template Variables Reference

Available for substitution in all templates:

| Variable | Type | Example |
|----------|------|---------|
| first_name | str | John |
| last_name | str | Doe |
| email | str | john@example.com |
| phone | str | +7-999-123-4567 |
| country | str | Russia |
| city | str | Moscow |
| club | str | Chess Club #1 |
| company | str | Google |
| position | str | Senior Manager |
| competition_name | str | World Chess Championship |
| role | str | player |
| registration_status | str | approved |
| telegram_username | str | @johndoe |

**Example Template**:
```
Привет, {{first_name}} {{last_name}}! 👋

Вы зарегистрированы на {{competition_name}} в роли {{role}}.
Статус: {{registration_status}}

С уважением,
Команда USN
```

---

## 🎯 Recipient Filter Examples

**All players in competition #1**:
```json
{
  "competition_ids": [1],
  "roles": ["player"]
}
```

**All approved voters**:
```json
{
  "roles": ["voter"],
  "statuses": ["approved"]
}
```

**All Russian participants with email**:
```json
{
  "countries": ["Russia"],
  "has_email": true
}
```

**Multiple competitions, specific roles**:
```json
{
  "competition_ids": [1, 2, 3],
  "roles": ["player", "voter"],
  "statuses": ["approved"]
}
```

---

## 🔐 Configuration

Add to `.env`:

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

### For Gmail:
1. Enable 2-Factor Authentication
2. Create "App Password" at https://myaccount.google.com/apppasswords
3. Use App Password (not regular password) in SMTP_PASSWORD

### For Yandex:
```bash
SMTP_HOST=smtp.yandex.ru
SMTP_PORT=587
SMTP_USE_TLS=True
```

---

## ✅ Verification Checklist

### Database ✅
- [ ] message_templates table created
- [ ] broadcasts table created
- [ ] broadcast_recipients table created
- [ ] Migration 006 executed successfully
- [ ] Indexes created

### Services ✅
- [ ] All 7 Python modules created
- [ ] Full type annotations in place
- [ ] No import errors
- [ ] Unit tests passing (if applicable)

### Integration ✅
- [ ] Django models registered
- [ ] Admin interface functional
- [ ] Can create message template
- [ ] Can create broadcast
- [ ] Can view statistics
- [ ] Can execute broadcast

### Functionality ✅
- [ ] Telegram messages delivered
- [ ] Email messages delivered
- [ ] Template variables substituted correctly
- [ ] Recipient filtering working
- [ ] Delivery statuses tracked
- [ ] Error handling graceful

### Code Quality ✅
- [ ] All types annotated
- [ ] SOLID principles applied
- [ ] Logging configured
- [ ] No code duplication
- [ ] Docstrings complete

---

## 📈 Future Enhancements (Phase 2)

1. **Celery Integration** - Async execution with retry logic
2. **Email Webhooks** - SendGrid/Mailgun delivery tracking
3. **A/B Testing** - Multiple template variants
4. **Rich Media** - Attachments, images, inline buttons
5. **UI Builder** - Visual filter editor instead of JSON
6. **Scheduled Broadcasts** - Cron-based scheduling
7. **Analytics** - Click tracking, engagement metrics

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- SQLite3
- Django 4.2.8+
- aiogram 3.4.1+

### Dependencies
```bash
pip install aiosmtplib==3.0.1 jinja2==3.1.3
```

### Step-by-Step Execution
1. Follow Task #1 through #13 in order
2. Run database migrations
3. Configure SMTP in .env
4. Create test template in Django admin
5. Create test broadcast with sample filters
6. Execute broadcast
7. Verify delivery in logs and database

---

## 📞 Support & Documentation

- **Database Schema**: See schema diagrams above
- **Template Variables**: See reference table
- **Recipient Filters**: See filter examples
- **Error Handling**: Check orchestrator.py logs
- **Admin Interface**: Built-in Django admin help

---

## 📝 Files Summary

**New Files** (16):
- models/broadcast.py
- migrations/006_create_broadcast_tables.py
- config/email_settings.py
- services/broadcast/__init__.py, channels.py, telegram_channel.py, email_channel.py, template_renderer.py, recipient_filter.py, orchestrator.py
- admin_panel/apps/BotDataApp/broadcast_models.py, broadcast_admin.py
- admin_panel/apps/BotDataApp/templates/admin/broadcast/preview_template.html, execute_confirm.html, stats.html

**Modified Files** (4):
- models/__init__.py
- utils/database.py
- admin_panel/apps/BotDataApp/admin.py
- .env.example, requirements.txt

---

## 🎓 Learning Resources

- **SQLAlchemy Async**: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **Jinja2 Templates**: https://jinja.palletsprojects.com/
- **aiosmtplib**: https://aiosmtplib.readthedocs.io/
- **aiogram**: https://docs.aiogram.dev/
- **SOLID Principles**: https://en.wikipedia.org/wiki/SOLID

---

**Implementation Status**: 🟦 Ready to Start
**Estimated Duration**: 8-10 hours
**Complexity**: High (architecture + integration)
**Risk Level**: Low (isolated from existing code)

---

*Last Updated: 2026-02-09 by Claude Code*
