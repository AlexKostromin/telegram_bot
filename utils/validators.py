"""
Валидаторы для проверки данных пользователя.
"""
import re
from typing import Tuple, Union
from datetime import datetime, date
from messages import BotMessages

class Validators:
    """Класс с методами валидации."""

    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Валидировать номер телефона.

        Args:
            phone: Номер телефона

        Returns:
            Кортеж (is_valid, message)
        """
        pattern = r"^[+7|8]\d{10}$"
        phone_clean = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

        if re.match(pattern, phone_clean):
            return True, phone_clean
        return False, BotMessages.INVALID_INPUT

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Валидировать email.

        Args:
            email: Email адрес

        Returns:
            Кортеж (is_valid, message)
        """
        pattern: str = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if re.match(pattern, email):
            return True, email
        return False, BotMessages.INVALID_INPUT

    @staticmethod
    def validate_name(name: str, max_length: int = 50) -> Tuple[bool, str]:
        """
        Валидировать имя/фамилию.

        Args:
            name: Имя
            max_length: Максимальная длина

        Returns:
            Кортеж (is_valid, message)
        """
        if not name or len(name) > max_length or len(name) < 2:
            return False, BotMessages.INVALID_INPUT
        return True, name

    @staticmethod
    def validate_certificate_name(name: str) -> Tuple[bool, str]:
        """
        Валидировать имя для сертификата (латиница).

        Args:
            name: Имя для сертификата

        Returns:
            Кортеж (is_valid, message)
        """
        pattern: str = r"^[A-Za-z\s\-']+$"

        if len(name) < 3 or len(name) > 100:
            return False, BotMessages.INVALID_INPUT

        if re.match(pattern, name):
            return True, name
        return False, "Пожалуйста, используйте только латинские буквы, пробелы и дефисы."

    @staticmethod
    def validate_text_field(text: str, min_length: int = 1, max_length: int = 255) -> Tuple[bool, str]:
        """
        Валидировать текстовое поле.

        Args:
            text: Текст для проверки
            min_length: Минимальная длина
            max_length: Максимальная длина

        Returns:
            Кортеж (is_valid, message)
        """
        if len(text) < min_length or len(text) > max_length:
            return False, BotMessages.INVALID_INPUT
        return True, text

    @staticmethod
    def validate_date_of_birth(date_str: str) -> Tuple[bool, Union[date, str]]:
        """
        Валидировать дату рождения. Форматы: DD.MM.YYYY или YYYY-MM-DD

        Args:
            date_str: Строка с датой

        Returns:
            Кортеж (is_valid, date_object_or_message)
        """
        for fmt in ["%d.%m.%Y", "%Y-%m-%d"]:
            try:
                dob: date = datetime.strptime(date_str.strip(), fmt).date()

                today: date = date.today()
                if dob >= today:
                    return False, "❌ Дата рождения должна быть в прошлом"

                age: int = (today - dob).days // 365
                if age < 10 or age > 100:
                    return False, "❌ Дата рождения должна быть в разумном диапазоне (возраст 10-100 лет)"

                return True, dob
            except ValueError:
                continue

        return False, "❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ или ГГГГ-ММ-ДД"

    @staticmethod
    def validate_channel_name(channel: str) -> Tuple[bool, str]:
        """
        Валидировать имя Telegram канала. Формат: @channelname или channelname

        Args:
            channel: Имя канала

        Returns:
            Кортеж (is_valid, channel_name_or_message)
        """
        channel = channel.strip()

        if channel.startswith("@"):
            channel = channel[1:]

        if not re.match(r"^[a-zA-Z0-9_]{5,32}$", channel):
            return False, "❌ Имя канала должно содержать 5-32 символа (буквы, цифры, подчеркивание)"

        return True, channel

    @staticmethod
    def validate_bio(bio: str, max_length: int = 500) -> Tuple[bool, str]:
        """
        Валидировать биографию. Макс 500 символов

        Args:
            bio: Текст биографии
            max_length: Максимальная длина

        Returns:
            Кортеж (is_valid, message)
        """
        bio = bio.strip()

        if len(bio) == 0:
            return True, ""

        if len(bio) > max_length:
            return False, f"❌ Биография не должна превышать {max_length} символов"

        return True, bio
