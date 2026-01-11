from pydantic import BaseModel

from src.application.messaging.registries import HandlersRegistry
from src.application.dtos.callback import CodeRunCallbackDTO

callback_registry = HandlersRegistry()


@callback_registry.register("register_attempt", CodeRunCallbackDTO)
async def register_attempt(dto: BaseModel, use_case):
    pass
