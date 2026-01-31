"""FastAPI application entry point.

prepare() — initializes IoC container and registers event subscribers.
create_app() — builds and returns the FastAPI application.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.adapters.inbound.api.routers import alarms, device, screens
from app.application.subscribers.device_subscribers import LogHeartbeatSubscriber
from app.application.subscribers.screen_subscribers import LogScreenCreatedSubscriber
from app.domain.events.device import DeviceHeartbeatReceivedEvent
from app.domain.events.screen import ScreenCreatedEvent
from app.infrastructure.container import init_container
from app.infrastructure.persistence.database import Base, async_session_factory, engine
from app.infrastructure.persistence.repositories import (
    SqlAlarmRepository,
    SqlDeviceRepository,
    SqlScreenRepository,
)


def prepare() -> None:
    """Initialize IoC container and register event subscribers."""
    container = init_container(
        session_factory=async_session_factory,
        screen_repo_cls=SqlScreenRepository,
        alarm_repo_cls=SqlAlarmRepository,
        device_repo_cls=SqlDeviceRepository,
    )

    event_bus = container.event_bus

    event_bus.subscribe(
        event=ScreenCreatedEvent,
        subscribers=[LogScreenCreatedSubscriber],
    )

    event_bus.subscribe(
        event=DeviceHeartbeatReceivedEvent,
        subscribers=[LogHeartbeatSubscriber],
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    prepare()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="PaperAssist API",
        version="0.1.0",
        lifespan=lifespan,
        root_path="/api",
    )

    app.include_router(screens.router, prefix="/v1")
    app.include_router(alarms.router, prefix="/v1")
    app.include_router(device.router, prefix="/v1")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
