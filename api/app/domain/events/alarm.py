"""Domain events related to Alarm."""

from dataclasses import dataclass
from uuid import UUID

from app.domain.events.base import Event


@dataclass(frozen=True)
class AlarmCreatedEvent(Event):
    alarm_id: UUID = None  # type: ignore[assignment]


@dataclass(frozen=True)
class AlarmTriggeredEvent(Event):
    alarm_id: UUID = None  # type: ignore[assignment]
