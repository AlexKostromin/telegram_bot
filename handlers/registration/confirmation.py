from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from messages import BotMessages
from keyboards import InlineKeyboards
from states import RegistrationStates
from utils import db_manager
from utils.notifications import notify_admins_new_registration

confirmation_router = Router()

@confirmation_router.callback_query(F.data == "yes", RegistrationStates.waiting_for_final_confirmation)
async def final_confirmation_yes(query: CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()
    user_telegram_id = query.from_user.id
    selected_competition = state_data.get("selected_competition")
    selected_role = state_data.get("selected_role")

    existing_user = await db_manager.get_user_by_telegram_id(user_telegram_id)

    if not existing_user:

        try:
            new_user = await db_manager.create_user(
                telegram_id=user_telegram_id,
                telegram_username=query.from_user.username or "",
                first_name=state_data.get("first_name", ""),
                last_name=state_data.get("last_name", ""),
                phone=state_data.get("phone", ""),
                email=state_data.get("email", ""),
                country=state_data.get("country", ""),
                city=state_data.get("city", ""),
                club=state_data.get("club", ""),
                bio=state_data.get("bio"),
                date_of_birth=state_data.get("date_of_birth"),
                channel_name=state_data.get("channel_name"),
                company=state_data.get("company", ""),
                position=state_data.get("position", ""),
                certificate_name=state_data.get("certificate_name"),
                presentation=state_data.get("presentation"),
            )
            user_id = new_user.id
        except Exception as e:
            await query.answer("❌ Ошибка при создании пользователя", show_alert=True)
            print(f"Error creating user: {e}")
            return
    else:
        user_id = existing_user.id

    registration = None
    if selected_competition:
        try:

            registration = await db_manager.create_registration(
                user_id=user_id,
                telegram_id=user_telegram_id,
                competition_id=selected_competition.get("id") if selected_competition else None,
                role=selected_role,
                status='pending',
            )

            if state_data.get('selected_time_slots'):
                for slot_id in state_data.get('selected_time_slots', []):
                    await db_manager.assign_voter_to_time_slot(registration.id, slot_id)

            if state_data.get('selected_jury_panel'):
                await db_manager.assign_voter_to_jury_panel(
                    registration.id,
                    state_data['selected_jury_panel']
                )

        except Exception as e:
            await query.answer("❌ Ошибка при регистрации на соревнование", show_alert=True)
            print(f"Error creating registration: {e}")
            return

    await query.message.edit_text(
        BotMessages.REGISTRATION_PENDING,
        reply_markup=InlineKeyboards.main_menu_keyboard(),
        parse_mode="HTML",
    )

    if registration and existing_user:
        user = existing_user
    elif registration:
        user = await db_manager.get_user_by_telegram_id(user_telegram_id)
    else:
        user = None

    if user and registration and selected_competition:
        competition = await db_manager.get_competition_by_id(selected_competition)
        if competition:
            await notify_admins_new_registration(
                bot=query.bot,
                user_name=user.get_display_name(),
                competition_name=competition.name,
                role=selected_role
            )

    await state.clear()
    await query.answer()

@confirmation_router.callback_query(F.data == "no", RegistrationStates.waiting_for_final_confirmation)
async def final_confirmation_no(query: CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()
    selected_role = state_data.get("selected_role", "spectator")

    from utils import BotHelpers
    edit_fields = BotHelpers.get_edit_fields_for_role(selected_role)

    await state.set_state(RegistrationStates.waiting_for_edit_field_select)
    await query.message.edit_text(
        BotMessages.EDIT_FIELD_PROMPT,
        reply_markup=InlineKeyboards.edit_fields_keyboard(edit_fields),
        parse_mode="HTML",
    )
    await query.answer()

@confirmation_router.callback_query(F.data == "yes", RegistrationStates.registration_complete)
async def registration_complete_yes(query: CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()
    user_telegram_id = query.from_user.id
    selected_competition = state_data.get("selected_competition")
    selected_role = state_data.get("selected_role")

    user = await db_manager.get_user_by_telegram_id(user_telegram_id)
    if not user:
        await query.answer("❌ Пользователь не найден", show_alert=True)
        return

    if selected_competition:
        try:
            await db_manager.create_registration(
                user_id=user.id,
                telegram_id=user_telegram_id,
                competition_id=selected_competition.get("id"),
                role=selected_role,
            )
        except Exception as e:
            await query.answer("❌ Ошибка при регистрации на соревнование", show_alert=True)
            print(f"Error creating registration: {e}")
            return

    role_names = {
        "player": "Игрок (Player)",
        "voter": "Судья (Voter)",
        "spectator": "Зритель",
        "second": "Секундант",
    }
    role_display = role_names.get(selected_role, selected_role)

    success_message = BotMessages.REGISTRATION_SUCCESS.format(
        role=role_display,
        competition=selected_competition.get("name", ""),
    )

    await query.message.edit_text(
        success_message,
        reply_markup=InlineKeyboards.main_menu_keyboard(),
        parse_mode="HTML",
    )

    await state.clear()
    await query.answer()
