"""SQLAlchemy ORM model for Alarm."""

import uuid
from datetime import datetime, time

from sqlalchemy import DateTime, String, Text, Time, func
from sqlalchemy.dialects.postgresql import ARRAY, INTEGER, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.alarm import Alarm, AlarmStatus
from app.infrastructure.persistence.database import Base


class AlarmORM(Base):
    __tablename__ = "alarms"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    trigger_time: Mapped[time] = mapped_column(Time, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=AlarmStatus.ACTIVE)
    repeat_days: Mapped[list[int]] = mapped_column(ARRAY(INTEGER), nullable=False, default=[])
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def to_domain(self) -> Alarm:
        return Alarm(
            id=self.id,
            name=self.name,
            trigger_time=self.trigger_time,
            message=self.message,
            status=AlarmStatus(self.status),
            repeat_days=self.repeat_days or [],
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @staticmethod
    def from_domain(alarm: Alarm) -> "AlarmORM":
        return AlarmORM(
            id=alarm.id,
            name=alarm.name,
            trigger_time=alarm.trigger_time,
            message=alarm.message,
            status=alarm.status.value,
            repeat_days=alarm.repeat_days,
        )
