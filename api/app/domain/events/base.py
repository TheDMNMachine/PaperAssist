"""Base Event class — immutable domain events."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Event:
    occurred_on: datetime = field(default_factory=datetime.utcnow)
