# 📧 Email Configuration Guide

## Email потоки в системе

```
┌─────────────────────────────────────────────────────────────────┐
│                    EMAIL FLOWS                                   │
└─────────────────────────────────────────────────────────────────┘

1️⃣  ИСХОДЯЩИЕ (Notifications)
   ┌──────────────────────┐
   │   Система USN        │
   │   (FROM: noreply@)   │
   │        ↓             │
   │   USER EMAIL         │  ← Уведомления, подтверждения
   └──────────────────────┘

2️⃣  ВХОДЯЩИЕ (Support Messages)
   ┌──────────────────────┐
   │   USER EMAIL         │
   │   (Пишет в боте)     │
   │        ↓             │
   │ SUPPORT EMAIL        │  ← Сообщения в поддержку
   │ (support@example.com)│
   └──────────────────────┘
```

---

## 🔧 Где что настраивается?

### 1. ИСХОДЯЩИЕ СООБЩЕНИЯ (Notifications)

**Почта ОТ которой отправляются:**

```
.env файл:
─────────────────────────────────────
EMAIL_FROM_ADDRESS=noreply@usn.example.com
EMAIL_FROM_NAME=USN Competitions
─────────────────────────────────────

Это почта ОТПРАВИТЕЛЯ для:
✅ Уведомлений об одобрении регистрации
✅ Приглашений на соревнования
✅ Объявлений и напоминаний
✅ Сообщений администратора
```

**Где используется в коде:**

```python
# utils/notifications.py - строка ~60-70
EMAIL_FROM = os.getenv('EMAIL_FROM_ADDRESS', 'noreply@example.com')

message['From'] = EMAIL_FROM  # Используется здесь
```

---

### 2. ВХОДЯЩИЕ СООБЩЕНИЯ (Support)

**Почта НА которую приходят сообщения поддержки:**

```
.env файл:
─────────────────────────────────────
SUPPORT_EMAIL=support@usn.example.com
SUPPORT_TELEGRAM_ID=123456789  (или Telegram ID админа)
─────────────────────────────────────

Это почта ПОЛУЧАТЕЛЯ для сообщений поддержки от пользователей
```

**Где используется в коде:**

```python
# handlers/support.py (нужно создать)
SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL')

# Когда пользователь пишет в поддержку:
await send_email_to_support(
    user_email=user.email,
    user_name=user.first_name,
    message=support_message,
    to_address=SUPPORT_EMAIL  # ← На этот адрес приходит
)
```

---

## 📋 Полный пример .env

```bash
# ==========================================
# EMAIL CONFIGURATION
# ==========================================

# SMTP Server (где отправляем ИЗ)
SMTP_HOST=smtp.mailtrap.io
SMTP_PORT=587
SMTP_USERNAME=your_mailtrap_username
SMTP_PASSWORD=your_mailtrap_password
SMTP_USE_TLS=True

# Исходящие уведомления (система → пользователь)
EMAIL_FROM_ADDRESS=noreply@usn.example.com
EMAIL_FROM_NAME=USN Competitions

# Входящие сообщения поддержки (пользователь → поддержка)
SUPPORT_EMAIL=support@usn.example.com
SUPPORT_TELEGRAM_ID=123456789
```

---

## 🎯 Практический пример

### Сценарий 1: Система отправляет уведомление пользователю

```
1. Администратор в Django Admin выбирает пользователей
2. Нажимает Action: "Отправить в Telegram + Email"
3. Система отправляет EMAIL:
   ├─ FROM: noreply@usn.example.com (из EMAIL_FROM_ADDRESS)
   ├─ TO: user.email (из базы данных)
   ├─ SUBJECT: ВАЖНОЕ УВЕДОМЛЕНИЕ...
   └─ BODY: Текст уведомления
```

**Файлы:**
- `utils/notifications.py` - функция `send_email()`
- `admin_panel/apps/BotDataApp/admin.py` - action `send_notification_action()`

---

### Сценарий 2: Пользователь пишет в поддержку

```
1. Пользователь в Telegram боте:
   /start → меню → "Связаться с поддержкой"

2. Пишет свое сообщение

3. Система отправляет EMAIL АДМИНИСТРАТОРУ:
   ├─ FROM: noreply@usn.example.com (из EMAIL_FROM_ADDRESS)
   ├─ TO: support@usn.example.com (из SUPPORT_EMAIL)
   ├─ SUBJECT: 📬 Новое сообщение от {user.name}
   └─ BODY: Текст сообщения + контакты пользователя

4. ИЛИ отправляет в Telegram админам:
   └─ SUPPORT_TELEGRAM_ID (приватное сообщение)
```

**Файлы (НУЖНО СОЗДАТЬ):**
- `handlers/support.py` - обработчик сообщений поддержки
- Новая команда/кнопка в боте

---

## 🔌 Как подключить поддержку

### Шаг 1: Добавить в .env

```bash
SUPPORT_EMAIL=support@usn.example.com
SUPPORT_TELEGRAM_ID=123456789  # Твой ID в Telegram
```

### Шаг 2: Создать функцию отправки в поддержку

```python
# utils/notifications.py

async def send_support_message(
    user_email: str,
    user_name: str,
    message_text: str,
    phone: Optional[str] = None
) -> None:
    """Send user message to support team."""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL')

    if not SUPPORT_EMAIL:
        logger.warning("SUPPORT_EMAIL not configured")
        return

    html_body = f"""
    <html>
    <body>
        <h2>📬 Новое сообщение от пользователя</h2>
        <p><strong>От:</strong> {user_name}</p>
        <p><strong>Email:</strong> {user_email}</p>
        {f'<p><strong>Телефон:</strong> {phone}</p>' if phone else ''}

        <hr>
        <h3>Сообщение:</h3>
        <p>{message_text}</p>
    </body>
    </html>
    """

    await send_email(
        email_address=SUPPORT_EMAIL,
        subject=f"📬 Сообщение от {user_name}",
        body=html_body
    )

    logger.info(f"✅ Support message from {user_name} sent to {SUPPORT_EMAIL}")
```

### Шаг 3: Добавить обработчик в бота

```python
# handlers/support.py

from aiogram import Router, F
from aiogram.types import Message
from utils.notifications import send_support_message

support_router = Router()

@support_router.message(F.text.contains("support"))
async def handle_support_message(message: Message):
    """Handle user support request."""
    user = message.from_user

    # Получить email и сообщение
    email = message.text.split("email:")[1].strip() if "email:" in message.text else ""
    support_text = message.text

    # Отправить в поддержку
    await send_support_message(
        user_email=email,
        user_name=user.first_name,
        message_text=support_text,
        phone=user.phone_number
    )

    await message.answer("✅ Ваше сообщение отправлено в поддержку!")
```

---

## 🎨 Таблица всех Email адресов

| Тип | Адрес | Переменная | Назначение |
|-----|-------|-----------|-----------|
| **FROM** (Исходящая) | noreply@usn.example.com | EMAIL_FROM_ADDRESS | Система отправляет уведомления |
| **TO** (Входящая поддержка) | support@usn.example.com | SUPPORT_EMAIL | Сообщения ОТ пользователей |
| **CC** (Копия) | admin@usn.example.com | ADMIN_EMAIL (опц.) | Копия для администратора |
| **Пользователя** | user@example.com | user.email | Адрес из БД пользователя |

---

## 📊 Конфигурация по сценариям

### Вариант A: Простой (только Telegram для поддержки)

```env
# Только исходящие уведомления на email
EMAIL_FROM_ADDRESS=noreply@usn.example.com
SUPPORT_TELEGRAM_ID=123456789  # Сообщения идут в Telegram
```

### Вариант B: Полный (Email и Telegram)

```env
# Исходящие уведомления
EMAIL_FROM_ADDRESS=noreply@usn.example.com

# Входящая поддержка
SUPPORT_EMAIL=support@usn.example.com
SUPPORT_TELEGRAM_ID=123456789  # И в Telegram тоже
```

### Вариант C:企业 (Разные адреса)

```env
# Исходящие
NOTIFICATIONS_EMAIL=notifications@usn.example.com
NOTIFICATIONS_NAME=USN Notifications

# Входящие
SUPPORT_EMAIL=support@usn.example.com
BILLING_EMAIL=billing@usn.example.com
ADMIN_EMAIL=admin@usn.example.com
```

---

## 🔒 Безопасность

### ✅ Правильно:
```bash
# .env - НИКОГДА не коммитить в Git
SMTP_PASSWORD=secret_app_password
EMAIL_FROM_ADDRESS=noreply@usn.example.com
```

### ❌ НЕПРАВИЛЬНО:
```python
# НИКОГДА не писать в коде
SMTP_PASSWORD = "secret_password"  # ← ОПАСНО!
```

---

## 🧪 Тест Email конфигурации

### Проверить FROM адрес:

```bash
grep "EMAIL_FROM" .env
```

```output
EMAIL_FROM_ADDRESS=noreply@usn.example.com
EMAIL_FROM_NAME=USN Competitions
```

### Проверить SUPPORT адреса:

```bash
grep "SUPPORT" .env
```

```output
SUPPORT_EMAIL=support@usn.example.com
SUPPORT_TELEGRAM_ID=123456789
```

### Отправить тестовое письмо:

```python
import asyncio
from utils.notifications import send_email

async def test():
    await send_email(
        email_address="test@example.com",
        subject="🧪 Test Email",
        body="<p>Это тестовое письмо</p>"
    )

asyncio.run(test())
```

---

## 📚 Файлы для редактирования

| Файл | Что менять | Зачем |
|------|-----------|-------|
| `.env` | EMAIL_FROM_ADDRESS | Адрес отправителя |
| `.env` | SUPPORT_EMAIL | Адрес поддержки |
| `.env` | SUPPORT_TELEGRAM_ID | ID админа в Telegram |
| `utils/notifications.py` | send_email() | Добавить функции |
| `handlers/support.py` | (создать новый) | Обработчик поддержки |
| `admin_panel/.../admin.py` | send_notification_action | Уже готово ✅ |

---

## 🚀 Быстрая настройка

```bash
# 1. Отредактируй .env
nano .env

# Добавь/замени:
EMAIL_FROM_ADDRESS=noreply@usn.example.com
SUPPORT_EMAIL=support@usn.example.com
SUPPORT_TELEGRAM_ID=<твой_telegram_id>

# 2. Сохрани (Ctrl+X, y, Enter)

# 3. Готово! ✅
```

---

## 📞 Поддержка

Если у тебя есть вопросы:

1. **Где в коде используется email?**
   - `utils/notifications.py` - основной модуль
   - `admin_panel/.../admin.py` - action для рассылок

2. **Как изменить адрес отправителя?**
   - Отредактируй `EMAIL_FROM_ADDRESS` в `.env`

3. **Как настроить входящую почту поддержки?**
   - Добавь `SUPPORT_EMAIL` в `.env`
   - Создай обработчик в `handlers/support.py`

4. **Как отправить письмо в тесте?**
   ```python
   await send_email(
       email_address="recipient@example.com",
       subject="Test",
       body="<p>Test message</p>"
   )
   ```

---

**Last Updated:** 2026-02-09
**Status:** ✅ Ready for configuration
