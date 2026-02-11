from typing import Dict, Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, func
from datetime import datetime
from models.user import Base

class CompetitionModel(Base):

    __tablename__: str = "competitions"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(255), nullable=False)
    description: Optional[str] = Column(String(500), nullable=True)
    competition_type: str = Column(String(50), nullable=False)
    available_roles: List = Column(JSON, nullable=False)
    player_entry_open: bool = Column(Boolean, default=True)
    voter_entry_open: bool = Column(Boolean, default=True)
    viewer_entry_open: bool = Column(Boolean, default=True)
    adviser_entry_open: bool = Column(Boolean, default=True)
    requires_time_slots: bool = Column(Boolean, default=False)
    requires_jury_panel: bool = Column(Boolean, default=False)
    is_active: bool = Column(Boolean, default=True)
    start_date: Optional[datetime] = Column(DateTime, nullable=True)
    end_date: Optional[datetime] = Column(DateTime, nullable=True)
    created_at: datetime = Column(DateTime, server_default=func.now())
    updated_at: datetime = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __str__(self) -> str:
        return f"{self.name} ({self.competition_type})"

    def is_role_open(self, role: str) -> bool:
        role_flags: Dict[str, bool] = {
            "player": self.player_entry_open,
            "voter": self.voter_entry_open,
            "viewer": self.viewer_entry_open,
            "adviser": self.adviser_entry_open,
        }
        return role_flags.get(role, False)

    def get_available_roles(self) -> List[str]:
        roles: List[str] = []
        if self.player_entry_open:
            roles.append("player")
        if self.voter_entry_open:
            roles.append("voter")
        if self.viewer_entry_open:
            roles.append("viewer")
        if self.adviser_entry_open:
            roles.append("adviser")
        return roles
