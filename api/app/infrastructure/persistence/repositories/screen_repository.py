"""Outbound adapter: SQLAlchemy implementation of ScreenRepository port."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.screen import Screen
from app.domain.ports.screen_repository import ScreenRepository
from app.infrastructure.persistence.models.screen import ScreenORM


class SqlScreenRepository(ScreenRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self) -> list[Screen]:
        result = await self._session.execute(
            select(ScreenORM).order_by(ScreenORM.display_order)
        )
        return [row.to_domain() for row in result.scalars().all()]

    async def get_by_id(self, screen_id: UUID) -> Screen | None:
        orm = await self._session.get(ScreenORM, screen_id)
        return orm.to_domain() if orm else None

    async def get_current(self) -> Screen | None:
        result = await self._session.execute(
            select(ScreenORM)
            .where(ScreenORM.is_active.is_(True))
            .order_by(ScreenORM.display_order)
            .limit(1)
        )
        orm = result.scalar_one_or_none()
        return orm.to_domain() if orm else None

    async def create(self, screen: Screen) -> Screen:
        orm = ScreenORM.from_domain(screen)
        self._session.add(orm)
        await self._session.flush()
        return orm.to_domain()

    async def update(self, screen: Screen) -> Screen:
        orm = await self._session.get(ScreenORM, screen.id)
        if not orm:
            raise ValueError(f"Screen {screen.id} not found")
        orm.title = screen.title
        orm.content = screen.content
        orm.screen_type = screen.screen_type.value
        orm.is_active = screen.is_active
        orm.display_order = screen.display_order
        await self._session.flush()
        return orm.to_domain()

    async def delete(self, screen_id: UUID) -> bool:
        orm = await self._session.get(ScreenORM, screen_id)
        if not orm:
            return False
        await self._session.delete(orm)
        await self._session.flush()
        return True
