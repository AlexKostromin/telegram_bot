from datetime import date, datetime
from typing import Optional, List, Any, Dict, Union
from models import UserModel, CompetitionModel, RegistrationModel

class BaseSerializer:
    """Базовый класс сериализатора."""

    @staticmethod
    def serialize_date(value: Optional[date]) -> Optional[str]:
        """Преобразовать дату в ISO формат."""
        if not value:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        return value.isoformat() if value else None

    @staticmethod
    def serialize_datetime(value: Optional[datetime]) -> Optional[str]:
        """Преобразовать datetime в ISO формат."""
        return value.isoformat() if value else None

class UserSerializer(BaseSerializer):
    """Сериализатор для модели User."""

    @staticmethod
    def serialize_full(user: UserModel) -> Dict[str, Any]:
        """Полная сериализация пользователя (для admin панели)."""
        return {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "telegram_username": user.telegram_username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "email": user.email,
            "country": user.country,
            "city": user.city,
            "club": user.club,
            "company": user.company,
            "position": user.position,
            "certificate_name": user.certificate_name,
            "presentation": user.presentation,
            "bio": user.bio,
            "date_of_birth": BaseSerializer.serialize_date(user.date_of_birth),
            "channel_name": user.channel_name,
            "is_active": user.is_active,
            "created_at": BaseSerializer.serialize_datetime(user.created_at),
            "updated_at": BaseSerializer.serialize_datetime(user.updated_at),
        }

    @staticmethod
    def serialize_profile(user: UserModel) -> Dict[str, Any]:
        """Сериализация профиля пользователя (для отображения в боте)."""
        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "telegram_username": user.telegram_username,
            "phone": user.phone,
            "email": user.email,
            "country": user.country,
            "city": user.city,
            "club": user.club,
            "company": user.company,
            "position": user.position,
            "bio": user.bio,
            "date_of_birth": BaseSerializer.serialize_date(user.date_of_birth),
            "channel_name": user.channel_name,
        }

    @staticmethod
    def serialize_public(user: UserModel) -> Dict[str, Any]:
        """Публичная сериализация (минимальная информация)."""
        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "country": user.country,
            "city": user.city,
            "club": user.club,
        }

class CompetitionSerializer(BaseSerializer):
    """Сериализатор для модели Competition."""

    @staticmethod
    def serialize_full(competition: CompetitionModel) -> Dict[str, Any]:
        """Полная сериализация соревнования (для admin панели)."""
        return {
            "id": competition.id,
            "name": competition.name,
            "description": competition.description,
            "competition_type": competition.competition_type,
            "available_roles": competition.available_roles,
            "player_entry_open": competition.player_entry_open,
            "voter_entry_open": competition.voter_entry_open,
            "viewer_entry_open": competition.viewer_entry_open,
            "adviser_entry_open": competition.adviser_entry_open,
            "requires_time_slots": competition.requires_time_slots,
            "requires_jury_panel": competition.requires_jury_panel,
            "is_active": competition.is_active,
            "start_date": BaseSerializer.serialize_datetime(competition.start_date),
            "end_date": BaseSerializer.serialize_datetime(competition.end_date),
            "created_at": BaseSerializer.serialize_datetime(competition.created_at),
        }

    @staticmethod
    def serialize_for_selection(competition: CompetitionModel) -> Dict[str, Any]:
        """Сериализация для выбора соревнования (регистрация)."""
        return {
            "id": competition.id,
            "name": competition.name,
            "description": competition.description,
            "type": competition.competition_type,
            "available_roles": competition.available_roles,
            "is_active": competition.is_active,
        }

    @staticmethod
    def serialize_list(competitions: List[CompetitionModel]) -> List[Dict[str, Any]]:
        """Сериализация списка соревнований."""
        return [
            CompetitionSerializer.serialize_for_selection(comp)
            for comp in competitions
        ]

class RegistrationSerializer(BaseSerializer):
    """Сериализатор для модели Registration."""

    @staticmethod
    def serialize_full(registration: RegistrationModel) -> Dict[str, Any]:
        """Полная сериализация заявки."""
        return {
            "id": registration.id,
            "user_id": registration.user_id,
            "telegram_id": registration.telegram_id,
            "competition_id": registration.competition_id,
            "role": registration.role,
            "status": registration.status,
            "confirmed_at": BaseSerializer.serialize_datetime(registration.confirmed_at),
            "confirmed_by": registration.confirmed_by,
            "created_at": BaseSerializer.serialize_datetime(registration.created_at),
            "updated_at": BaseSerializer.serialize_datetime(registration.updated_at),
        }

    @staticmethod
    def serialize_admin_view(registration: RegistrationModel) -> Dict[str, Any]:
        """Сериализация заявки для админ панели."""
        return {
            "id": registration.id,
            "user_id": registration.user_id,
            "competition_id": registration.competition_id,
            "role": registration.role,
            "status": registration.status,
            "confirmed_at": BaseSerializer.serialize_datetime(registration.confirmed_at),
            "confirmed_by": registration.confirmed_by,
        }

