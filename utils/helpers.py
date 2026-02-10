from aiogram.types import User
from typing import Optional, List, Dict, Any
from datetime import datetime

class BotHelpers:

    @staticmethod
    def get_telegram_username(user: User) -> str:
        if user.username:
            return f"@{user.username}"
        return ""

    @staticmethod
    def get_user_phone_from_contact(contact: Dict[str, Any]) -> Optional[str]:
        return contact.get("phone_number") if contact else None

    @staticmethod
    def format_user_data(
        first_name: str,
        last_name: str,
        telegram_username: str,
        phone: str,
        email: str,
        country: str,
        city: str,
        club: str,
        company: str,
        position: str,
        certificate_name: Optional[str] = None,
        presentation: Optional[str] = None,
        include_certificate: bool = False,
    ) -> str:
        certificate_section = ""
        if include_certificate and certificate_name:
            certificate_section = f"📜 Имя для сертификата (лат.): {certificate_name}\n"

        presentation_value = presentation if presentation else "Не указано"

        return (
            f"Добрый день, {first_name} {last_name}!\n\n"
            f"Пожалуйста, проверьте ваши данные для регистрации:\n\n"
            f"👤 Имя пользователя Telegram: {telegram_username}\n"
            f"📱 Телефон: {phone}\n"
            f"📧 Email: {email}\n"
            f"🌍 Страна: {country}\n"
            f"🏙️ Город: {city}\n"
            f"🏫 Клуб/школа: {club}\n"
            f"{certificate_section}"
            f"🏢 Компания: {company}\n"
            f"💼 Должность: {position}\n"
            f"🎤 Как вас представить: {presentation_value}\n\n"
            f"Всё верно?"
        )

    @staticmethod
    def get_available_roles_for_competition(competition_type: str) -> List[str]:
        base_roles: List[str] = ["player", "viewer", "voter"]

        if competition_type.lower() == "classic_game":
            base_roles.insert(1, "adviser")

        return base_roles

    @staticmethod
    def get_edit_fields_for_role(role: str) -> List[str]:
        fields: List[str] = [
            "phone",
            "email",
            "country",
            "city",
            "club",
            "company",
            "position",
        ]

        if role in ["player", "voter"]:
            fields.insert(7, "certificate_name")
            fields.insert(8, "presentation")

        return fields

    @staticmethod
    def format_application_detail(registration_data: Dict[str, Any]) -> str:

        if registration_data.get('bio'):
            text += f"\n📝 О себе: {registration_data.get('bio')}"

        return text
