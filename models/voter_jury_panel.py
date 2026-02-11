from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, func
from models.user import Base

class VoterJuryPanelModel(Base):

    __tablename__: str = "voter_jury_panels"
    __table_args__ = (
        UniqueConstraint('registration_id', 'jury_panel_id', name='uq_voter_jury_panel'),
    )

    id: int = Column(Integer, primary_key=True)
    registration_id: int = Column(Integer, ForeignKey('registrations.id', ondelete='CASCADE'), nullable=False, index=True)
    jury_panel_id: int = Column(Integer, ForeignKey('jury_panels.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at: datetime = Column(DateTime, server_default=func.now())

    def __str__(self) -> str:
        return f"Registration {self.registration_id} -> Panel {self.jury_panel_id}"
