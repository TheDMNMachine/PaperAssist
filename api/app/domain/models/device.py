"""Domain entity: DeviceStatus — pure Python, no framework dependencies."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class DeviceStatus:
    device_id: str
    ip_address: str = ""
    firmware_version: str = ""
    battery_level: int | None = None
    last_seen: datetime = field(default_factory=datetime.utcnow)
    id: UUID = field(default_factory=uuid4)
