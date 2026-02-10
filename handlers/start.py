from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from messages import BotMessages
from keyboards import InlineKeyboards

start_router = Router()

@start_router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /start.

    Args:
        message: Объект сообщения
        state: Контекст FSM
    """

    await state.clear()

    await message.answer(
        BotMessages.MAIN_MENU_START,
        reply_markup=InlineKeyboards.main_menu_keyboard(),
    )

@start_router.message(Command("help"))
async def help_handler(message: Message) -> None:
    """
    Обработчик команды /help.

    Args:
        message: Объект сообщения
    """
    help_text = (
        "🤖 **Справка по использованию бота USN**\n\n"
        "**Доступные команды:**\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n\n"
        "**Основные функции:**\n"
        "1️⃣ Связаться с командой USN - Отправить сообщение команде\n"
        "2️⃣ Зарегистрироваться на соревнования - Пройти процесс регистрации\n\n"
        "**Советы:**\n"
        "• Используйте кнопки для навигации\n"
        "• Корректно заполняйте все поля при регистрации\n"
        "• При возникновении вопросов свяжитесь с командой USN\n"
    )
    await message.answer(help_text)

