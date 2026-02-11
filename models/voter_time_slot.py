from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, func
from models.user import Base

class VoterTimeSlotModel(Base):

    __tablename__: str = "voter_time_slots"
    __table_args__ = (
        UniqueConstraint('registration_id', 'time_slot_id', name='uq_voter_time_slot'),
    )

    id: int = Column(Integer, primary_key=True)
    registration_id: int = Column(Integer, ForeignKey('registrations.id', ondelete='CASCADE'), nullable=False, index=True)
    time_slot_id: int = Column(Integer, ForeignKey('time_slots.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at: datetime = Column(DateTime, server_default=func.now())

    def __str__(self) -> str:
        return f"Registration {self.registration_id} -> Slot {self.time_slot_id}"
