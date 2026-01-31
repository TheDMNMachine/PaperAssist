"""Subscribers for Device events.

SubscriberCommands run inside the existing @transactional — NEVER add @transactional here.
"""

import logging

from app.infrastructure.commands import SubscriberCommand
from app.infrastructure.events.subscriber import SyncSubscriber

logger = logging.getLogger(__name__)


class LogHeartbeatCommand(SubscriberCommand):
    device_id: str

    async def handle(self) -> None:
        logger.info("Heartbeat received from device: %s", self.device_id)


class LogHeartbeatSubscriber(SyncSubscriber):
    command = LogHeartbeatCommand
