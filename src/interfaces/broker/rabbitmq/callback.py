from pydantic import BaseModel

from application.messaging.registries import HandlersRegistry

callback_registry = HandlersRegistry()


@callback_registry.register("register_attempt")
async def register_attempt(dto: BaseModel, use_case):
    pass
