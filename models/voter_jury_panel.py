from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from models.user import Base

class VoterJuryPanelModel(Base):
    """Model for voter to jury panel assignment."""

    __tablename__: str = "voter_jury_panels"

    id: int = Column(Integer, primary_key=True)
    registration_id: int = Column(Integer, ForeignKey('registrations.id', ondelete='CASCADE'), nullable=False, index=True)
    jury_panel_id: int = Column(Integer, ForeignKey('jury_panels.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    def __str__(self) -> str:
        """String representation."""
        return f"Registration {self.registration_id} -> Panel {self.jury_panel_id}"

