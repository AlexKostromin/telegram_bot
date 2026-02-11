from typing import List, Dict, Any
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from utils.admin_check import admin_only
from utils import db_manager
from keyboards.admin_keyboards import admin_main_menu_keyboard
from states import AdminStates

admin_main_router: Router = Router()

@admin_main_router.message(Command("admin"))
@admin_only
async def admin_command_handler(message: Message, state: FSMContext) -> None:
    pending_apps: List[Dict[str, Any]] = await db_manager.get_pending_registrations()
    pending_count: int = len(pending_apps)

    text: str = (
        f"<b>🔧 Панель администратора</b>\n\n"
        f"📬 Заявок на рассмотрении: {pending_count}"
    )

    await message.answer(text, reply_markup=admin_main_menu_keyboard(), parse_mode="HTML")
    await state.set_state(AdminStates.admin_main_menu)
