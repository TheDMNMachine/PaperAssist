"""SQLAlchemy ORM model for Screen."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.screen import Screen, ScreenType
from app.infrastructure.persistence.database import Base


class ScreenORM(Base):
    __tablename__ = "screens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    screen_type: Mapped[str] = mapped_column(String(50), nullable=False, default=ScreenType.TEXT)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def to_domain(self) -> Screen:
        return Screen(
            id=self.id,
            title=self.title,
            content=self.content,
            screen_type=ScreenType(self.screen_type),
            is_active=self.is_active,
            display_order=self.display_order,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @staticmethod
    def from_domain(screen: Screen) -> "ScreenORM":
        return ScreenORM(
            id=screen.id,
            title=screen.title,
            content=screen.content,
            screen_type=screen.screen_type.value,
            is_active=screen.is_active,
            display_order=screen.display_order,
        )
