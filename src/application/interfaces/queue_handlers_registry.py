from typing import Callable, Awaitable, Any, Type, Protocol

from pydantic import BaseModel


class QueueHandlersRegistryInterface(Protocol):
    def get_handler_coro(self, key: str, data: str | bytes) -> Awaitable[None]: ...
