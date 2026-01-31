"""SQLAlchemy ORM model for DeviceStatus."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.device import DeviceStatus
from app.infrastructure.persistence.database import Base


class DeviceStatusORM(Base):
    __tablename__ = "device_status"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False, default="")
    firmware_version: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    battery_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_seen: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def to_domain(self) -> DeviceStatus:
        return DeviceStatus(
            id=self.id,
            device_id=self.device_id,
            ip_address=self.ip_address,
            firmware_version=self.firmware_version,
            battery_level=self.battery_level,
            last_seen=self.last_seen,
        )

    @staticmethod
    def from_domain(status: DeviceStatus) -> "DeviceStatusORM":
        return DeviceStatusORM(
            id=status.id,
            device_id=status.device_id,
            ip_address=status.ip_address,
            firmware_version=status.firmware_version,
            battery_level=status.battery_level,
            last_seen=status.last_seen,
        )
