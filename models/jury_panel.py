"""
Model for jury panel management.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from models.user import Base


class JuryPanelModel(Base):
    """Model for jury panels in competitions."""

    __tablename__: str = "jury_panels"

    id: int = Column(Integer, primary_key=True)
    competition_id: int = Column(Integer, ForeignKey('competitions.id', ondelete='CASCADE'), nullable=False, index=True)
    panel_name: str = Column(String(100), nullable=False)
    max_voters: int = Column(Integer, default=5)
    is_active: bool = Column(Boolean, default=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    def __str__(self) -> str:
        """String representation of jury panel."""
        return f"{self.panel_name} (max {self.max_voters})"
