from typing import Callable, Awaitable, Any, Type
from functools import wraps

from pydantic import BaseModel

from ..exceptions.messaging import NoHandlerRegisteredError, NoDTOModelRegisteredError


class QueueHandlersRegistry:
    def __init__(self, queue_name: str):
        self._queue_name = queue_name
        self._handlers: dict[str, Callable[[BaseModel, Any], Awaitable[None]]] = {}
        self._models: dict[str, Type[BaseModel]] = {}

    def register(self, key: str, model: type[BaseModel]):
        def wrap(handler_func: Callable[[BaseModel, Any], Awaitable[None]]):
            self._handlers[key] = handler_func
            self._models[key] = model

            @wraps(handler_func)
            async def wrapper(dto: BaseModel, *args, **kwargs):
                return await handler_func(dto, *args, **kwargs)
            return wrapper
        return wrap

    def get_handler_coro(self, key: str, data: str | bytes) -> Awaitable[None]:
        handler = self._handlers.get(key)
        if not handler:
            raise NoHandlerRegisteredError(f"Handler for key ({key}) was not registered")
        model = self._models.get(key)
        if not model:
            raise NoDTOModelRegisteredError(f"DTO model for key ({key}) was not registered")
        return handler(model.model_validate_json(data))
