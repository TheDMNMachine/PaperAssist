"""Domain events related to Screen."""

from dataclasses import dataclass
from uuid import UUID

from app.domain.events.base import Event


@dataclass(frozen=True)
class ScreenCreatedEvent(Event):
    screen_id: UUID = None  # type: ignore[assignment]


@dataclass(frozen=True)
class ScreenUpdatedEvent(Event):
    screen_id: UUID = None  # type: ignore[assignment]


@dataclass(frozen=True)
class ScreenDeletedEvent(Event):
    screen_id: UUID = None  # type: ignore[assignment]
