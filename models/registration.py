from typing import Optional
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Boolean, UniqueConstraint, func
from datetime import datetime
import enum
from models.user import Base

class RegistrationStatus(str, enum.Enum):
    PENDING: str = "pending"
    APPROVED: str = "approved"
    REJECTED: str = "rejected"

class RegistrationModel(Base):

    __tablename__: str = "registrations"
    __table_args__ = (UniqueConstraint('user_id', 'competition_id', 'role', name='uq_user_comp_role'),)

    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    telegram_id: int = Column(BigInteger, nullable=False, index=True)
    competition_id: int = Column(Integer, ForeignKey('competitions.id', ondelete='CASCADE'), nullable=False, index=True)
    role: str = Column(String(50), nullable=False)
    is_confirmed: bool = Column(Boolean, default=False)
    status: str = Column(String(20), default=RegistrationStatus.PENDING.value)
    confirmed_at: Optional[datetime] = Column(DateTime, nullable=True)
    confirmed_by: Optional[int] = Column(BigInteger, nullable=True)
    created_at: datetime = Column(DateTime, server_default=func.now())
    updated_at: datetime = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __str__(self) -> str:
        return f"User {self.telegram_id} - Competition {self.competition_id} ({self.role})"
