"""Application commands for Screen — invoked via CommandBus.

Each command's handle() is decorated with @transactional:
  1. Executes business logic
  2. Publishes domain events
  3. @transactional flushes, dispatches events, commits
"""

from datetime import time as dt_time
from typing import Any
from uuid import UUID

from app.domain.events.screen import ScreenCreatedEvent, ScreenDeletedEvent, ScreenUpdatedEvent
from app.domain.models.screen import Screen, ScreenType
from app.domain.ports.screen_repository import ScreenRepository
from app.infrastructure.commands import BaseCommand
from app.infrastructure.decorators import transactional
from app.infrastructure.events.event_bus import EventBus


class ListScreensCommand(BaseCommand):
    screen_repository: ScreenRepository
    event_bus: EventBus

    @transactional
    async def handle(self) -> list[Screen]:
        return await self.screen_repository.get_all()


class GetCurrentScreenCommand(BaseCommand):
    screen_repository: ScreenRepository
    event_bus: EventBus

    @transactional
    async def handle(self) -> Screen | None:
        return await self.screen_repository.get_current()


class GetScreenCommand(BaseCommand):
    screen_repository: ScreenRepository
    event_bus: EventBus

    screen_id: UUID

    @transactional
    async def handle(self) -> Screen | None:
        return await self.screen_repository.get_by_id(self.screen_id)


class CreateScreenCommand(BaseCommand):
    screen_repository: ScreenRepository
    event_bus: EventBus

    title: str
    content: str
    screen_type: str = ScreenType.TEXT
    display_order: int = 0

    @transactional
    async def handle(self) -> Screen:
        screen = Screen(
            title=self.title,
            content=self.content,
            screen_type=ScreenType(self.screen_type),
            display_order=self.display_order,
        )
        created = await self.screen_repository.create(screen)
        self.event_bus.publish(ScreenCreatedEvent(screen_id=created.id))
        return created


class UpdateScreenCommand(BaseCommand):
    screen_repository: ScreenRepository
    event_bus: EventBus

    screen_id: UUID
    title: str | None = None
    content: str | None = None
    screen_type: str | None = None
    is_active: bool | None = None
    display_order: int | None = None

    @transactional
    async def handle(self) -> Screen | None:
        screen = await self.screen_repository.get_by_id(self.screen_id)
        if not screen:
            return None

        if self.title is not None:
            screen.title = self.title
        if self.content is not None:
            screen.content = self.content
        if self.screen_type is not None:
            screen.screen_type = ScreenType(self.screen_type)
        if self.is_active is not None:
            screen.is_active = self.is_active
        if self.display_order is not None:
            screen.display_order = self.display_order

        updated = await self.screen_repository.update(screen)
        self.event_bus.publish(ScreenUpdatedEvent(screen_id=updated.id))
        return updated


class DeleteScreenCommand(BaseCommand):
    screen_repository: ScreenRepository
    event_bus: EventBus

    screen_id: UUID

    @transactional
    async def handle(self) -> bool:
        deleted = await self.screen_repository.delete(self.screen_id)
        if deleted:
            self.event_bus.publish(ScreenDeletedEvent(screen_id=self.screen_id))
        return deleted
