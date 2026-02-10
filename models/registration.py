"""
Модель регистрации пользователя на соревнование.
"""
from typing import Optional
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Boolean
from datetime import datetime
import enum
from models.user import Base


class RegistrationStatus(str, enum.Enum):
    """Status of registration."""
    PENDING: str = "pending"
    APPROVED: str = "approved"
    REJECTED: str = "rejected"


class RegistrationModel(Base):
    """Модель регистрации пользователя на соревнование."""

    __tablename__: str = "registrations"

    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    telegram_id: int = Column(BigInteger, nullable=False, index=True)
    competition_id: int = Column(Integer, ForeignKey('competitions.id', ondelete='CASCADE'), nullable=False, index=True)
    role: str = Column(String(50), nullable=False)  # player, adviser, viewer, voter
    is_confirmed: bool = Column(Boolean, default=False)
    status: str = Column(String(20), default=RegistrationStatus.PENDING.value)  # pending, approved, rejected
    confirmed_at: Optional[datetime] = Column(DateTime, nullable=True)
    confirmed_by: Optional[int] = Column(BigInteger, nullable=True)  # admin telegram_id
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __str__(self) -> str:
        """Строковое представление регистрации."""
        return f"User {self.telegram_id} - Competition {self.competition_id} ({self.role})"