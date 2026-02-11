from typing import Optional, Dict, Any
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from messages import BotMessages
from keyboards import InlineKeyboards
from states import RegistrationStates
from utils import db_manager, Validators, BotHelpers
from models import UserModel

user_create_router = Router()

@user_create_router.message(StateFilter(RegistrationStates.waiting_for_first_name))
async def get_first_name(message: Message, state: FSMContext) -> None:
    is_valid: bool
    value: str
    is_valid, value = Validators.validate_name(message.text)
    if not is_valid:
        await message.answer(
            BotMessages.INVALID_INPUT,
            reply_markup=InlineKeyboards.back_keyboard(),
            parse_mode="HTML",
        )
        return

    await state.update_data(first_name=value)
    await state.set_state(RegistrationStates.waiting_for_last_name)
    await message.answer(
        BotMessages.REQUEST_LAST_NAME,
        reply_markup=InlineKeyboards.back_keyboard(),
        parse_mode="HTML",
    )

@user_create_router.message(StateFilter(RegistrationStates.waiting_for_last_name))
async def get_last_name(message: Message, state: FSMContext) -> None:
    is_valid, value = Validators.validate_name(message.text)
    if not is_valid:
        await message.answer(
            BotMessages.INVALID_INPUT,
            reply_markup=InlineKeyboards.back_keyboard(),
            parse_mode="HTML",
        )
        return

    await state.update_data(last_name=value)
    await state.set_state(RegistrationStates.waiting_for_phone)
    await message.answer(
        BotMessages.REQUEST_PHONE,
        reply_markup=InlineKeyboards.back_keyboard(),
        parse_mode="HTML",
    )

@user_create_router.message(StateFilter(RegistrationStates.waiting_for_phone))
async def get_phone(message: Message, state: FSMContext) -> None:
    is_valid, value = Validators.validate_phone(message.text)
    if not is_valid:
        await message.answer(
            BotMessages.INVALID_INPUT,
            reply_markup=InlineKeyboards.back_keyboard(),
            parse_mode="HTML",
        )
        return

    if await db_manager.phone_exists(value):
        await message.answer(
            "<b>❌ Ошибка</b>\n\nПользователь с таким номером телефона уже зарегистрирован.",
            reply_markup=InlineKeyboards.back_keyboard(),
            parse_mode="HTML",
        )
        return

    await state.update_data(phone=value)
    await state.set_state(RegistrationStates.waiting_for_email)
    await message.answer(
        BotMessages.REQUEST_EMAIL,
        reply_markup=InlineKeyboards.back_keyboard(),
        parse_mode="HTML",
    )

@user_create_router.message(StateFilter(RegistrationStates.waiting_for_email))
async def get_email(message: Message, state: FSMContext) -> None:
    is_valid, value = Validators.validate_email(message.text)
    if not is_valid:
        await message.answer(
            BotMessages.INVALID_INPUT,
            reply_markup=InlineKeyboards.back_keyboard(),
            parse_mode="HTML",
        )
        return

    if await db_manager.email_exists(value):
        await message.answer(
            "<b>❌ Ошибка</b>\n\nПользователь с таким email уже зарегистрирован.",
            reply_markup=InlineKeyboards.back_keyboard(),
            parse_mode="HTML",
        )
        return

    await state.update_data(email=value)
    await state.set_state(RegistrationStates.waiting_for_country)
    await message.answer(
        BotMessages.REQUEST_COUNTRY,
        reply_markup=InlineKeyboards.back_keyboard(),
        parse_mode="HTML",
    )

@user_create_router.message(StateFilter(RegistrationStates.waiting_for_country))
async def get_country(message: Message, state: FSMContext) -> None:
    is_valid, value = Validators.validate_text_field(message.text, min_length=2, max_length=100)
    if not is_valid:
        await message.answer(
            BotMessages.INVALID_INPUT,
            reply_markup=InlineKeyboards.back_keyboard(),
            parse_mode="HTML",
        )
        return

    await state.update_data(country=value)
    await state.set_state(RegistrationStates.waiting_for_city)
    await message.answer(
        BotMessages.REQUEST_CITY,
        reply_markup=InlineKeyboards.back_keyboard(),
        parse_mode="HTML",
    )

@user_create_router.message(StateFilter(RegistrationStates.waiting_for_city))
async def get_city(message: Message, state: FSMContext) -> None:
    is_valid, value = Validators.validate_text_field(message.text, min_length=2, max_length=100)
    if not is_valid:
        await message.answer(
            BotMessages.INVALID_INPUT,
            reply_markup=InlineKeyboards.back_keyboard(),
            parse_mode="HTML",
        )
        return

    await state.update_data(city=value)
    await state.set_state(RegistrationStates.waiting_for_club)
    await message.answer(
        BotMessages.REQUEST_CLUB,
        reply_markup=InlineKeyboards.back_keyboard(),
        parse_mode="HTML",
    )

@user_create_router.message(StateFilter(RegistrationStates.waiting_for_club))
async def get_club(message: Message, state: FSMContext) -> None:
    is_valid, value = Validators.validate_text_field(message.text, min_length=2, max_length=255)
    if not is_valid:
        await message.answer(
            BotMessages.INVALID_INPUT,
            reply_markup=InlineKeyboards.back_keyboard(),
            parse_mode="HTML",
        )
        return

    await state.update_data(club=value)
    await state.set_state(RegistrationStates.waiting_for_role_confirmation_first)
    await message.answer(
        BotMessages.REQUEST_PLAYER_VOTER,
        reply_markup=InlineKeyboards.yes_no_keyboard(),
        parse_mode="HTML",
    )

@user_create_router.message(StateFilter(RegistrationStates.waiting_for_certificate_name))
async def get_certificate_name(message: Message, state: FSMContext) -> None:
    is_valid, value = Validators.validate_certificate_name(message.text)
    if not is_valid:
        await message.answer(
            "<b>❌ Ошибка формата</b>\n\nПожалуйста, используйте только латинские буквы, пробелы и дефисы.",
            reply_markup=InlineKeyboards.back_keyboard(),
            parse_mode="HTML",
        )
        return

    await state.update_data(certificate_name=value)
    state_data = await state.get_data()

    if state_data.get('first_role_confirmation_yes') == False:

        await state.set_state(RegistrationStates.waiting_for_presentation)
        await message.answer(
            BotMessages.REQUEST_PRESENTATION,
            reply_markup=InlineKeyboards.back_keyboard(),
        )
    else:

        await state.set_state(RegistrationStates.waiting_for_company)
        await message.answer(
            BotMessages.REQUEST_COMPANY,
            reply_markup=InlineKeyboards.back_keyboard(),
        )

@user_create_router.message(StateFilter(RegistrationStates.waiting_for_company))
async def get_company(message: Message, state: FSMContext) -> None:
    is_valid, value = Validators.validate_text_field(message.text, min_length=2, max_length=255)
    if not is_valid:
        await message.answer(
            BotMessages.INVALID_INPUT,
            reply_markup=InlineKeyboards.back_keyboard(),
            parse_mode="HTML",
        )
        return

    await state.update_data(company=value)
    await state.set_state(RegistrationStates.waiting_for_position)
    await message.answer(
        BotMessages.REQUEST_POSITION,
        reply_markup=InlineKeyboards.back_keyboard(),
    )

@user_create_router.message(StateFilter(RegistrationStates.waiting_for_position))
async def get_position(message: Message, state: FSMContext) -> None:
    is_valid, value = Validators.validate_text_field(message.text, min_length=2, max_length=255)
    if not is_valid:
        await message.answer(
            BotMessages.INVALID_INPUT,
            reply_markup=InlineKeyboards.back_keyboard(),
            parse_mode="HTML",
        )
        return

    await state.update_data(position=value)
    state_data = await state.get_data()
    first_role_confirmation_yes = state_data.get('first_role_confirmation_yes', False)

    if first_role_confirmation_yes:

        await state.set_state(RegistrationStates.waiting_for_role_confirmation_repeat)
        await message.answer(
            BotMessages.REQUEST_PLAYER_VOTER,
            reply_markup=InlineKeyboards.yes_no_keyboard(),
        )
    else:

        await state.set_state(RegistrationStates.waiting_for_role_confirmation_repeat)
        await message.answer(
            BotMessages.REQUEST_PLAYER_VOTER,
            reply_markup=InlineKeyboards.yes_no_keyboard(),
        )

@user_create_router.callback_query(F.data == "yes", RegistrationStates.waiting_for_role_confirmation_first)
async def role_confirmation_first_yes(query: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(first_role_confirmation_yes=True)
    await state.set_state(RegistrationStates.waiting_for_certificate_name)
    await query.message.edit_text(
        BotMessages.REQUEST_CERTIFICATE_NAME,
        reply_markup=InlineKeyboards.back_keyboard(),
    )
    await query.answer()

@user_create_router.callback_query(F.data == "no", RegistrationStates.waiting_for_role_confirmation_first)
async def role_confirmation_first_no(query: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(first_role_confirmation_yes=False)
    await state.set_state(RegistrationStates.waiting_for_company)
    await query.message.edit_text(
        BotMessages.REQUEST_COMPANY,
        reply_markup=InlineKeyboards.back_keyboard(),
    )
    await query.answer()

@user_create_router.callback_query(F.data == "yes", RegistrationStates.waiting_for_role_confirmation_repeat)
async def role_confirmation_repeat_yes(query: CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()
    first_role_confirmation_yes = state_data.get('first_role_confirmation_yes', False)

    if first_role_confirmation_yes:
        await state.set_state(RegistrationStates.waiting_for_presentation)
        await query.message.edit_text(
            BotMessages.REQUEST_PRESENTATION,
            reply_markup=InlineKeyboards.back_keyboard(),
        )
    else:
        await state.set_state(RegistrationStates.waiting_for_certificate_name)
        await query.message.edit_text(
            BotMessages.REQUEST_CERTIFICATE_NAME,
            reply_markup=InlineKeyboards.back_keyboard(),
            parse_mode="HTML",
        )
    await query.answer()

@user_create_router.callback_query(F.data == "no", RegistrationStates.waiting_for_role_confirmation_repeat)
async def role_confirmation_repeat_no(query: CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()
    first_role_confirmation_yes = state_data.get('first_role_confirmation_yes', False)

    if first_role_confirmation_yes:

        await state.update_data(presentation="")
    else:

        await state.update_data(certificate_name=None, presentation="")

    await state.set_state(RegistrationStates.waiting_for_final_confirmation)
    state_data = await state.get_data()
    user = await _create_user_from_state_data(query.from_user, state_data)

    if user:
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
        await query.message.edit_text(
            user_data_text,
            reply_markup=InlineKeyboards.yes_no_keyboard(),
            parse_mode="HTML",
        )

    await query.answer()

@user_create_router.message(StateFilter(RegistrationStates.waiting_for_presentation))
async def get_presentation(message: Message, state: FSMContext) -> None:
    is_valid, value = Validators.validate_text_field(message.text, min_length=3, max_length=500)
    if not is_valid:
        await message.answer(
            BotMessages.INVALID_INPUT,
            reply_markup=InlineKeyboards.back_keyboard(),
            parse_mode="HTML",
        )
        return

    await state.update_data(presentation=value)

    state_data = await state.get_data()
    selected_role = state_data.get("selected_role")
    selected_competition = state_data.get("selected_competition")

    if selected_role == "voter" and selected_competition:
        try:
            time_slots = await db_manager.get_available_time_slots(selected_competition.get("id"))

            if time_slots:
                await message.answer(
                    BotMessages.SELECT_TIME_SLOTS,
                    reply_markup=InlineKeyboards.time_slots_keyboard(time_slots, [])
                )
                await state.set_state(RegistrationStates.waiting_for_time_slot_selection)
                return
        except Exception as e:
            print(f"Error loading time slots: {e}")

    await state.set_state(RegistrationStates.waiting_for_final_confirmation)

    user = await _create_user_from_state_data(message.from_user, state_data)

    if user:
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
        await message.answer(
            user_data_text,
            reply_markup=InlineKeyboards.yes_no_keyboard(),
            parse_mode="HTML",
        )

@user_create_router.callback_query(F.data == "yes", RegistrationStates.waiting_for_certificate_name)
async def certificate_after_role_yes(query: CallbackQuery, state: FSMContext) -> None:

    pass

async def _create_user_from_state_data(telegram_user: Any, state_data: Dict[str, Any]) -> UserModel:
    user: UserModel = UserModel(
        telegram_id=telegram_user.id,
        telegram_username=telegram_user.username,
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
    return user
