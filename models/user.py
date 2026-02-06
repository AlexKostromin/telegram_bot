"""
Модель пользователя для Telegram бота.
"""
from typing import Optional
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date

Base = declarative_base()


class UserModel(Base):
    """Модель пользователя в системе."""

    __tablename__: str = "users"

    id: int = Column(Integer, primary_key=True)
    telegram_id: int = Column(BigInteger, unique=True, nullable=False, index=True)
    telegram_username: Optional[str] = Column(String(255), nullable=True)
    first_name: str = Column(String(100), nullable=False)
    last_name: str = Column(String(100), nullable=False)
    phone: str = Column(String(20), nullable=False, unique=True)
    email: str = Column(String(255), nullable=False, unique=True)
    country: str = Column(String(100), nullable=False)
    city: str = Column(String(100), nullable=False)
    club: str = Column(String(255), nullable=False)
    company: Optional[str] = Column(String(255), nullable=True)
    position: Optional[str] = Column(String(255), nullable=True)
    certificate_name: Optional[str] = Column(String(255), nullable=True)
    presentation: Optional[str] = Column(String(500), nullable=True)
    bio: Optional[str] = Column(Text, nullable=True)
    date_of_birth: Optional[date] = Column(Date, nullable=True)
    channel_name: Optional[str] = Column(String(255), nullable=True)
    is_active: bool = Column(Boolean, default=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __str__(self) -> str:
        """Строковое представление пользователя."""
        return f"{self.first_name} {self.last_name} ({self.telegram_username})"

    def get_display_name(self) -> str:
        """Получить отображаемое имя пользователя."""
        return f"{self.first_name} {self.last_name}"