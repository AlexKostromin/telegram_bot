"""
Voter time slot and jury panel selection handlers.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from messages import BotMessages
from keyboards.inline import InlineKeyboards
from states import RegistrationStates
from utils import db_manager

voter_slots_router = Router()


@voter_slots_router.callback_query(
    StateFilter(RegistrationStates.waiting_for_time_slot_selection)
)
async def time_slot_selection_handler(callback: CallbackQuery, state: FSMContext):
    """Handle time slot selection (multi-select)."""
    if callback.data == "slots_confirm":
        # User confirmed slot selection
        data = await state.get_data()
        selected_slots = data.get('selected_time_slots', [])

        if not selected_slots:
            await callback.answer("Выберите хотя бы один слот", show_alert=True)
            return

        # Check if jury panel is required
        competition_id = data.get('selected_competition')
        competition = await db_manager.get_competition_by_id(competition_id)

        if competition and competition.requires_jury_panel:
            panels = await db_manager.get_jury_panels_for_competition(competition_id)
            if panels:
                await callback.message.edit_text(
                    BotMessages.SELECT_JURY_PANEL,
                    reply_markup=InlineKeyboards.jury_panels_keyboard(panels)
                )
                await state.set_state(RegistrationStates.waiting_for_jury_panel_selection)
            else:
                # No panels available, proceed to final confirmation
                await state.set_state(RegistrationStates.waiting_for_final_confirmation)
                await callback.answer()
                return
        else:
            # No jury panel needed, proceed to company field
            await state.set_state(RegistrationStates.waiting_for_company)
            await callback.message.edit_text(
                BotMessages.REQUEST_COMPANY,
                reply_markup=InlineKeyboards.back_keyboard(),
            )

        await callback.answer()

    elif callback.data.startswith("slot_toggle_"):
        # User toggled a slot selection
        slot_id = int(callback.data.split("_")[2])
        data = await state.get_data()
        selected_slots = data.get('selected_time_slots', [])

        if slot_id in selected_slots:
            selected_slots.remove(slot_id)
        else:
            selected_slots.append(slot_id)

        await state.update_data(selected_time_slots=selected_slots)

        # Refresh keyboard
        competition_id = data.get('selected_competition')
        time_slots = await db_manager.get_available_time_slots(competition_id)
        await callback.message.edit_reply_markup(
            reply_markup=InlineKeyboards.time_slots_keyboard(time_slots, selected_slots)
        )
        await callback.answer()


@voter_slots_router.callback_query(
    StateFilter(RegistrationStates.waiting_for_jury_panel_selection)
)
async def jury_panel_selection_handler(callback: CallbackQuery, state: FSMContext):
    """Handle jury panel selection."""
    if callback.data.startswith("panel_select_"):
        panel_id = int(callback.data.split("_")[2])
        await state.update_data(selected_jury_panel=panel_id)

        # Proceed to company field
        await state.set_state(RegistrationStates.waiting_for_company)
        await callback.message.edit_text(
            BotMessages.REQUEST_COMPANY,
            reply_markup=InlineKeyboards.back_keyboard(),
        )
        await callback.answer()
