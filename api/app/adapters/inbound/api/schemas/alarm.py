"""Pydantic schemas for Alarm API — request/response DTOs."""

from datetime import datetime, time
from uuid import UUID

from pydantic import BaseModel

from app.domain.models.alarm import AlarmStatus


class AlarmCreate(BaseModel):
    name: str
    trigger_time: time
    message: str = ""
    repeat_days: list[int] = []


class AlarmUpdate(BaseModel):
    name: str | None = None
    trigger_time: time | None = None
    message: str | None = None
    status: AlarmStatus | None = None
    repeat_days: list[int] | None = None


class AlarmResponse(BaseModel):
    id: UUID
    name: str
    trigger_time: time
    message: str
    status: AlarmStatus
    repeat_days: list[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
