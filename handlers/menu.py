from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from messages import BotMessages
from keyboards import InlineKeyboards
from states import ContactStates, RegistrationStates

menu_router = Router()

@menu_router.callback_query(F.data == "back_to_menu")
async def back_to_menu_handler(query: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик кнопки "В главное меню".

    Args:
        query: Объект callback query
        state: Контекст FSM
    """
    await state.clear()
    await query.message.edit_text(
        BotMessages.MAIN_MENU,
        reply_markup=InlineKeyboards.main_menu_keyboard(),
    )
    await query.answer()

@menu_router.callback_query(F.data == "contact_team")
async def contact_team_handler(query: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик кнопки "Связаться с командой USN".

    Args:
        query: Объект callback query
        state: Контекст FSM
    """
    await state.set_state(ContactStates.waiting_for_message)
    await query.message.edit_text(
        BotMessages.CONTACT_REQUEST_MESSAGE,
        reply_markup=InlineKeyboards.back_keyboard(),
    )
    await query.answer()

@menu_router.callback_query(F.data == "back")
async def back_handler(query: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик кнопки "Назад".

    Args:
        query: Объект callback query
        state: Контекст FSM
    """
    current_state = await state.get_state()

    if current_state == ContactStates.waiting_for_message:
        await state.clear()
        await query.message.edit_text(
            BotMessages.MAIN_MENU,
            reply_markup=InlineKeyboards.main_menu_keyboard(),
        )
    else:

        await state.clear()
        await query.message.edit_text(
            BotMessages.MAIN_MENU,
            reply_markup=InlineKeyboards.main_menu_keyboard(),
        )

    await query.answer()

