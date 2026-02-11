from aiogram.types import User
from typing import Optional, List, Dict, Any

CERTIFICATE_REQUIRED_ROLES = ["player", "voter"]


def parse_callback_id(callback_data: str, separator: str = "_", index: int = -1) -> Optional[int]:
    try:
        return int(callback_data.split(separator)[index])
    except (IndexError, ValueError, AttributeError):
        return None


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

        if role in CERTIFICATE_REQUIRED_ROLES:
            fields.extend(["certificate_name", "presentation"])

        return fields

    @staticmethod
    def format_user_confirmation_from_model(user, state_data: Dict[str, Any]) -> str:
        include_certificate = state_data.get("certificate_name") is not None
        return BotHelpers.format_user_data(
            user.first_name,
            user.last_name,
            user.telegram_username or "@-",
            user.phone,
            user.email,
            user.country,
            user.city,
            user.club,
            user.company or "-",
            user.position or "-",
            user.certificate_name if include_certificate else None,
            user.presentation if include_certificate else None,
            include_certificate,
        )

    @staticmethod
    def format_application_detail(registration_data: Dict[str, Any]) -> str:
        status_emoji: Dict[str, str] = {
            "pending": "🕐",
            "approved": "✅",
            "rejected": "❌",
        }
        status: str = registration_data.get("status", "pending")
        emoji: str = status_emoji.get(status, "❓")

        text: str = (
            f"<b>📋 Заявка #{registration_data.get('registration_id', '?')}</b>\n\n"
            f"👤 {registration_data.get('first_name', '')} {registration_data.get('last_name', '')}\n"
            f"🎭 Роль: {registration_data.get('role', '—')}\n"
            f"{emoji} Статус: {status}\n"
            f"🏆 Соревнование: {registration_data.get('competition_name', '—')}\n\n"
            f"📧 Email: {registration_data.get('email', '—')}\n"
            f"📱 Телефон: {registration_data.get('phone', '—')}\n"
            f"💬 Telegram: {registration_data.get('telegram_username', '—')}\n"
        )

        if registration_data.get("bio"):
            text += f"📝 О себе: {registration_data['bio']}\n"

        if registration_data.get("confirmed_at"):
            text += f"\n🕐 Подтверждено: {registration_data['confirmed_at']}"
        if registration_data.get("confirmed_by"):
            text += f"\n👤 Подтвердил: {registration_data['confirmed_by']}"

        return text
