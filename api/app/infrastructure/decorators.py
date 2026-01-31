"""Decorators: @transactional — manages DB session + event dispatch.

Use ONLY on BaseCommand.handle(). NEVER on SubscriberCommand.handle().
"""

import functools
import logging
from typing import Any

from app.infrastructure.container import get_container

logger = logging.getLogger(__name__)


def transactional(func: Any) -> Any:
    """Wraps async handle() with session management and event dispatch.

    Flow:
        1. Execute function
        2. session.flush()       — check DB constraints
        3. event_bus.dispatch()  — run subscriber commands
        4. session.commit()      — persist everything

    On exception:
        1. event_bus.clear()
        2. session.rollback()
    Always:
        1. session.close()
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        container = get_container()
        session = container.session()
        event_bus = container.event_bus

        try:
            result = await func(*args, **kwargs)
            await session.flush()
            await event_bus.dispatch(container=container)
            await session.commit()
            return result
        except Exception:
            event_bus.clear()
            await session.rollback()
            raise
        finally:
            await session.close()

    return wrapper
