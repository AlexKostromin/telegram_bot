"""
Модель соревнования для Telegram бота.
"""
from typing import Dict, Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from datetime import datetime
from models.user import Base


class CompetitionModel(Base):
    """Модель соревнования в системе."""

    __tablename__: str = "competitions"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(255), nullable=False)
    description: Optional[str] = Column(String(500), nullable=True)
    competition_type: str = Column(String(50), nullable=False)  # classic_game, puzzle, etc.
    available_roles: List = Column(JSON, nullable=False)  # ["player", "adviser", "viewer", "voter"]
    player_entry_open: bool = Column(Boolean, default=True)
    voter_entry_open: bool = Column(Boolean, default=True)
    viewer_entry_open: bool = Column(Boolean, default=True)
    adviser_entry_open: bool = Column(Boolean, default=True)
    requires_time_slots: bool = Column(Boolean, default=False)
    requires_jury_panel: bool = Column(Boolean, default=False)
    is_active: bool = Column(Boolean, default=True)
    start_date: Optional[datetime] = Column(DateTime, nullable=True)
    end_date: Optional[datetime] = Column(DateTime, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __str__(self) -> str:
        """Строковое представление соревнования."""
        return f"{self.name} ({self.competition_type})"

    def is_role_open(self, role: str) -> bool:
        """Check if registration is open for specific role."""
        role_flags: Dict[str, bool] = {
            "player": self.player_entry_open,
            "voter": self.voter_entry_open,
            "viewer": self.viewer_entry_open,
            "adviser": self.adviser_entry_open,
        }
        return role_flags.get(role, False)