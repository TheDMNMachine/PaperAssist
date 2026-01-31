"""Inbound adapter: FastAPI router for Device endpoints."""

from fastapi import APIRouter, HTTPException

from app.adapters.inbound.api.dependencies import get_command_bus
from app.adapters.inbound.api.schemas.device import DeviceStatusResponse, HeartbeatRequest
from app.application.commands.device_commands import GetDeviceStatusCommand, RecordHeartbeatCommand
from app.domain.models.device import DeviceStatus

router = APIRouter(prefix="/device", tags=["device"])


def _to_response(status: DeviceStatus) -> DeviceStatusResponse:
    return DeviceStatusResponse(
        id=status.id,
        device_id=status.device_id,
        ip_address=status.ip_address,
        firmware_version=status.firmware_version,
        battery_level=status.battery_level,
        last_seen=status.last_seen,
    )


@router.get("/status/{device_id}", response_model=DeviceStatusResponse)
async def get_device_status(device_id: str) -> DeviceStatusResponse:
    bus = get_command_bus()
    status = await bus.execute(GetDeviceStatusCommand, params={"device_id": device_id})
    if not status:
        raise HTTPException(status_code=404, detail="Device not found")
    return _to_response(status)


@router.post("/heartbeat", response_model=DeviceStatusResponse)
async def record_heartbeat(body: HeartbeatRequest) -> DeviceStatusResponse:
    bus = get_command_bus()
    status = await bus.execute(RecordHeartbeatCommand, params=body.model_dump())
    return _to_response(status)
