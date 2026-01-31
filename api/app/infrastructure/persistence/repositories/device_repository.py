"""Outbound adapter: SQLAlchemy implementation of DeviceRepository port."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.device import DeviceStatus
from app.domain.ports.device_repository import DeviceRepository
from app.infrastructure.persistence.models.device import DeviceStatusORM


class SqlDeviceRepository(DeviceRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_status(self, device_id: str) -> DeviceStatus | None:
        result = await self._session.execute(
            select(DeviceStatusORM).where(DeviceStatusORM.device_id == device_id)
        )
        orm = result.scalar_one_or_none()
        return orm.to_domain() if orm else None

    async def upsert_heartbeat(self, status: DeviceStatus) -> DeviceStatus:
        result = await self._session.execute(
            select(DeviceStatusORM).where(DeviceStatusORM.device_id == status.device_id)
        )
        orm = result.scalar_one_or_none()

        if orm:
            orm.ip_address = status.ip_address
            orm.firmware_version = status.firmware_version
            orm.battery_level = status.battery_level
            orm.last_seen = status.last_seen
        else:
            orm = DeviceStatusORM.from_domain(status)
            self._session.add(orm)

        await self._session.flush()
        return orm.to_domain()
