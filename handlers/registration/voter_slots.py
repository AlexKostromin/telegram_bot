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
    if callback.data == "slots_confirm":
        data = await state.get_data()
        selected_slots = data.get('selected_time_slots', [])

        if not selected_slots:
            await callback.answer("Выберите хотя бы один слот", show_alert=True)
            return

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
                await state.set_state(RegistrationStates.waiting_for_final_confirmation)

                state_data = await state.get_data()
                from handlers.registration.user_create import _create_user_from_state_data

                user = await _create_user_from_state_data(callback.from_user, state_data)
                if user:
                    from utils.helpers import BotHelpers
                    include_certificate = state_data.get("certificate_name") is not None
                    user_data_text = BotHelpers.format_user_data(
                        user.first_name,
                        user.last_name,
                        user.telegram_username or "@-",
                        user.phone,
                        user.email,
                        user.country,
                        user.city,
                        user.club,
                        user.company or "-",
                        user.position or "-",
                        user.certificate_name if include_certificate else None,
                        user.presentation if include_certificate else None,
                        include_certificate,
                    )
                    await callback.message.edit_text(
                        user_data_text,
                        reply_markup=InlineKeyboards.yes_no_keyboard(),
                    )
        else:
            await state.set_state(RegistrationStates.waiting_for_final_confirmation)

            state_data = await state.get_data()
            from handlers.registration.user_create import _create_user_from_state_data

            user = await _create_user_from_state_data(callback.from_user, state_data)
            if user:
                from utils.helpers import BotHelpers
                include_certificate = state_data.get("certificate_name") is not None
                user_data_text = BotHelpers.format_user_data(
                    user.first_name,
                    user.last_name,
                    user.telegram_username or "@-",
                    user.phone,
                    user.email,
                    user.country,
                    user.city,
                    user.club,
                    user.company or "-",
                    user.position or "-",
                    user.certificate_name if include_certificate else None,
                    user.presentation if include_certificate else None,
                    include_certificate,
                )
                await callback.message.edit_text(
                    user_data_text,
                    reply_markup=InlineKeyboards.yes_no_keyboard(),
                )

        await callback.answer()

    elif callback.data.startswith("slot_toggle_"):
        slot_id = int(callback.data.split("_")[2])
        data = await state.get_data()
        selected_slots = data.get('selected_time_slots', [])

        if slot_id in selected_slots:
            selected_slots.remove(slot_id)
        else:
            selected_slots.append(slot_id)

        await state.update_data(selected_time_slots=selected_slots)

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
    if callback.data.startswith("panel_select_"):
        panel_id = int(callback.data.split("_")[2])
        await state.update_data(selected_jury_panel=panel_id)

        await state.set_state(RegistrationStates.waiting_for_final_confirmation)

        state_data = await state.get_data()
        from handlers.registration.user_create import _create_user_from_state_data

        user = await _create_user_from_state_data(callback.from_user, state_data)
        if user:
            from utils.helpers import BotHelpers
            include_certificate = state_data.get("certificate_name") is not None
            user_data_text = BotHelpers.format_user_data(
                user.first_name,
                user.last_name,
                user.telegram_username or "@-",
                user.phone,
                user.email,
                user.country,
                user.city,
                user.club,
                user.company or "-",
                user.position or "-",
                user.certificate_name if include_certificate else None,
                user.presentation if include_certificate else None,
                include_certificate,
            )
            await callback.message.edit_text(
                user_data_text,
                reply_markup=InlineKeyboards.yes_no_keyboard(),
            )

        await callback.answer()
