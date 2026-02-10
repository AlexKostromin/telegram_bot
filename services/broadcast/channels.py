from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class DeliveryResult:

    success: bool
    status: str
    message_id: Optional[str] = None
    error: Optional[str] = None
    sent_at: Optional[datetime] = None

class NotificationChannel(ABC):

    @abstractmethod
    async def send(
        self,
        recipient: Dict[str, Any],
        subject: str,
        body: str
    ) -> DeliveryResult:
        pass

    @abstractmethod
    async def validate_recipient(self, recipient: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def get_channel_name(self) -> str:
        pass

    @abstractmethod
    async def validate_configuration(self) -> bool:
        pass

    async def test_connection(self) -> bool:
        return True

    def __str__(self) -> str:
        return f"{self.get_channel_name()}Channel"

    def __repr__(self) -> str:
        return f"<{self.get_channel_name()}Channel>"
