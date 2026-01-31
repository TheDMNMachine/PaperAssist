"""Port: Device repository interface — domain defines the contract."""

from abc import ABC, abstractmethod

from app.domain.models.device import DeviceStatus


class DeviceRepository(ABC):
    @abstractmethod
    async def get_status(self, device_id: str) -> DeviceStatus | None:
        ...

    @abstractmethod
    async def upsert_heartbeat(self, status: DeviceStatus) -> DeviceStatus:
        ...
