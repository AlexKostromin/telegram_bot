"""
Admin panel keyboards.
"""
from typing import List, Any
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main admin menu keyboard."""
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    builder.button(text="📬 Заявки", callback_data="admin_applications")
    builder.button(text="🏆 Соревнования", callback_data="admin_competitions")
    builder.button(text="🕐 Временные слоты", callback_data="admin_time_slots")
    builder.button(text="⬅️ В главное меню", callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup()


def applications_list_keyboard(applications: List[Any]) -> InlineKeyboardMarkup:
    """Keyboard with list of applications."""
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for app in applications:
        user_name: str = f"{app.first_name if hasattr(app, 'first_name') else 'User'} (ID: {app.id})"
        builder.button(
            text=f"👤 {user_name}",
            callback_data=f"app_view_{app.id}"
        )

    builder.button(text="⬅️ Назад", callback_data="admin_menu")
    builder.adjust(1)
    return builder.as_markup()


def application_actions_keyboard(registration_id: int, status: str) -> InlineKeyboardMarkup:
    """Keyboard with actions for application."""
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    if status == "pending":
        builder.button(text="✅ Одобрить", callback_data=f"app_approve_{registration_id}")
        builder.button(text="❌ Отклонить", callback_data=f"app_reject_{registration_id}")
    elif status == "approved":
        builder.button(text="⚠️ Отозвать", callback_data=f"app_revoke_{registration_id}")

    builder.button(text="⬅️ Назад", callback_data="admin_applications")
    builder.adjust(1)
    return builder.as_markup()


def competition_management_keyboard(competition: Any) -> InlineKeyboardMarkup:
    """Keyboard for competition management."""
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    # Role entry toggles
    player_status: str = "✅" if competition.player_entry_open else "❌"
    voter_status: str = "✅" if competition.voter_entry_open else "❌"
    viewer_status: str = "✅" if competition.viewer_entry_open else "❌"
    adviser_status: str = "✅" if competition.adviser_entry_open else "❌"

    builder.button(
        text=f"Player {player_status}",
        callback_data=f"toggle_entry_{competition.id}_player"
    )
    builder.button(
        text=f"Voter {voter_status}",
        callback_data=f"toggle_entry_{competition.id}_voter"
    )
    builder.button(
        text=f"Viewer {viewer_status}",
        callback_data=f"toggle_entry_{competition.id}_viewer"
    )
    builder.button(
        text=f"Adviser {adviser_status}",
        callback_data=f"toggle_entry_{competition.id}_adviser"
    )

    builder.button(text="🕐 Управление слотами", callback_data=f"comp_slots_{competition.id}")
    builder.button(text="⬅️ Назад", callback_data="admin_competitions")
    builder.adjust(2)
    return builder.as_markup()


def time_slot_management_keyboard(competition_id: int) -> InlineKeyboardMarkup:
    """Keyboard for time slot management."""
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить слот", callback_data="create_time_slot")
    builder.button(text="📋 Список слотов", callback_data=f"list_slots_{competition_id}")
    builder.button(text="⬅️ Назад", callback_data="admin_competitions")
    builder.adjust(1)
    return builder.as_markup()


def confirm_action_keyboard(action: str, data: str) -> InlineKeyboardMarkup:
    """Keyboard for action confirmation."""
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data=f"confirm_{action}_{data}")
    builder.button(text="❌ Нет", callback_data="admin_menu")
    builder.adjust(2)
    return builder.as_markup()


def back_button() -> InlineKeyboardMarkup:
    """Simple back button."""
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data="admin_menu")
    builder.adjust(1)
    return builder.as_markup()
