# 💬 Реализация Support в Telegram боте

## Как добавить функцию "Связаться с поддержкой"

---!

## 📋 Шаг 1: Создать обработчик поддержки

Создай файл: `handlers/support.py`

```python
"""
Support system for user inquiries.
"""
from typing import Optional
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
import logging

from utils import db_manager
from utils.notifications import send_support_message, send_email
from models import UserModel
from sqlalchemy import select

logger = logging.getLogger(__name__)

support_router = Router()


class SupportStates(StatesGroup):
    """FSM states for support request."""
    waiting_for_message = State()
    waiting_for_email = State()
    waiting_for_phone = State()


@support_router.message(Command("support"))
@support_router.message(F.text.contains("Поддержка"))
async def support_start(message: types.Message, state: FSMContext):
    """Start support request."""
    await state.set_state(SupportStates.waiting_for_message)

    reply_markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "📧 Напишите ваше сообщение для поддержки:\n\n"
        "(Опишите проблему как можно подробнее)",
        reply_markup=reply_markup
    )


@support_router.message(SupportStates.waiting_for_message)
async def support_message_received(message: types.Message, state: FSMContext):
    """Get support message from user."""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено")
        return

    # Сохрани сообщение
    await state.update_data(support_message=message.text)

    # Получи email пользователя из БД
    user = await db_manager.get_user_by_telegram_id(message.from_user.id)

    if user and user.email:
        # У пользователя уже есть email
        await send_support_email(message, state, user)
    else:
        # Попроси ввести email
        await state.set_state(SupportStates.waiting_for_email)
        await message.answer(
            "📧 На какой email вам отправить ответ?",
            reply_markup=types.ReplyKeyboardMarkup(
                keyboard=[[types.KeyboardButton(text="❌ Отмена")]],
                resize_keyboard=True
            )
        )


@support_router.message(SupportStates.waiting_for_email)
async def support_email_received(message: types.Message, state: FSMContext):
    """Get email from user."""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено")
        return

    # Валидировать email
    if "@" not in message.text or "." not in message.text:
        await message.answer("❌ Некорректный email. Пожалуйста, попробуйте еще раз.")
        return

    await state.update_data(email=message.text)

    # Создать временный объект пользователя с email
    user_data = await state.get_data()
    user = type('User', (), {
        'first_name': message.from_user.first_name or 'Аноним',
        'last_name': message.from_user.last_name or '',
        'email': message.text,
        'phone': None
    })()

    await send_support_email(message, state, user)


async def send_support_email(
    message: types.Message,
    state: FSMContext,
    user
) -> None:
    """Send support message to support email."""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL')
    SUPPORT_TELEGRAM_ID = int(os.getenv('SUPPORT_TELEGRAM_ID', 0))

    data = await state.get_data()
    support_message = data.get('support_message', '')
    user_email = user.email

    user_name = f"{user.first_name} {user.last_name}".strip()

    try:
        # Отправить по email
        if SUPPORT_EMAIL:
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2>📬 Новое сообщение от пользователя</h2>

                <h3>Данные пользователя:</h3>
                <ul>
                    <li><strong>Имя:</strong> {user_name}</li>
                    <li><strong>Email:</strong> {user_email}</li>
                    <li><strong>Telegram ID:</strong> {message.from_user.id}</li>
                    <li><strong>Telegram:</strong> @{message.from_user.username or 'не указан'}</li>
                </ul>

                <hr>

                <h3>Сообщение:</h3>
                <p style="background: #f5f5f5; padding: 10px; border-left: 4px solid #007bff;">
                    {support_message.replace(chr(10), '<br>')}
                </p>

                <hr>
                <p style="color: #999; font-size: 12px;">
                    Отправлено: {message.date.strftime('%d.%m.%Y %H:%M:%S UTC')}
                </p>
            </body>
            </html>
            """

            await send_email(
                email_address=SUPPORT_EMAIL,
                subject=f"📬 Сообщение от {user_name}",
                body=html_body
            )

            logger.info(f"✅ Support email sent to {SUPPORT_EMAIL}")

        # Отправить в Telegram админам
        if SUPPORT_TELEGRAM_ID:
            tg_message = f"""
📬 <b>НОВОЕ СООБЩЕНИЕ В ПОДДЕРЖКУ</b>

👤 <b>От:</b> {user_name}
📧 <b>Email:</b> {user_email}
🆔 <b>Telegram ID:</b> {message.from_user.id}
📱 <b>Username:</b> @{message.from_user.username or 'не указан'}

━━━━━━━━━━━━━━━━━━━━━
💬 <b>Сообщение:</b>

{support_message}
━━━━━━━━━━━━━━━━━━━━━

⏰ {message.date.strftime('%d.%m.%Y %H:%M:%S')}
            """.strip()

            # Получить bot из контекста
            from aiogram import Bot
            from config import BOT_TOKEN

            bot = Bot(token=BOT_TOKEN)
            try:
                await bot.send_message(
                    chat_id=SUPPORT_TELEGRAM_ID,
                    text=tg_message
                )
                logger.info(f"✅ Support message sent to Telegram {SUPPORT_TELEGRAM_ID}")
            finally:
                await bot.session.close()

        # Подтверждение пользователю
        await message.answer(
            "✅ Спасибо! Ваше сообщение отправлено в поддержку.\n\n"
            "Мы ответим вам на указанный email как можно скорее.",
            reply_markup=types.ReplyKeyboardRemove()
        )

        await state.clear()

    except Exception as e:
        logger.error(f"❌ Error sending support message: {e}")
        await message.answer(
            "❌ Ошибка при отправке сообщения. Пожалуйста, попробуйте позже.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.clear()
```

---

## 📋 Шаг 2: Обновить файл `utils/notifications.py`

Добавить функцию (если её еще нет):

```python
async def send_support_message(
    user_email: str,
    user_name: str,
    message_text: str,
    phone: Optional[str] = None
) -> None:
    """Send user message to support team.

    Args:
        user_email: Email пользователя (для ответа)
        user_name: Имя пользователя
        message_text: Текст сообщения
        phone: Номер телефона (опционально)
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()

    SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL')

    if not SUPPORT_EMAIL:
        logger.warning("⚠️  SUPPORT_EMAIL not configured in .env")
        return

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>📬 Новое сообщение от пользователя</h2>

        <p><strong>От:</strong> {user_name}</p>
        <p><strong>Email:</strong> {user_email}</p>
        {f'<p><strong>Телефон:</strong> {phone}</p>' if phone else ''}

        <hr>

        <h3>Сообщение:</h3>
        <p style="background: #f5f5f5; padding: 10px; border-left: 4px solid #0066cc;">
            {message_text.replace(chr(10), '<br>')}
        </p>
    </body>
    </html>
    """

    try:
        await send_email(
            email_address=SUPPORT_EMAIL,
            subject=f"📬 Сообщение от {user_name}",
            body=html_body
        )
        logger.info(f"✅ Support message from {user_name} sent to {SUPPORT_EMAIL}")
    except Exception as e:
        logger.error(f"❌ Error sending support message: {e}")
        raise
```

---

## 🎯 Шаг 3: Зарегистрировать router в боте

Обновить файл `handlers/__init__.py`:

```python
"""
Handlers module.
"""
from .start import start_router
from .registration import registration_router
from .menu import menu_router
from .contact import contact_router
from .admin import admin_router
from .support import support_router  # ← ДОБАВИТЬ ЭТУ СТРОКУ

__all__ = [
    "start_router",
    "registration_router",
    "menu_router",
    "contact_router",
    "admin_router",
    "support_router",  # ← И ЭТУ
]
```

Обновить файл `bot.py`:

```python
# В функции main() после регистрации других роутеров:

dp.include_router(start_router)
dp.include_router(menu_router)
dp.include_router(contact_router)
dp.include_router(registration_router)
dp.include_router(admin_router)
dp.include_router(support_router)  # ← ДОБАВИТЬ
```

---

## 🎯 Шаг 4: Добавить кнопку в меню

Обновить файл `messages/texts.py`:

```python
class BotMessages:
    # ... существующие сообщения ...

    START_MENU = """
👋 Добро пожаловать в USN Competitions Bot!

Выберите действие:
    """

    # Кнопки меню
    MENU_BUTTONS = {
        'register': '📝 Зарегистрироваться',
        'my_registrations': '📋 Мои регистрации',
        'support': '💬 Связаться с поддержкой',  # ← ДОБАВИТЬ
        'admin': '⚙️ Администратор',
    }
```

Обновить файл `keyboards/inline.py`:

```python
def main_menu_keyboard():
    """Main menu keyboard."""
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="📝 Зарегистрироваться", callback_data="register"),
        InlineKeyboardButton(text="📋 Мои регистрации", callback_data="my_registrations"),
    ).row(
        InlineKeyboardButton(text="💬 Поддержка", callback_data="support"),  # ← ДОБАВИТЬ
        InlineKeyboardButton(text="⚙️ Админ", callback_data="admin"),
    ).as_markup()
```

---

## 📋 Шаг 5: Обновить .env

```bash
# Support configuration
SUPPORT_EMAIL=support@usn.example.com
SUPPORT_TELEGRAM_ID=123456789  # Твой Telegram ID
```

---

## 🧪 Как это работает

### Сценарий 1: Пользователь с зарегистрированным email

```
1. Пользователь: /support
2. Бот: "Напишите ваше сообщение"
3. Пользователь: "У меня проблема с регистрацией"
4. Бот: ✅ Отправляет email на support@usn.example.com
         + Отправляет в Telegram админу (SUPPORT_TELEGRAM_ID)
5. Админ: Получает письмо И сообщение в Telegram
```

### Сценарий 2: Новый пользователь без email

```
1. Пользователь: /support
2. Бот: "Напишите сообщение"
3. Пользователь: "Вопрос по регистрации"
4. Бот: "На какой email отправить ответ?"
5. Пользователь: "my@email.com"
6. Бот: ✅ Отправляет email на support@usn.example.com
         + Отправляет в Telegram админу
```

---

## 📊 Что приходит админу

### По EMAIL (support@usn.example.com):

```
Subject: 📬 Сообщение от John Doe

──────────────────────

Данные пользователя:
• Имя: John Doe
• Email: john@example.com
• Telegram ID: 987654321
• Username: @johndoe

──────────────────────

Сообщение:

У меня проблема с регистрацией на соревнование.
Заявка не подтверждается уже 3 дня.
Помогите пожалуйста!

──────────────────────
Отправлено: 09.02.2026 11:50:00 UTC
```

### В TELEGRAM (SUPPORT_TELEGRAM_ID):

```
📬 НОВОЕ СООБЩЕНИЕ В ПОДДЕРЖКУ

👤 От: John Doe
📧 Email: john@example.com
🆔 Telegram ID: 987654321
📱 Username: @johndoe

━━━━━━━━━━━━━━━━━━━━━
💬 Сообщение:

У меня проблема с регистрацией на соревнование.
Заявка не подтверждается уже 3 дня.
Помогите пожалуйста!
━━━━━━━━━━━━━━━━━━━━━

⏰ 09.02.2026 11:50:00
```

---

## 🔐 Безопасность

✅ **Правильно:**
```python
SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL')  # Из .env
```

❌ **НЕПРАВИЛЬНО:**
```python
SUPPORT_EMAIL = "support@example.com"  # Хардкод!
```

---

## 📞 Если что-то не работает

### Проблема: Email не приходит

**Решение:**
1. Проверь `.env`:
   ```bash
   grep SUPPORT_EMAIL .env
   ```
2. Проверь SMTP конфигурацию
3. Смотри логи: `tail -f bot.log`

### Проблема: Telegram не приходит

**Решение:**
1. Проверь SUPPORT_TELEGRAM_ID:
   ```bash
   grep SUPPORT_TELEGRAM_ID .env
   ```
2. Убедись что это твой реальный Telegram ID (число!)
3. Проверь логи бота

### Проблема: Статус 500 в админке

**Решение:**
1. Проверь что импорты правильные
2. Проверь что функции добавлены в notifications.py
3. Проверь логи: `tail -f admin_panel/admin.log`

---

## 📝 Готовый Checklist

- [ ] Создать `handlers/support.py`
- [ ] Обновить `handlers/__init__.py`
- [ ] Обновить `bot.py` - добавить support_router
- [ ] Обновить `messages/texts.py` - добавить кнопку
- [ ] Обновить `keyboards/inline.py` - добавить кнопку
- [ ] Обновить `utils/notifications.py` - добавить send_support_message
- [ ] Обновить `.env`:
  ```
  SUPPORT_EMAIL=support@usn.example.com
  SUPPORT_TELEGRAM_ID=123456789
  ```
- [ ] Перезагрузить бота
- [ ] Протестировать: `/support` → отправить сообщение

---

**Status:** ✅ Ready to implement
**Last Updated:** 2026-02-09
