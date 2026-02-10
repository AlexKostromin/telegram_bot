from typing import List, Dict, Any, Optional
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from messages import BotMessages

class InlineKeyboards:

    @staticmethod
    def yes_no_keyboard() -> InlineKeyboardMarkup:
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
        builder.button(text=BotMessages.BUTTON_YES, callback_data="yes")
        builder.button(text=BotMessages.BUTTON_NO, callback_data="no")
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def main_menu_keyboard() -> InlineKeyboardMarkup:
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
        builder.button(
            text=BotMessages.BUTTON_CONTACT_TEAM,
            callback_data="contact_team"
        )
        builder.button(
            text=BotMessages.BUTTON_REGISTER,
            callback_data="register"
        )
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def competitions_keyboard(competitions: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
        for comp in competitions:
            button_text: str = BotMessages.format_competition_info(
                comp.get("name"),
                comp.get("type", "")
            )
            builder.button(
                text=button_text,
                callback_data=f"competition_{comp.get('id')}"
            )
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def roles_keyboard(available_roles: List[str]) -> InlineKeyboardMarkup:
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
        role_map: Dict[str, str] = {
            "player": BotMessages.ROLE_PLAYER,
            "adviser": BotMessages.ROLE_ADVISER,
            "viewer": BotMessages.ROLE_VIEWER,
            "voter": BotMessages.ROLE_VOTER,
        }
        for role in available_roles:
            builder.button(
                text=role_map.get(role, role),
                callback_data=f"role_{role}"
            )
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def edit_fields_keyboard(available_fields: List[str]) -> InlineKeyboardMarkup:
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
        for field in available_fields:
            field_display: str = BotMessages.get_edit_field_name(field)
            builder.button(
                text=f"✏️ {field_display}",
                callback_data=f"edit_field_{field}"
            )
        builder.button(
            text=BotMessages.BUTTON_BACK_TO_MENU,
            callback_data="back_to_menu"
        )
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def back_to_menu_keyboard() -> InlineKeyboardMarkup:
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
        builder.button(
            text=BotMessages.BUTTON_BACK_TO_MENU,
            callback_data="back_to_menu"
        )
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def back_keyboard() -> InlineKeyboardMarkup:
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
        builder.button(
            text=BotMessages.BUTTON_BACK,
            callback_data="back"
        )
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def skip_keyboard() -> InlineKeyboardMarkup:
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
        builder.button(
            text="⏩ Пропустить",
            callback_data="skip_field"
        )
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def time_slots_keyboard(time_slots: List[Dict[str, Any]], selected_slots: Optional[List[int]] = None) -> InlineKeyboardMarkup:
        if selected_slots is None:
            selected_slots = []

        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        for slot_info in time_slots:
            slot: Any = slot_info.get("slot")
            assigned: int = slot_info.get("assigned", 0)
            available: int = slot_info.get("available", 0)

            is_selected: bool = slot.id in selected_slots
            checkbox: str = "✅" if is_selected else "⬜"

            button_text: str = (
                f"{checkbox} {slot.slot_day} {slot.start_time}-{slot.end_time} "
                f"({assigned}/{slot.max_voters})"
            )

            builder.button(
                text=button_text,
                callback_data=f"slot_toggle_{slot.id}"
            )

        builder.button(text="✔️ Подтвердить выбор", callback_data="slots_confirm")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def jury_panels_keyboard(panels: List[Any]) -> InlineKeyboardMarkup:
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        for panel in panels:
            button_text: str = f"{panel.panel_name}"
            builder.button(
                text=button_text,
                callback_data=f"panel_select_{panel.id}"
            )

        builder.adjust(1)
        return builder.as_markup()
