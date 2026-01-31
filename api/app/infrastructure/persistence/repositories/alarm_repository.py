"""Outbound adapter: SQLAlchemy implementation of AlarmRepository port."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.alarm import Alarm, AlarmStatus
from app.domain.ports.alarm_repository import AlarmRepository
from app.infrastructure.persistence.models.alarm import AlarmORM


class SqlAlarmRepository(AlarmRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self) -> list[Alarm]:
        result = await self._session.execute(select(AlarmORM).order_by(AlarmORM.trigger_time))
        return [row.to_domain() for row in result.scalars().all()]

    async def get_by_id(self, alarm_id: UUID) -> Alarm | None:
        orm = await self._session.get(AlarmORM, alarm_id)
        return orm.to_domain() if orm else None

    async def get_active(self) -> list[Alarm]:
        result = await self._session.execute(
            select(AlarmORM)
            .where(AlarmORM.status == AlarmStatus.ACTIVE.value)
            .order_by(AlarmORM.trigger_time)
        )
        return [row.to_domain() for row in result.scalars().all()]

    async def create(self, alarm: Alarm) -> Alarm:
        orm = AlarmORM.from_domain(alarm)
        self._session.add(orm)
        await self._session.flush()
        return orm.to_domain()

    async def update(self, alarm: Alarm) -> Alarm:
        orm = await self._session.get(AlarmORM, alarm.id)
        if not orm:
            raise ValueError(f"Alarm {alarm.id} not found")
        orm.name = alarm.name
        orm.trigger_time = alarm.trigger_time
        orm.message = alarm.message
        orm.status = alarm.status.value
        orm.repeat_days = alarm.repeat_days
        await self._session.flush()
        return orm.to_domain()

    async def delete(self, alarm_id: UUID) -> bool:
        orm = await self._session.get(AlarmORM, alarm_id)
        if not orm:
            return False
        await self._session.delete(orm)
        await self._session.flush()
        return True
