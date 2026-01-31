"""IoC Container — dependency injection for commands and subscribers.

Replaces haps Container() from ARCHITECTURE_PLAN. Provides:
- Repository instances (bound to current session)
- EventBus singleton
- inject() method to populate command attributes
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.ports.alarm_repository import AlarmRepository
from app.domain.ports.device_repository import DeviceRepository
from app.domain.ports.screen_repository import ScreenRepository
from app.infrastructure.events.event_bus import EventBus

_container_instance: "Container | None" = None


class Container:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        event_bus: EventBus,
        screen_repo_cls: type[ScreenRepository],
        alarm_repo_cls: type[AlarmRepository],
        device_repo_cls: type[DeviceRepository],
    ) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self.event_bus = event_bus
        self._screen_repo_cls = screen_repo_cls
        self._alarm_repo_cls = alarm_repo_cls
        self._device_repo_cls = device_repo_cls

    def session(self) -> AsyncSession:
        if self._session is None or not self._session.is_active:
            self._session = self._session_factory()
        return self._session

    @property
    def screen_repository(self) -> ScreenRepository:
        return self._screen_repo_cls(self.session())  # type: ignore[call-arg]

    @property
    def alarm_repository(self) -> AlarmRepository:
        return self._alarm_repo_cls(self.session())  # type: ignore[call-arg]

    @property
    def device_repository(self) -> DeviceRepository:
        return self._device_repo_cls(self.session())  # type: ignore[call-arg]

    def inject(self, instance: Any) -> None:
        """Inject dependencies into command instance based on type annotations."""
        annotations = {}
        for cls in type(instance).__mro__:
            annotations.update(getattr(cls, "__annotations__", {}))

        for attr_name, attr_type in annotations.items():
            if attr_type is ScreenRepository or (
                isinstance(attr_type, type) and issubclass(attr_type, ScreenRepository)
            ):
                setattr(instance, attr_name, self.screen_repository)
            elif attr_type is AlarmRepository or (
                isinstance(attr_type, type) and issubclass(attr_type, AlarmRepository)
            ):
                setattr(instance, attr_name, self.alarm_repository)
            elif attr_type is DeviceRepository or (
                isinstance(attr_type, type) and issubclass(attr_type, DeviceRepository)
            ):
                setattr(instance, attr_name, self.device_repository)
            elif attr_type is EventBus:
                setattr(instance, attr_name, self.event_bus)


def init_container(
    session_factory: async_sessionmaker[AsyncSession],
    screen_repo_cls: type[ScreenRepository],
    alarm_repo_cls: type[AlarmRepository],
    device_repo_cls: type[DeviceRepository],
) -> Container:
    global _container_instance
    event_bus = EventBus()
    _container_instance = Container(
        session_factory=session_factory,
        event_bus=event_bus,
        screen_repo_cls=screen_repo_cls,
        alarm_repo_cls=alarm_repo_cls,
        device_repo_cls=device_repo_cls,
    )
    return _container_instance


def get_container() -> Container:
    if _container_instance is None:
        raise RuntimeError("Container not initialized. Call init_container() first.")
    return _container_instance
