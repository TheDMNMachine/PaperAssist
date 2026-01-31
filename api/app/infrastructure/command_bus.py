"""Command Bus — decouples command invocation from implementation.

Usage in routers:
    result = await command_bus.execute(CreateScreenCommand, params={...})
"""

from abc import ABC, abstractmethod
from typing import Any

from app.infrastructure.commands import BaseCommand


class CommandBus(ABC):
    @abstractmethod
    async def execute(
        self, command: type[BaseCommand], params: dict[str, Any] | None = None
    ) -> Any:
        ...


class SimpleCommandBus(CommandBus):
    """Creates command instance with params and calls handle()."""

    def __init__(self, container: "Container") -> None:  # noqa: F821
        self._container = container

    async def execute(
        self, command: type[BaseCommand], params: dict[str, Any] | None = None
    ) -> Any:
        instance = command(**(params or {}))
        self._container.inject(instance)
        return await instance.handle()
