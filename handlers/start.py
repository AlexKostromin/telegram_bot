from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from messages import BotMessages
from keyboards import InlineKeyboards

start_router = Router()

@start_router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext) -> None:

    await state.clear()

    await message.answer(
        BotMessages.MAIN_MENU_START,
        reply_markup=InlineKeyboards.main_menu_keyboard(),
        parse_mode="HTML",
    )

@start_router.message(Command("help"))
async def help_handler(message: Message) -> None:
    help_text = (
        "<b>🤖 Справка по использованию бота USN</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>Доступные команды:</b>\n"
        "   /start - Начать работу с ботом\n"
        "   /help - Показать эту справку\n\n"
        "<b>Основные функции:</b>\n"
        "   1️⃣ Связаться с командой USN\n"
        "      ↳ Отправить сообщение команде\n"
        "   2️⃣ Зарегистрироваться на соревнования\n"
        "      ↳ Пройти процесс регистрации\n\n"
        "<b>💡 Советы:</b>\n"
        "   ✓ Используйте кнопки для навигации\n"
        "   ✓ Заполняйте поля корректно при регистрации\n"
        "   ✓ Свяжитесь с командой при возникновении вопросов\n\n"
        "━━━━━━━━━━━━━━━━━━━"
    )
    await message.answer(help_text, parse_mode="HTML")
