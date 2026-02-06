"""
Обработчик выбора соревнования при регистрации.
"""
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

# Создание роутера
competition_select_router = Router()


@competition_select_router.callback_query(F.data == "register")
async def register_callback_handler(query: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик нажатия на кнопку "Зарегистрироваться" в главном меню.

    Args:
        query: Объект callback query
        state: Контекст FSM
    """
    print(f"DEBUG: register callback received")
    # Получить активные соревнования
    competitions: List[Dict[str, Any]] = await db_manager.get_active_competitions()
    print(f"DEBUG: competitions = {competitions}")

    if not competitions:
        # Если нет активных соревнований
        await query.message.edit_text(
            BotMessages.NO_ACTIVE_COMPETITIONS,
            reply_markup=InlineKeyboards.main_menu_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    if len(competitions) == 1:
        # Если есть только одно соревнование, сразу переходим к выбору роли
        competition: Dict[str, Any] = competitions[0]
        await state.update_data(selected_competition=competition)
        await state.set_state(RegistrationStates.waiting_for_role_select)

        # Парсить available_roles если это JSON строка
        available_roles: Any = competition["available_roles"]
        if isinstance(available_roles, str):
            available_roles = json.loads(available_roles)

        await query.message.edit_text(
            f"📋 {BotMessages.format_competition_info(competition['name'], competition['type'])}\n\n"
            f"{BotMessages.SELECT_ROLE}",
            reply_markup=InlineKeyboards.roles_keyboard(available_roles),
        )
    else:
        # Если несколько соревнований, показать список
        await query.message.edit_text(
            BotMessages.SELECT_COMPETITION,
            reply_markup=InlineKeyboards.competitions_keyboard(competitions),
        )

    await query.answer()


@competition_select_router.message(StateFilter(RegistrationStates.waiting_for_competition_select))
async def competition_select_handler(message: Message, state: FSMContext) -> None:
    """
    Обработчик начала выбора соревнования.

    Args:
        message: Объект сообщения
        state: Контекст FSM
    """
    # Получить активные соревнования
    competitions: List[Dict[str, Any]] = await db_manager.get_active_competitions()

    if not competitions:
        # Если нет активных соревнований
        await message.answer(
            BotMessages.NO_ACTIVE_COMPETITIONS,
            reply_markup=InlineKeyboards.main_menu_keyboard(),
        )
        await state.clear()
        return

    if len(competitions) == 1:
        # Если есть только одно соревнование, сразу переходим к выбору роли
        competition: Dict[str, Any] = competitions[0]
        await state.update_data(selected_competition=competition)
        await state.set_state(RegistrationStates.waiting_for_role_select)

        # Парсить available_roles если это JSON строка
        available_roles: Any = competition["available_roles"]
        if isinstance(available_roles, str):
            available_roles = json.loads(available_roles)

        # Переход к выбору роли будет обработан в role_select.py
        await message.answer(
            f"📋 {BotMessages.format_competition_info(competition['name'], competition['type'])}\n\n"
            f"{BotMessages.SELECT_ROLE}",
            reply_markup=InlineKeyboards.roles_keyboard(available_roles),
        )
    else:
        # Если несколько соревнований, показать список
        await message.answer(
            BotMessages.SELECT_COMPETITION,
            reply_markup=InlineKeyboards.competitions_keyboard(competitions),
        )


@competition_select_router.callback_query(F.data.startswith("competition_"))
async def competition_select_callback(query: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик выбора соревнования из списка.

    Args:
        query: Объект callback query
        state: Контекст FSM
    """
    # Извлечь ID соревнования
    competition_id: int = int(query.data.split("_")[1])

    # Получить соревнование из БД
    competition: Optional[CompetitionModel] = await db_manager.get_competition_by_id(competition_id)

    if not competition:
        await query.answer("❌ Соревнование не найдено", show_alert=True)
        return

    # Сохранить выбранное соревнование в состояние
    from utils.serializers import CompetitionSerializer
    await state.update_data(selected_competition=CompetitionSerializer.serialize_for_selection(competition))

    # Перейти к выбору роли
    await state.set_state(RegistrationStates.waiting_for_role_select)

    # Парсить available_roles если это JSON строка
    available_roles: Any = competition.available_roles
    if isinstance(available_roles, str):
        available_roles = json.loads(available_roles)

    await query.message.edit_text(
        f"📋 {BotMessages.format_competition_info(competition.name, competition.competition_type)}\n\n"
        f"{BotMessages.SELECT_ROLE}",
        reply_markup=InlineKeyboards.roles_keyboard(available_roles),
    )
    await query.answer()