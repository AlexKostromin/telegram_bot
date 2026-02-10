from typing import Optional, List, Dict, Any
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from messages import BotMessages
from keyboards import InlineKeyboards
from states import RegistrationStates
from utils import db_manager, Validators, BotHelpers
from models import UserModel

user_edit_router = Router()

@user_edit_router.callback_query(F.data == "yes", RegistrationStates.waiting_for_existing_user_confirmation)
async def user_data_confirmed(query: CallbackQuery, state: FSMContext) -> None:

    await state.set_state(RegistrationStates.registration_complete)
    await state.update_data(data_confirmed=True)

    await query.answer()

@user_edit_router.callback_query(F.data == "no", RegistrationStates.waiting_for_existing_user_confirmation)
async def user_data_edit_needed(query: CallbackQuery, state: FSMContext) -> None:

    state_data: Dict[str, Any] = await state.get_data()
    selected_role: str = state_data.get("selected_role", "spectator")

    edit_fields: List[str] = BotHelpers.get_edit_fields_for_role(selected_role)

    await state.set_state(RegistrationStates.waiting_for_edit_field_select)
    await query.message.edit_text(
        BotMessages.EDIT_FIELD_PROMPT,
        reply_markup=InlineKeyboards.edit_fields_keyboard(edit_fields),
    )
    await query.answer()

@user_edit_router.callback_query(F.data.startswith("edit_field_"), RegistrationStates.waiting_for_edit_field_select)
async def edit_field_selected(query: CallbackQuery, state: FSMContext) -> None:

    field_name: str = query.data.split("_", 2)[2]

    await state.update_data(editing_field=field_name)

    await state.set_state(RegistrationStates.waiting_for_field_edit_input)
    field_display = BotMessages.get_edit_field_name(field_name)
    await query.message.edit_text(
        BotMessages.EDIT_FIELD_INPUT_PROMPT.format(field_name=field_display),
        reply_markup=InlineKeyboards.back_keyboard(),
    )
    await query.answer()

@user_edit_router.message(StateFilter(RegistrationStates.waiting_for_field_edit_input))
async def edit_field_input(message: Message, state: FSMContext) -> None:
    state_data: Dict[str, Any] = await state.get_data()
    editing_field: str = state_data.get("editing_field")

    is_valid: bool
    value: Any
    if editing_field == "phone":
        is_valid, value = Validators.validate_phone(message.text)
    elif editing_field == "email":
        is_valid, value = Validators.validate_email(message.text)
    elif editing_field == "certificate_name":
        is_valid, value = Validators.validate_certificate_name(message.text)
    else:
        is_valid, value = Validators.validate_text_field(message.text)

    if not is_valid:
        await message.answer(
            BotMessages.INVALID_INPUT,
            reply_markup=InlineKeyboards.back_keyboard(),
        )
        return

    user_id: int = message.from_user.id
    updated_user: Optional[UserModel] = await db_manager.update_user(user_id, **{editing_field: value})

    if not updated_user:
        await message.answer(
            BotMessages.REGISTRATION_ERROR,
            reply_markup=InlineKeyboards.back_keyboard(),
        )
        return

    await message.answer(BotMessages.EDIT_SUCCESS)

    await state.set_state(RegistrationStates.waiting_for_edit_confirmation)
    await message.answer(
        BotMessages.EDIT_CONTINUE_PROMPT,
        reply_markup=InlineKeyboards.yes_no_keyboard(),
    )

@user_edit_router.callback_query(F.data == "yes", RegistrationStates.waiting_for_edit_confirmation)
async def continue_editing(query: CallbackQuery, state: FSMContext) -> None:

    state_data = await state.get_data()
    selected_role = state_data.get("selected_role", "spectator")

    edit_fields = BotHelpers.get_edit_fields_for_role(selected_role)

    await state.set_state(RegistrationStates.waiting_for_edit_field_select)
    await query.message.edit_text(
        BotMessages.EDIT_FIELD_PROMPT,
        reply_markup=InlineKeyboards.edit_fields_keyboard(edit_fields),
    )
    await query.answer()

@user_edit_router.callback_query(F.data == "no", RegistrationStates.waiting_for_edit_confirmation)
async def finish_editing(query: CallbackQuery, state: FSMContext) -> None:

    user: Optional[UserModel] = await db_manager.get_user_by_telegram_id(query.from_user.id)
    state_data: Dict[str, Any] = await state.get_data()
    selected_role: str = state_data.get("selected_role", "spectator")

    if not user:
        await query.answer("❌ Ошибка при загрузке данных", show_alert=True)
        return

    include_certificate = selected_role in ["player", "voter"]
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

    await state.set_state(RegistrationStates.waiting_for_existing_user_confirmation)
    await query.message.edit_text(
        user_data_text,
        reply_markup=InlineKeyboards.yes_no_keyboard(),
    )
    await query.answer()
