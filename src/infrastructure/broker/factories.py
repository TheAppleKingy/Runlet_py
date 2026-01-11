from src.application.interfaces.broker import MessageConsumerInterface
from .rabbitmq.consumer import RabbitConsumer


class RabbitMQConsumerFactory:
    async def create(self) -> MessageConsumerInterface:
        consumer = RabbitConsumer(prefetch_count=1)
        await consumer.connect()
        await consumer.init_channel()
        return consumer
