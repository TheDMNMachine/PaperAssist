"""Base command classes following the Command Bus pattern.

BaseCommand — for commands invoked via CommandBus. Decorate handle() with @transactional.
SubscriberCommand — for commands invoked by event subscribers. NEVER use @transactional.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseCommand(ABC):
    """Command invoked through CommandBus. Use @transactional on handle()."""

    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    async def handle(self) -> Any:
        ...


class SubscriberCommand(ABC):
    """Command invoked by event subscribers — runs inside existing transaction.

    NEVER decorate handle() with @transactional.
    """

    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    async def handle(self) -> Any:
        ...
