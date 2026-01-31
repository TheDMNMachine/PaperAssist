"""Pydantic schemas for Device API — request/response DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class HeartbeatRequest(BaseModel):
    device_id: str
    ip_address: str = ""
    firmware_version: str = ""
    battery_level: int | None = None


class DeviceStatusResponse(BaseModel):
    id: UUID
    device_id: str
    ip_address: str
    firmware_version: str
    battery_level: int | None
    last_seen: datetime

    model_config = {"from_attributes": True}
