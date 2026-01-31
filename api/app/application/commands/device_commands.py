"""Application commands for Device — invoked via CommandBus."""

from app.domain.events.device import DeviceHeartbeatReceivedEvent
from app.domain.models.device import DeviceStatus
from app.domain.ports.device_repository import DeviceRepository
from app.infrastructure.commands import BaseCommand
from app.infrastructure.decorators import transactional
from app.infrastructure.events.event_bus import EventBus


class GetDeviceStatusCommand(BaseCommand):
    device_repository: DeviceRepository
    event_bus: EventBus

    device_id: str

    @transactional
    async def handle(self) -> DeviceStatus | None:
        return await self.device_repository.get_status(self.device_id)


class RecordHeartbeatCommand(BaseCommand):
    device_repository: DeviceRepository
    event_bus: EventBus

    device_id: str
    ip_address: str = ""
    firmware_version: str = ""
    battery_level: int | None = None

    @transactional
    async def handle(self) -> DeviceStatus:
        status = DeviceStatus(
            device_id=self.device_id,
            ip_address=self.ip_address,
            firmware_version=self.firmware_version,
            battery_level=self.battery_level,
        )
        result = await self.device_repository.upsert_heartbeat(status)
        self.event_bus.publish(DeviceHeartbeatReceivedEvent(device_id=self.device_id))
        return result
