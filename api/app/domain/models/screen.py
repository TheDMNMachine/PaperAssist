"""Domain entity: Screen — pure Python, no framework dependencies."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4


class ScreenType(StrEnum):
    TEXT = "text"
    WEATHER = "weather"
    CALENDAR = "calendar"
    CUSTOM = "custom"


@dataclass
class Screen:
    title: str
    content: str
    screen_type: ScreenType = ScreenType.TEXT
    is_active: bool = True
    display_order: int = 0
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
