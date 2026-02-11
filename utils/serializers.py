from typing import Optional, List, Any, Dict
from pydantic import BaseModel, ConfigDict, Field
from models import UserModel, CompetitionModel, RegistrationModel


# ============ User Schemas ============

class UserFull(BaseModel):
    """Полный профиль пользователя"""
    id: int
    telegram_id: int
    telegram_username: Optional[str] = None
    first_name: str
    last_name: str
    phone: str
    email: str
    country: str
    city: str
    club: str
    company: Optional[str] = None
    position: Optional[str] = None
    certificate_name: Optional[str] = None
    presentation: Optional[str] = None
    bio: Optional[str] = None
    date_of_birth: Optional[str] = None
    channel_name: Optional[str] = None
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserProfile(BaseModel):
    """Профиль для просмотра пользователем"""
    id: int
    first_name: str
    last_name: str
    telegram_username: Optional[str] = None
    phone: str
    email: str
    country: str
    city: str
    club: str
    company: Optional[str] = None
    position: Optional[str] = None
    bio: Optional[str] = None
    date_of_birth: Optional[str] = None
    channel_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserPublic(BaseModel):
    """Публичный профиль (минимум информации)"""
    id: int
    first_name: str
    last_name: str
    country: str
    city: str
    club: str

    model_config = ConfigDict(from_attributes=True)


# ============ Competition Schemas ============

class CompetitionFull(BaseModel):
    """Полная информация о соревновании"""
    id: int
    name: str
    description: Optional[str] = None
    competition_type: str
    available_roles: Dict[str, Any]
    player_entry_open: bool
    voter_entry_open: bool
    viewer_entry_open: bool
    adviser_entry_open: bool
    requires_time_slots: bool
    requires_jury_panel: bool
    is_active: bool
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CompetitionSelection(BaseModel):
    """Информация о соревновании для выбора"""
    id: int
    name: str
    description: Optional[str] = None
    type: str = Field(alias="competition_type")
    available_roles: Dict[str, Any]
    is_active: bool

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ============ Registration Schemas ============

class RegistrationFull(BaseModel):
    """Полная информация о регистрации"""
    id: int
    user_id: int
    telegram_id: int
    competition_id: int
    role: str
    status: str
    confirmed_at: Optional[str] = None
    confirmed_by: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RegistrationAdmin(BaseModel):
    """Регистрация для админ-панели"""
    id: int
    user_id: int
    competition_id: int
    role: str
    status: str
    confirmed_at: Optional[str] = None
    confirmed_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# ============ Serializers (обратная совместимость) ============

class UserSerializer:
    """Serializer for User models - теперь с Pydantic"""

    @staticmethod
    def serialize_full(user: UserModel) -> Dict[str, Any]:
        schema = UserFull.model_validate(user, from_attributes=True)
        return schema.model_dump()

    @staticmethod
    def serialize_profile(user: UserModel) -> Dict[str, Any]:
        schema = UserProfile.model_validate(user, from_attributes=True)
        return schema.model_dump()

    @staticmethod
    def serialize_public(user: UserModel) -> Dict[str, Any]:
        schema = UserPublic.model_validate(user, from_attributes=True)
        return schema.model_dump()


class CompetitionSerializer:
    """Serializer for Competition models - теперь с Pydantic"""

    @staticmethod
    def serialize_full(competition: CompetitionModel) -> Dict[str, Any]:
        schema = CompetitionFull.model_validate(competition, from_attributes=True)
        return schema.model_dump()

    @staticmethod
    def serialize_for_selection(competition: CompetitionModel) -> Dict[str, Any]:
        schema = CompetitionSelection.model_validate(competition, from_attributes=True)
        return schema.model_dump(by_alias=True)

    @staticmethod
    def serialize_list(competitions: List[CompetitionModel]) -> List[Dict[str, Any]]:
        return [
            CompetitionSerializer.serialize_for_selection(comp)
            for comp in competitions
        ]


class RegistrationSerializer:
    """Serializer for Registration models - теперь с Pydantic"""

    @staticmethod
    def serialize_full(registration: RegistrationModel) -> Dict[str, Any]:
        schema = RegistrationFull.model_validate(registration, from_attributes=True)
        return schema.model_dump()

    @staticmethod
    def serialize_admin_view(registration: RegistrationModel) -> Dict[str, Any]:
        schema = RegistrationAdmin.model_validate(registration, from_attributes=True)
        return schema.model_dump()
