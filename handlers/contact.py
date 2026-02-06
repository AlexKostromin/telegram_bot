"""
Обработчик для "Связаться с командой USN".
"""
from typing import Optional
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from messages import BotMessages
from keyboards import InlineKeyboards
from states import ContactStates

# Создание роутера
contact_router = Router()


@contact_router.message(StateFilter(ContactStates.waiting_for_message))
async def contact_message_handler(message: Message, state: FSMContext) -> None:
    """
    Обработчик сообщения для команды USN.

    Args:
        message: Объект сообщения
        state: Контекст FSM
    """
    # Сохранить сообщение (в реальной системе отправить команде)
    user_message: str = message.text
    user_id: int = message.from_user.id
    username: str = message.from_user.username or "Неизвестно"

    # Логирование сообщения (можно отправить команде через отдельный канал/чат)
    print(f"Message from user {user_id} (@{username}): {user_message}")

    # Отправить подтверждение пользователю
    await message.answer(
        BotMessages.CONTACT_SUCCESS,
        reply_markup=InlineKeyboards.main_menu_keyboard(),
    )

    # Очистить состояние
    await state.clear()