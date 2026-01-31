"""Domain entity: Alarm — pure Python, no framework dependencies."""

from dataclasses import dataclass, field
from datetime import datetime, time
from enum import StrEnum
from uuid import UUID, uuid4


class AlarmStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    TRIGGERED = "triggered"


@dataclass
class Alarm:
    name: str
    trigger_time: time
    message: str = ""
    status: AlarmStatus = AlarmStatus.ACTIVE
    repeat_days: list[int] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
