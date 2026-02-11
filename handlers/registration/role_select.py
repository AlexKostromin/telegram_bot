from typing import Optional, Dict, Any, Union
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from messages import BotMessages
from keyboards import InlineKeyboards
from states import RegistrationStates
from utils import db_manager
from models import UserModel, CompetitionModel

role_select_router = Router()

@role_select_router.callback_query(F.data.startswith("role_"), RegistrationStates.waiting_for_role_select)
async def role_select_callback(query: CallbackQuery, state: FSMContext) -> None:

    selected_role: str = query.data.split("_")[1]

    data: Dict[str, Any] = await state.get_data()
    competition_data: Union[Dict[str, Any], int] = data.get('selected_competition')

    competition_id: int
    if isinstance(competition_data, dict):
        competition_id = competition_data.get('id')
    else:
        competition_id = competition_data

    competition: Optional[CompetitionModel] = await db_manager.get_competition_by_id(competition_id)

    if competition and not competition.is_role_open(selected_role):
        await query.answer("⚠️ Регистрация для этой роли закрыта", show_alert=True)
        return

    await state.update_data(selected_role=selected_role)

    user_telegram_id: int = query.from_user.id

    existing_user: Optional[UserModel] = await db_manager.get_user_by_telegram_id(user_telegram_id)

    if existing_user:

        await state.set_state(RegistrationStates.waiting_for_existing_user_confirmation)
        await query.message.edit_text(
            f"<b>Проверка данных</b>\n"
            f"━━━━━━━━━━━━━━━━━\n\n"
            f"Добрый день, <b>{existing_user.first_name} {existing_user.last_name}</b>!\n\n"
            f"👤 Telegram: {existing_user.telegram_username or '@-'}\n"
            f"📱 Телефон: {existing_user.phone}\n"
            f"📧 Email: {existing_user.email}\n"
            f"🌍 Страна: {existing_user.country}\n"
            f"🏙️ Город: {existing_user.city}\n"
            f"🏫 Клуб/школа: {existing_user.club}\n"
            f"{f'📜 Сертификат (лат.): {existing_user.certificate_name}' if selected_role in ['player', 'voter'] and existing_user.certificate_name else ''}\n"
            f"🏢 Компания: {existing_user.company or '-'}\n"
            f"💼 Должность: {existing_user.position or '-'}\n"
            f"🎤 Представление: {existing_user.presentation or '-'}\n\n"
            f"━━━━━━━━━━━━━━━━━\n\n"
            f"<i>Всё верно?</i>",
            reply_markup=InlineKeyboards.yes_no_keyboard(),
            parse_mode="HTML",
        )
    else:

        await state.set_state(RegistrationStates.waiting_for_first_name)
        await query.message.edit_text(
            BotMessages.REQUEST_FIRST_NAME,
            reply_markup=InlineKeyboards.back_keyboard(),
            parse_mode="HTML",
        )

    await query.answer()
