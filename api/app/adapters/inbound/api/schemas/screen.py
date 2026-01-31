"""Pydantic schemas for Screen API — request/response DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.models.screen import ScreenType


class ScreenCreate(BaseModel):
    title: str
    content: str = ""
    screen_type: ScreenType = ScreenType.TEXT
    display_order: int = 0


class ScreenUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    screen_type: ScreenType | None = None
    is_active: bool | None = None
    display_order: int | None = None


class ScreenResponse(BaseModel):
    id: UUID
    title: str
    content: str
    screen_type: ScreenType
    is_active: bool
    display_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
