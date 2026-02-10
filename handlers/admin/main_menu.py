from typing import List, Dict, Any
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from utils.admin_check import admin_only
from utils import db_manager
from keyboards.admin_keyboards import admin_main_menu_keyboard
from messages import BotMessages
from states import AdminStates

admin_main_router: Router = Router()

@admin_main_router.message(Command("admin"))
@admin_only
async def admin_command_handler(message: Message, state: FSMContext) -> None:
    """Handle /admin command - open admin panel."""
    pending_apps: List[Dict[str, Any]] = await db_manager.get_pending_registrations()
    pending_count: int = len(pending_apps)

    text = f"""
{BotMessages.ADMIN_MAIN_MENU}

📊 Статистика:
📬 Заявок на рассмотрение: {pending_count}

Выберите действие:
    """.strip()

    await message.answer(text, reply_markup=admin_main_menu_keyboard())
    await state.set_state(AdminStates.admin_main_menu)

