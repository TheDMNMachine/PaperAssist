"""Port: Screen repository interface — domain defines the contract."""

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.screen import Screen


class ScreenRepository(ABC):
    @abstractmethod
    async def get_all(self) -> list[Screen]:
        ...

    @abstractmethod
    async def get_by_id(self, screen_id: UUID) -> Screen | None:
        ...

    @abstractmethod
    async def get_current(self) -> Screen | None:
        ...

    @abstractmethod
    async def create(self, screen: Screen) -> Screen:
        ...

    @abstractmethod
    async def update(self, screen: Screen) -> Screen:
        ...

    @abstractmethod
    async def delete(self, screen_id: UUID) -> bool:
        ...
