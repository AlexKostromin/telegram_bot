from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from utils.admin_check import admin_only
from utils import db_manager
from keyboards.admin_keyboards import (
    competition_management_keyboard,
    admin_main_menu_keyboard,
)
from states import AdminStates

admin_competitions_router = Router()

def competitions_list_keyboard(competitions: list):
    """Create keyboard with competitions list."""
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    for comp in competitions:
        builder.button(
            text=f"🏆 {comp.name}",
            callback_data=f"comp_manage_{comp.id}"
        )
    builder.button(text="⬅️ Назад", callback_data="admin_menu")
    builder.adjust(1)
    return builder.as_markup()

@admin_competitions_router.callback_query(F.data == "admin_competitions")
@admin_only
async def list_competitions(callback: CallbackQuery, state: FSMContext):
    """List active competitions."""
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
    """Manage specific competition entry flags."""
    competition_id = int(callback.data.split("_")[2])
    competition = await db_manager.get_competition_by_id(competition_id)

    if not competition:
        await callback.answer("Competition not found", show_alert=True)
        return

    text = f"""
🏆 {competition.name}

Статусы открытия регистрации:
Player: {'✅ Открыто' if competition.player_entry_open else '❌ Закрыто'}
Voter: {'✅ Открыто' if competition.voter_entry_open else '❌ Закрыто'}
Viewer: {'✅ Открыто' if competition.viewer_entry_open else '❌ Закрыто'}
Adviser: {'✅ Открыто' if competition.adviser_entry_open else '❌ Закрыто'}

Нажмите на роль чтобы переключить статус:
    """.strip()

    await callback.message.edit_text(
        text,
        reply_markup=competition_management_keyboard(competition)
    )
    await state.update_data(managing_competition=competition_id)
    await state.set_state(AdminStates.managing_competition)
    await callback.answer()

@admin_competitions_router.callback_query(F.data.startswith("toggle_entry_"))
@admin_only
async def toggle_role_entry(callback: CallbackQuery, state: FSMContext):
    """Toggle role entry status for competition."""
    parts = callback.data.split("_")
    competition_id = int(parts[2])
    role = parts[3]

    competition = await db_manager.get_competition_by_id(competition_id)
    current_status = getattr(competition, f"{role}_entry_open")
    new_status = not current_status

    await db_manager.update_role_entry_status(competition_id, role, new_status)

    status_text = "✅ Открыто" if new_status else "❌ Закрыто"
    await callback.answer(f"{role.upper()}: {status_text}")

    await manage_competition(callback, state)

