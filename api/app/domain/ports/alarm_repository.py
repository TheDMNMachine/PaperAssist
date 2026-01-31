"""Port: Alarm repository interface — domain defines the contract."""

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.alarm import Alarm


class AlarmRepository(ABC):
    @abstractmethod
    async def get_all(self) -> list[Alarm]:
        ...

    @abstractmethod
    async def get_by_id(self, alarm_id: UUID) -> Alarm | None:
        ...

    @abstractmethod
    async def get_active(self) -> list[Alarm]:
        ...

    @abstractmethod
    async def create(self, alarm: Alarm) -> Alarm:
        ...

    @abstractmethod
    async def update(self, alarm: Alarm) -> Alarm:
        ...

    @abstractmethod
    async def delete(self, alarm_id: UUID) -> bool:
        ...
