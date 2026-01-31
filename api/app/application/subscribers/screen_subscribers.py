"""Subscribers for Screen events.

SubscriberCommands run inside the existing @transactional — NEVER add @transactional here.
Subscribers link events to commands. Registered in app.main.prepare().
"""

import logging
from uuid import UUID

from app.infrastructure.commands import SubscriberCommand
from app.infrastructure.events.subscriber import SyncSubscriber

logger = logging.getLogger(__name__)


# --- SubscriberCommand: runs inside existing transaction ---


class LogScreenCreatedCommand(SubscriberCommand):
    screen_id: UUID

    async def handle(self) -> None:
        logger.info("Screen created: %s", self.screen_id)


# --- Subscriber: links event → command ---


class LogScreenCreatedSubscriber(SyncSubscriber):
    command = LogScreenCreatedCommand
