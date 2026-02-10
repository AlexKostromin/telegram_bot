from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from messages import BotMessages

class ReplyKeyboards:
    """Класс с reply-клавиатурами."""

    @staticmethod
    def yes_no_keyboard() -> ReplyKeyboardMarkup:
        """Reply клавиатура Да/Нет."""
        builder = ReplyKeyboardBuilder()
        builder.button(text=BotMessages.BUTTON_YES)
        builder.button(text=BotMessages.BUTTON_NO)
        builder.adjust(2)
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def back_to_menu_keyboard() -> ReplyKeyboardMarkup:
        """Reply клавиатура с кнопкой возврата в меню."""
        builder = ReplyKeyboardBuilder()
        builder.button(text=BotMessages.BUTTON_BACK_TO_MENU)
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def back_keyboard() -> ReplyKeyboardMarkup:
        """Reply клавиатура с кнопкой назад."""
        builder = ReplyKeyboardBuilder()
        builder.button(text=BotMessages.BUTTON_BACK)
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def cancel_keyboard() -> ReplyKeyboardMarkup:
        """Reply клавиатура отмены."""
        builder = ReplyKeyboardBuilder()
        builder.button(text="❌ Отмена")
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)

