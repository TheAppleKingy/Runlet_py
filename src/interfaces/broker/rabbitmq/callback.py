from pydantic import BaseModel

from application.messaging.registy import QueueHandlersRegistry

callback_registry = QueueHandlersRegistry("callback")


@callback_registry.register("register_attempt")
async def register_attempt(dto: BaseModel, use_case):
    pass
