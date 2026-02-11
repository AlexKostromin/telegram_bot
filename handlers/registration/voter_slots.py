import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from messages import BotMessages
from keyboards.inline import InlineKeyboards
from states import RegistrationStates
from utils import db_manager
from utils.helpers import BotHelpers, parse_callback_id

logger = logging.getLogger(__name__)

voter_slots_router = Router()


async def _show_final_confirmation(callback: CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()
    from handlers.registration.user_create import _create_user_from_state_data

    user = await _create_user_from_state_data(callback.from_user, state_data)
    if user:
        user_data_text = BotHelpers.format_user_confirmation_from_model(user, state_data)
        await callback.message.edit_text(
            user_data_text,
            reply_markup=InlineKeyboards.yes_no_keyboard(),
            parse_mode="HTML",
        )


@voter_slots_router.callback_query(
    StateFilter(RegistrationStates.waiting_for_time_slot_selection)
)
async def time_slot_selection_handler(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.data == "slots_confirm":
        data = await state.get_data()
        selected_slots = data.get('selected_time_slots', [])

        if not selected_slots:
            await callback.answer("Выберите хотя бы один слот", show_alert=True)
            return

        competition_id = data.get('selected_competition')
        if isinstance(competition_id, dict):
            competition_id = competition_id.get('id')

        competition = await db_manager.get_competition_by_id(competition_id)

        if competition and competition.requires_jury_panel:
            panels = await db_manager.get_jury_panels_for_competition(competition_id)
            if panels:
                await callback.message.edit_text(
                    BotMessages.SELECT_JURY_PANEL,
                    reply_markup=InlineKeyboards.jury_panels_keyboard(panels),
                    parse_mode="HTML"
                )
                await state.set_state(RegistrationStates.waiting_for_jury_panel_selection)
                await callback.answer()
                return

        await state.set_state(RegistrationStates.waiting_for_final_confirmation)
        await _show_final_confirmation(callback, state)
        await callback.answer()

    elif callback.data.startswith("slot_toggle_"):
        slot_id = parse_callback_id(callback.data)
        if slot_id is None:
            await callback.answer("Ошибка данных", show_alert=True)
            return

        data = await state.get_data()
        selected_slots = list(data.get('selected_time_slots', []))

        if slot_id in selected_slots:
            selected_slots.remove(slot_id)
        else:
            selected_slots.append(slot_id)

        await state.update_data(selected_time_slots=selected_slots)

        competition_id = data.get('selected_competition')
        if isinstance(competition_id, dict):
            competition_id = competition_id.get('id')

        time_slots = await db_manager.get_available_time_slots(competition_id)
        await callback.message.edit_reply_markup(
            reply_markup=InlineKeyboards.time_slots_keyboard(time_slots, selected_slots)
        )
        await callback.answer()


@voter_slots_router.callback_query(
    StateFilter(RegistrationStates.waiting_for_jury_panel_selection)
)
async def jury_panel_selection_handler(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.data.startswith("panel_select_"):
        panel_id = parse_callback_id(callback.data)
        if panel_id is None:
            await callback.answer("Ошибка данных", show_alert=True)
            return

        await state.update_data(selected_jury_panel=panel_id)
        await state.set_state(RegistrationStates.waiting_for_final_confirmation)
        await _show_final_confirmation(callback, state)
        await callback.answer()