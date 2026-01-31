"""Application commands for Alarm — invoked via CommandBus."""

from datetime import time as dt_time
from typing import Any
from uuid import UUID

from app.domain.events.alarm import AlarmCreatedEvent
from app.domain.models.alarm import Alarm, AlarmStatus
from app.domain.ports.alarm_repository import AlarmRepository
from app.infrastructure.commands import BaseCommand
from app.infrastructure.decorators import transactional
from app.infrastructure.events.event_bus import EventBus


class ListAlarmsCommand(BaseCommand):
    alarm_repository: AlarmRepository
    event_bus: EventBus

    @transactional
    async def handle(self) -> list[Alarm]:
        return await self.alarm_repository.get_all()


class GetActiveAlarmsCommand(BaseCommand):
    alarm_repository: AlarmRepository
    event_bus: EventBus

    @transactional
    async def handle(self) -> list[Alarm]:
        return await self.alarm_repository.get_active()


class CreateAlarmCommand(BaseCommand):
    alarm_repository: AlarmRepository
    event_bus: EventBus

    name: str
    trigger_time: dt_time
    message: str = ""
    repeat_days: list[int] | None = None

    @transactional
    async def handle(self) -> Alarm:
        alarm = Alarm(
            name=self.name,
            trigger_time=self.trigger_time,
            message=self.message,
            repeat_days=self.repeat_days or [],
        )
        created = await self.alarm_repository.create(alarm)
        self.event_bus.publish(AlarmCreatedEvent(alarm_id=created.id))
        return created


class UpdateAlarmCommand(BaseCommand):
    alarm_repository: AlarmRepository
    event_bus: EventBus

    alarm_id: UUID
    name: str | None = None
    trigger_time: dt_time | None = None
    message: str | None = None
    status: str | None = None
    repeat_days: list[int] | None = None

    @transactional
    async def handle(self) -> Alarm | None:
        alarm = await self.alarm_repository.get_by_id(self.alarm_id)
        if not alarm:
            return None

        if self.name is not None:
            alarm.name = self.name
        if self.trigger_time is not None:
            alarm.trigger_time = self.trigger_time
        if self.message is not None:
            alarm.message = self.message
        if self.status is not None:
            alarm.status = AlarmStatus(self.status)
        if self.repeat_days is not None:
            alarm.repeat_days = self.repeat_days

        return await self.alarm_repository.update(alarm)


class DeleteAlarmCommand(BaseCommand):
    alarm_repository: AlarmRepository
    event_bus: EventBus

    alarm_id: UUID

    @transactional
    async def handle(self) -> bool:
        return await self.alarm_repository.delete(self.alarm_id)
