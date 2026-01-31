"""EventBus — queues domain events and dispatches them inside @transactional.

Events are published with publish() and dispatched with dispatch().
dispatch() is called automatically by @transactional after session.flush().
"""

from typing import Any

from app.domain.events.base import Event
from app.infrastructure.events.subscriber import SyncSubscriber


class EventBus:
    def __init__(self) -> None:
        self._queue: list[Event] = []
        self._subscriptions: dict[type[Event], list[type[SyncSubscriber]]] = {}

    def subscribe(
        self,
        event: type[Event],
        subscribers: list[type[SyncSubscriber]],
    ) -> None:
        existing = self._subscriptions.get(event, [])
        existing.extend(subscribers)
        self._subscriptions[event] = existing

    def publish(self, event: Event) -> None:
        """Add event to queue. Dispatched later by @transactional."""
        self._queue.append(event)

    async def dispatch(self, container: Any = None) -> None:
        """Execute all queued events' subscribers. Called by @transactional."""
        while self._queue:
            event = self._queue.pop(0)
            subscriber_classes = self._subscriptions.get(type(event), [])
            for subscriber_cls in subscriber_classes:
                params = self._collect_params(event, subscriber_cls)
                command_instance = subscriber_cls.command(**params)
                if container:
                    container.inject(command_instance)
                await command_instance.handle()

    def clear(self) -> None:
        """Clear event queue. Called by @transactional on exception."""
        self._queue.clear()

    @staticmethod
    def _collect_params(event: Event, subscriber: type[SyncSubscriber]) -> dict[str, Any]:
        """Map event fields to subscriber command params by name."""
        import dataclasses

        event_fields = {f.name: getattr(event, f.name) for f in dataclasses.fields(event)}
        command_cls = subscriber.command
        command_init_fields = set()
        for cls in command_cls.__mro__:
            command_init_fields.update(getattr(cls, "__annotations__", {}).keys())
        return {k: v for k, v in event_fields.items() if k in command_init_fields}
