from typing import Callable, Awaitable, Any, Type

from pydantic import BaseModel


class HandlersRegistry:
    def __init__(self):
        self._handlers: dict[str, Callable[[BaseModel, Any], Awaitable[None]]] = {}
        self._models: dict[str, Type[BaseModel]] = {}

    def register(self, key: str, model: type[BaseModel]):
        def wrap(handler_func: Callable[[BaseModel, Any], Awaitable[None]]):
            self._handlers[key] = handler_func
            self._models[key] = model
            return handler_func
        return wrap

    def _generate_validation_func(self, key: str):
        def validate_data(data: str | bytes):
            dto = self._models[key].model_validate_json(data)
            return self._handlers[key](dto)

        return validate_data

    def as_dict(self) -> dict[str, Callable[[str | bytes], Awaitable[None]]]:
        return {k: self._generate_validation_func(k) for k in self._handlers}
