"""Subscriber — links a domain Event to a SubscriberCommand."""

from app.infrastructure.commands import SubscriberCommand


class SyncSubscriber:
    """Base subscriber. Set `command` to a SubscriberCommand class."""

    command: type[SubscriberCommand]
