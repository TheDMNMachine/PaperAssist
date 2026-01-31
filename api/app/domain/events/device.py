"""Domain events related to Device."""

from dataclasses import dataclass

from app.domain.events.base import Event


@dataclass(frozen=True)
class DeviceHeartbeatReceivedEvent(Event):
    device_id: str = ""
