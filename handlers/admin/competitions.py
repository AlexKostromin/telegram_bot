import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from utils.admin_check import admin_only
from utils import db_manager
from utils.helpers import parse_callback_id
from keyboards.admin_keyboards import (
    competition_management_keyboard,
    admin_main_menu_keyboard,
)
from states import AdminStates

logger = logging.getLogger(__name__)

admin_competitions_router = Router()

def competitions_list_keyboard(competitions: list):
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    for comp in competitions:
        comp_name = comp.get("name", comp.name) if isinstance(comp, dict) else comp.name
        comp_id = comp.get("id", comp.id) if isinstance(comp, dict) else comp.id
        builder.button(
            text=f"🏆 {comp_name}",
            callback_data=f"comp_manage_{comp_id}"
        )
    builder.button(text="⬅️ Назад", callback_data="admin_menu")
    builder.adjust(1)
    return builder.as_markup()

@admin_competitions_router.callback_query(F.data == "admin_competitions")
@admin_only
async def list_competitions(callback: CallbackQuery, state: FSMContext):
    competitions = await db_manager.get_active_competitions()

    if not competitions:
        await callback.message.answer(
            "❌ Нет активных соревнований",
            reply_markup=admin_main_menu_keyboard()
        )
        await callback.answer()
        return

    text = f"🏆 Соревнования ({len(competitions)}):"
    await callback.message.answer(
        text,
        reply_markup=competitions_list_keyboard(competitions)
    )
    await state.set_state(AdminStates.managing_competition)
    await callback.answer()

@admin_competitions_router.callback_query(F.data.startswith("comp_manage_"))
@admin_only
async def manage_competition(callback: CallbackQuery, state: FSMContext):
    competition_id = parse_callback_id(callback.data)
    if competition_id is None:
        await callback.answer("Ошибка данных", show_alert=True)
        return
    competition = await db_manager.get_competition_by_id(competition_id)

    if not competition:
        await callback.answer("Competition not found", show_alert=True)
        return

    player_status = "✅" if competition.player_entry_open else "❌"
    voter_status = "✅" if competition.voter_entry_open else "❌"
    viewer_status = "✅" if competition.viewer_entry_open else "❌"
    adviser_status = "✅" if competition.adviser_entry_open else "❌"

    text = (
        f"<b>🏆 {competition.name}</b>\n\n"
        f"Тип: {competition.competition_type}\n"
        f"Статус: {'Активно' if competition.is_active else 'Неактивно'}\n\n"
        f"<b>Регистрация по ролям:</b>\n"
        f"  {player_status} Игрок\n"
        f"  {voter_status} Судья\n"
        f"  {viewer_status} Зритель\n"
        f"  {adviser_status} Советник"
    )

    await callback.message.edit_text(
        text,
        reply_markup=competition_management_keyboard(competition),
        parse_mode="HTML"
    )
    await state.update_data(managing_competition=competition_id)
    await state.set_state(AdminStates.managing_competition)
    await callback.answer()

@admin_competitions_router.callback_query(F.data.startswith("toggle_entry_"))
@admin_only
async def toggle_role_entry(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    try:
        competition_id = int(parts[2])
        role = parts[3]
    except (IndexError, ValueError):
        await callback.answer("Ошибка данных", show_alert=True)
        return

    competition = await db_manager.get_competition_by_id(competition_id)
    current_status = getattr(competition, f"{role}_entry_open")
    new_status = not current_status

    await db_manager.update_role_entry_status(competition_id, role, new_status)

    status_text = "✅ Открыто" if new_status else "❌ Закрыто"
    await callback.answer(f"{role.upper()}: {status_text}")

    await manage_competition(callback, state)
