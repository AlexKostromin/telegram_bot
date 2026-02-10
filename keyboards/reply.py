from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from messages import BotMessages

class ReplyKeyboards:

    @staticmethod
    def yes_no_keyboard() -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        builder.button(text=BotMessages.BUTTON_YES)
        builder.button(text=BotMessages.BUTTON_NO)
        builder.adjust(2)
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def back_to_menu_keyboard() -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        builder.button(text=BotMessages.BUTTON_BACK_TO_MENU)
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def back_keyboard() -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        builder.button(text=BotMessages.BUTTON_BACK)
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def cancel_keyboard() -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        builder.button(text="❌ Отмена")
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)
