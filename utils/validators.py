import re
from typing import Tuple, Union, Optional
from datetime import datetime, date
from pydantic import BaseModel, field_validator, Field
from messages import BotMessages


class UserInputValidators(BaseModel):
    """Pydantic models for validating user input"""

    class PhoneInput(BaseModel):
        phone: str = Field(..., min_length=11, max_length=20)

        @field_validator("phone")
        @classmethod
        def validate_phone_format(cls, v: str) -> str:
            pattern = r"^(\+7|8)\d{10}$"
            phone_clean = v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            if not re.match(pattern, phone_clean):
                raise ValueError("Invalid phone number format. Use +7XXXXXXXXXX or 8XXXXXXXXXX")
            return phone_clean

    class EmailInput(BaseModel):
        email: str = Field(..., min_length=5, max_length=255)

        @field_validator("email")
        @classmethod
        def validate_email_format(cls, v: str) -> str:
            pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(pattern, v):
                raise ValueError("Invalid email format")
            return v

    class NameInput(BaseModel):
        name: str = Field(..., min_length=2, max_length=50)

        @field_validator("name")
        @classmethod
        def validate_name_format(cls, v: str) -> str:
            v = v.strip()
            if len(v) < 2 or len(v) > 50:
                raise ValueError("Name must be between 2 and 50 characters")
            return v

    class CertificateNameInput(BaseModel):
        name: str = Field(..., min_length=3, max_length=100)

        @field_validator("name")
        @classmethod
        def validate_certificate_format(cls, v: str) -> str:
            pattern = r"^[A-Za-z\s\-']+$"
            if len(v) < 3 or len(v) > 100:
                raise ValueError("Certificate name must be between 3 and 100 characters")
            if not re.match(pattern, v):
                raise ValueError("Certificate name must contain only Latin letters, spaces, and hyphens")
            return v

    class TextInput(BaseModel):
        text: str = Field(..., min_length=1, max_length=255)

        @field_validator("text")
        @classmethod
        def validate_text_length(cls, v: str, info) -> str:
            min_length = info.context.get("min_length", 1) if info.context else 1
            max_length = info.context.get("max_length", 255) if info.context else 255
            if len(v) < min_length or len(v) > max_length:
                raise ValueError(f"Text must be between {min_length} and {max_length} characters")
            return v

    class DateOfBirthInput(BaseModel):
        date_str: str

        @field_validator("date_str")
        @classmethod
        def validate_dob_format(cls, v: str) -> date:
            for fmt in ["%d.%m.%Y", "%Y-%m-%d"]:
                try:
                    dob = datetime.strptime(v.strip(), fmt).date()
                    today = date.today()

                    if dob >= today:
                        raise ValueError("Date of birth must be in the past")

                    age = (today - dob).days // 365
                    if age < 10 or age > 100:
                        raise ValueError("Age must be between 10 and 100 years")

                    return dob
                except ValueError:
                    continue

            raise ValueError("Invalid date format. Use DD.MM.YYYY or YYYY-MM-DD")

    class ChannelNameInput(BaseModel):
        channel: str = Field(..., min_length=5, max_length=32)

        @field_validator("channel")
        @classmethod
        def validate_channel_format(cls, v: str) -> str:
            channel = v.strip()
            if channel.startswith("@"):
                channel = channel[1:]

            if not re.match(r"^[a-zA-Z0-9_]{5,32}$", channel):
                raise ValueError("Channel name must be 5-32 characters (letters, numbers, underscore)")
            return channel

    class BioInput(BaseModel):
        bio: str = Field(default="", max_length=500)

        @field_validator("bio")
        @classmethod
        def validate_bio_length(cls, v: str) -> str:
            v = v.strip()
            if len(v) > 500:
                raise ValueError("Bio must not exceed 500 characters")
            return v


class Validators:

    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        pattern = r"^(\+7|8)\d{10}$"
        phone_clean = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

        if re.match(pattern, phone_clean):
            return True, phone_clean
        return False, BotMessages.INVALID_INPUT

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        pattern: str = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if re.match(pattern, email):
            return True, email
        return False, BotMessages.INVALID_INPUT

    @staticmethod
    def validate_name(name: str, max_length: int = 50) -> Tuple[bool, str]:
        if not name or len(name) > max_length or len(name) < 2:
            return False, BotMessages.INVALID_INPUT
        return True, name

    @staticmethod
    def validate_certificate_name(name: str) -> Tuple[bool, str]:
        pattern: str = r"^[A-Za-z\s\-']+$"

        if len(name) < 3 or len(name) > 100:
            return False, BotMessages.INVALID_INPUT

        if re.match(pattern, name):
            return True, name
        return False, "Пожалуйста, используйте только латинские буквы, пробелы и дефисы."

    @staticmethod
    def validate_text_field(text: str, min_length: int = 1, max_length: int = 255) -> Tuple[bool, str]:
        if len(text) < min_length or len(text) > max_length:
            return False, BotMessages.INVALID_INPUT
        return True, text

    @staticmethod
    def validate_date_of_birth(date_str: str) -> Tuple[bool, Union[date, str]]:
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
        channel = channel.strip()

        if channel.startswith("@"):
            channel = channel[1:]

        if not re.match(r"^[a-zA-Z0-9_]{5,32}$", channel):
            return False, "❌ Имя канала должно содержать 5-32 символа (буквы, цифры, подчеркивание)"

        return True, channel

    @staticmethod
    def validate_bio(bio: str, max_length: int = 500) -> Tuple[bool, str]:
        bio = bio.strip()

        if len(bio) == 0:
            return True, ""

        if len(bio) > max_length:
            return False, f"❌ Биография не должна превышать {max_length} символов"

        return True, bio
