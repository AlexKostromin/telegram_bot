from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, Boolean, JSON, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

from models.user import Base

class BroadcastStatus(PyEnum):
    draft = "draft"
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"

class DeliveryStatus(PyEnum):
    pending = "pending"
    sent = "sent"
    delivered = "delivered"
    failed = "failed"
    blocked = "blocked"

class MessageTemplate(Base):

    __tablename__: str = "message_templates"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(255), unique=True, nullable=False, index=True)
    description: Optional[str] = Column(Text, nullable=True)

    subject: str = Column(String(500), nullable=False)
    body_telegram: str = Column(Text, nullable=False)
    body_email: str = Column(Text, nullable=False)

    available_variables: Dict[str, str] = Column(JSON, nullable=False, default={})

    is_active: bool = Column(Boolean, default=True, index=True)

    created_by: Optional[int] = Column(Integer, nullable=True)
    created_at: datetime = Column(DateTime, server_default=func.now(), index=True)
    updated_at: datetime = Column(DateTime, server_default=func.now(), onupdate=func.now())

    broadcasts = relationship("Broadcast", back_populates="template")

    def __str__(self) -> str:
        return f"MessageTemplate({self.name})"

    def __repr__(self) -> str:
        return f"<MessageTemplate id={self.id} name='{self.name}' is_active={self.is_active}>"

class Broadcast(Base):

    __tablename__: str = "broadcasts"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(255), nullable=False, index=True)

    template_id: int = Column(Integer, ForeignKey("message_templates.id"), nullable=False)
    template = relationship("MessageTemplate", back_populates="broadcasts")

    filters: Dict[str, Any] = Column(JSON, nullable=False, default={})

    send_telegram: bool = Column(Boolean, default=True)
    send_email: bool = Column(Boolean, default=False)

    scheduled_at: Optional[datetime] = Column(DateTime, nullable=True)

    status: BroadcastStatus = Column(Enum(BroadcastStatus), default=BroadcastStatus.draft, index=True)

    total_recipients: int = Column(Integer, default=0)
    sent_count: int = Column(Integer, default=0)
    failed_count: int = Column(Integer, default=0)

    started_at: Optional[datetime] = Column(DateTime, nullable=True)
    completed_at: Optional[datetime] = Column(DateTime, nullable=True)

    created_by: int = Column(Integer, nullable=False)
    created_at: datetime = Column(DateTime, server_default=func.now(), index=True)
    updated_at: datetime = Column(DateTime, server_default=func.now(), onupdate=func.now())

    recipients = relationship("BroadcastRecipient", back_populates="broadcast", cascade="all, delete-orphan")

    def __str__(self) -> str:
        return f"Broadcast({self.name}, status={self.status.value})"

    def __repr__(self) -> str:
        return (
            f"<Broadcast id={self.id} name='{self.name}' "
            f"status={self.status.value} template_id={self.template_id}>"
        )

    def get_progress_percent(self) -> float:
        if self.total_recipients == 0:
            return 0.0
        return min(100.0, (self.sent_count / self.total_recipients) * 100)

    def is_completed(self) -> bool:
        return self.status in (BroadcastStatus.completed, BroadcastStatus.failed)

class BroadcastRecipient(Base):

    __tablename__: str = "broadcast_recipients"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True)

    broadcast_id: int = Column(Integer, ForeignKey("broadcasts.id"), nullable=False, index=True)
    broadcast = relationship("Broadcast", back_populates="recipients")

    user_id: int = Column(Integer, nullable=False, index=True)
    telegram_id: int = Column(BigInteger, nullable=False, index=True)

    telegram_status: DeliveryStatus = Column(
        Enum(DeliveryStatus),
        default=DeliveryStatus.pending,
        index=True
    )
    telegram_sent_at: Optional[datetime] = Column(DateTime, nullable=True)
    telegram_error: Optional[str] = Column(Text, nullable=True)
    telegram_message_id: Optional[int] = Column(Integer, nullable=True)

    email_status: DeliveryStatus = Column(
        Enum(DeliveryStatus),
        default=DeliveryStatus.pending,
        index=True
    )
    email_sent_at: Optional[datetime] = Column(DateTime, nullable=True)
    email_error: Optional[str] = Column(Text, nullable=True)
    email_address: Optional[str] = Column(String(255), nullable=True)

    rendered_subject: Optional[str] = Column(String(500), nullable=True)
    rendered_body: Optional[str] = Column(Text, nullable=True)

    created_at: datetime = Column(DateTime, server_default=func.now(), index=True)
    updated_at: datetime = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __str__(self) -> str:
        return f"BroadcastRecipient(user_id={self.user_id}, broadcast_id={self.broadcast_id})"

    def __repr__(self) -> str:
        return (
            f"<BroadcastRecipient id={self.id} broadcast_id={self.broadcast_id} "
            f"user_id={self.user_id} tg_status={self.telegram_status.value} "
            f"email_status={self.email_status.value}>"
        )

    def is_sent(self) -> bool:
        return (
            self.telegram_status in (DeliveryStatus.sent, DeliveryStatus.delivered) or
            self.email_status in (DeliveryStatus.sent, DeliveryStatus.delivered)
        )

    def has_errors(self) -> bool:
        return (
            self.telegram_status == DeliveryStatus.failed or
            self.email_status == DeliveryStatus.failed
        )
