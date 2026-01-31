"""FastAPI dependencies — provides CommandBus to routers."""

from app.infrastructure.command_bus import CommandBus, SimpleCommandBus
from app.infrastructure.container import get_container


def get_command_bus() -> CommandBus:
    return SimpleCommandBus(get_container())
