from typing import Optional
from datetime import datetime, date, time
from sqlalchemy import Column, Integer, Date, Time, Boolean, DateTime, ForeignKey, func
from models.user import Base

class TimeSlotModel(Base):

    __tablename__: str = "time_slots"

    id: int = Column(Integer, primary_key=True)
    competition_id: int = Column(Integer, ForeignKey('competitions.id', ondelete='CASCADE'), nullable=False, index=True)
    slot_day: date = Column(Date, nullable=False)
    start_time: time = Column(Time, nullable=False)
    end_time: time = Column(Time, nullable=False)
    max_voters: int = Column(Integer, default=10)
    is_active: bool = Column(Boolean, default=True)
    created_at: datetime = Column(DateTime, server_default=func.now())

    def __str__(self) -> str:
        return f"{self.slot_day} {self.start_time}-{self.end_time}"
