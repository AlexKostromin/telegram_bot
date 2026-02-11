from typing import Optional, Dict, Any, List
import json
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from messages import BotMessages
from keyboards import InlineKeyboards
from states import RegistrationStates
from utils import db_manager
from models import CompetitionModel

competition_select_router = Router()

@competition_select_router.callback_query(F.data == "register")
async def register_callback_handler(query: CallbackQuery, state: FSMContext) -> None:
    print(f"DEBUG: register callback received")

    competitions: List[Dict[str, Any]] = await db_manager.get_active_competitions()
    print(f"DEBUG: competitions = {competitions}")

    if not competitions:

        await query.message.edit_text(
            BotMessages.NO_ACTIVE_COMPETITIONS,
            reply_markup=InlineKeyboards.main_menu_keyboard(),
            parse_mode="HTML",
        )
        await state.clear()
        await query.answer()
        return

    if len(competitions) == 1:

        competition: Dict[str, Any] = competitions[0]
        await state.update_data(selected_competition=competition)
        await state.set_state(RegistrationStates.waiting_for_role_select)

        available_roles: Any = competition["available_roles"]
        if isinstance(available_roles, str):
            available_roles = json.loads(available_roles)

        await query.message.edit_text(
            f"<b>📋 {BotMessages.format_competition_info(competition['name'], competition['type'])}</b>\n\n"
            f"{BotMessages.SELECT_ROLE}",
            reply_markup=InlineKeyboards.roles_keyboard(available_roles),
            parse_mode="HTML",
        )
    else:

        await query.message.edit_text(
            BotMessages.SELECT_COMPETITION,
            reply_markup=InlineKeyboards.competitions_keyboard(competitions),
            parse_mode="HTML",
        )

    await query.answer()

@competition_select_router.message(StateFilter(RegistrationStates.waiting_for_competition_select))
async def competition_select_handler(message: Message, state: FSMContext) -> None:

    competitions: List[Dict[str, Any]] = await db_manager.get_active_competitions()

    if not competitions:

        await message.answer(
            BotMessages.NO_ACTIVE_COMPETITIONS,
            reply_markup=InlineKeyboards.main_menu_keyboard(),
            parse_mode="HTML",
        )
        await state.clear()
        return

    if len(competitions) == 1:

        competition: Dict[str, Any] = competitions[0]
        await state.update_data(selected_competition=competition)
        await state.set_state(RegistrationStates.waiting_for_role_select)

        available_roles: Any = competition["available_roles"]
        if isinstance(available_roles, str):
            available_roles = json.loads(available_roles)

        await message.answer(
            f"<b>📋 {BotMessages.format_competition_info(competition['name'], competition['type'])}</b>\n\n"
            f"{BotMessages.SELECT_ROLE}",
            reply_markup=InlineKeyboards.roles_keyboard(available_roles),
            parse_mode="HTML",
        )
    else:

        await message.answer(
            BotMessages.SELECT_COMPETITION,
            reply_markup=InlineKeyboards.competitions_keyboard(competitions),
            parse_mode="HTML",
        )

@competition_select_router.callback_query(F.data.startswith("competition_"))
async def competition_select_callback(query: CallbackQuery, state: FSMContext) -> None:

    competition_id: int = int(query.data.split("_")[1])

    competition: Optional[CompetitionModel] = await db_manager.get_competition_by_id(competition_id)

    if not competition:
        await query.answer("❌ Соревнование не найдено", show_alert=True)
        return

    from utils.serializers import CompetitionSerializer
    await state.update_data(selected_competition=CompetitionSerializer.serialize_for_selection(competition))

    await state.set_state(RegistrationStates.waiting_for_role_select)

    available_roles: Any = competition.available_roles
    if isinstance(available_roles, str):
        available_roles = json.loads(available_roles)

    await query.message.edit_text(
        f"<b>📋 {BotMessages.format_competition_info(competition.name, competition.competition_type)}</b>\n\n"
        f"{BotMessages.SELECT_ROLE}",
        reply_markup=InlineKeyboards.roles_keyboard(available_roles),
        parse_mode="HTML",
    )
    await query.answer()
