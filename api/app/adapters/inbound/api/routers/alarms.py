"""Inbound adapter: FastAPI router for Alarm endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.adapters.inbound.api.dependencies import get_command_bus
from app.adapters.inbound.api.schemas.alarm import AlarmCreate, AlarmResponse, AlarmUpdate
from app.application.commands.alarm_commands import (
    CreateAlarmCommand,
    DeleteAlarmCommand,
    GetActiveAlarmsCommand,
    ListAlarmsCommand,
    UpdateAlarmCommand,
)
from app.domain.models.alarm import Alarm

router = APIRouter(prefix="/alarms", tags=["alarms"])


def _to_response(alarm: Alarm) -> AlarmResponse:
    return AlarmResponse(
        id=alarm.id,
        name=alarm.name,
        trigger_time=alarm.trigger_time,
        message=alarm.message,
        status=alarm.status,
        repeat_days=alarm.repeat_days,
        created_at=alarm.created_at,
        updated_at=alarm.updated_at,
    )


@router.get("", response_model=list[AlarmResponse])
async def list_alarms() -> list[AlarmResponse]:
    bus = get_command_bus()
    alarms = await bus.execute(ListAlarmsCommand)
    return [_to_response(a) for a in alarms]


@router.get("/active", response_model=list[AlarmResponse])
async def get_active_alarms() -> list[AlarmResponse]:
    bus = get_command_bus()
    alarms = await bus.execute(GetActiveAlarmsCommand)
    return [_to_response(a) for a in alarms]


@router.post("", response_model=AlarmResponse, status_code=201)
async def create_alarm(body: AlarmCreate) -> AlarmResponse:
    bus = get_command_bus()
    alarm = await bus.execute(CreateAlarmCommand, params=body.model_dump())
    return _to_response(alarm)


@router.put("/{alarm_id}", response_model=AlarmResponse)
async def update_alarm(alarm_id: UUID, body: AlarmUpdate) -> AlarmResponse:
    bus = get_command_bus()
    params = {"alarm_id": alarm_id, **body.model_dump(exclude_unset=True)}
    alarm = await bus.execute(UpdateAlarmCommand, params=params)
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    return _to_response(alarm)


@router.delete("/{alarm_id}", status_code=204)
async def delete_alarm(alarm_id: UUID) -> None:
    bus = get_command_bus()
    deleted = await bus.execute(DeleteAlarmCommand, params={"alarm_id": alarm_id})
    if not deleted:
        raise HTTPException(status_code=404, detail="Alarm not found")
