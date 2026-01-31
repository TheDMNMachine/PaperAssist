"""Inbound adapter: FastAPI router for Screen endpoints.

Routers ONLY call CommandBus — never access repositories or domain services directly.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.adapters.inbound.api.dependencies import get_command_bus
from app.adapters.inbound.api.schemas.screen import ScreenCreate, ScreenResponse, ScreenUpdate
from app.application.commands.screen_commands import (
    CreateScreenCommand,
    DeleteScreenCommand,
    GetCurrentScreenCommand,
    GetScreenCommand,
    ListScreensCommand,
    UpdateScreenCommand,
)
from app.domain.models.screen import Screen

router = APIRouter(prefix="/screens", tags=["screens"])


def _to_response(screen: Screen) -> ScreenResponse:
    return ScreenResponse(
        id=screen.id,
        title=screen.title,
        content=screen.content,
        screen_type=screen.screen_type,
        is_active=screen.is_active,
        display_order=screen.display_order,
        created_at=screen.created_at,
        updated_at=screen.updated_at,
    )


@router.get("", response_model=list[ScreenResponse])
async def list_screens() -> list[ScreenResponse]:
    bus = get_command_bus()
    screens = await bus.execute(ListScreensCommand)
    return [_to_response(s) for s in screens]


@router.get("/current", response_model=ScreenResponse | None)
async def get_current_screen() -> ScreenResponse | None:
    bus = get_command_bus()
    screen = await bus.execute(GetCurrentScreenCommand)
    return _to_response(screen) if screen else None


@router.get("/{screen_id}", response_model=ScreenResponse)
async def get_screen(screen_id: UUID) -> ScreenResponse:
    bus = get_command_bus()
    screen = await bus.execute(GetScreenCommand, params={"screen_id": screen_id})
    if not screen:
        raise HTTPException(status_code=404, detail="Screen not found")
    return _to_response(screen)


@router.post("", response_model=ScreenResponse, status_code=201)
async def create_screen(body: ScreenCreate) -> ScreenResponse:
    bus = get_command_bus()
    screen = await bus.execute(CreateScreenCommand, params=body.model_dump())
    return _to_response(screen)


@router.put("/{screen_id}", response_model=ScreenResponse)
async def update_screen(screen_id: UUID, body: ScreenUpdate) -> ScreenResponse:
    bus = get_command_bus()
    params = {"screen_id": screen_id, **body.model_dump(exclude_unset=True)}
    screen = await bus.execute(UpdateScreenCommand, params=params)
    if not screen:
        raise HTTPException(status_code=404, detail="Screen not found")
    return _to_response(screen)


@router.delete("/{screen_id}", status_code=204)
async def delete_screen(screen_id: UUID) -> None:
    bus = get_command_bus()
    deleted = await bus.execute(DeleteScreenCommand, params={"screen_id": screen_id})
    if not deleted:
        raise HTTPException(status_code=404, detail="Screen not found")
