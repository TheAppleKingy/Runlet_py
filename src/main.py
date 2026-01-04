from contextlib import asynccontextmanager

from fastapi import FastAPI

from infrastructure.broker.factories import RabbitMQConsumerFactory
from application.messaging.registries import MessageConsumerRegistry
from interfaces.broker.rabbitmq.callback import callback_registry


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    _consumer_registry = MessageConsumerRegistry(RabbitMQConsumerFactory())
    _consumer_registry.register("callback", callback_registry)

app = FastAPI(lifespan=lifespan_handler)
