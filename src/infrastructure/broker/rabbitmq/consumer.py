from typing import Optional, Callable, Awaitable

from pydantic import BaseModel

from aio_pika import Message
from aio_pika.abc import AbstractRobustChannel, AbstractIncomingMessage, AbstractRobustQueue

from application.interfaces import QueueHandlersRegistryInterface
from .client import RabbitMQClient
from .exceptions import NoConnectionError, NoChannelError, NoTaskNameError


class RabbitConsumer(RabbitMQClient):
    def __init__(self, registry: QueueHandlersRegistryInterface, prefetch_count: int = 0):
        super().__init__()
        self._tags: dict[str, str] = {}
        self._channel: Optional[AbstractRobustChannel] = None
        self._prefetch_count: int = prefetch_count
        self._handlers_registry = registry

    async def init_channel(self) -> None:
        if not self._connection:
            raise NoConnectionError("Unable to initialize consumer: connection was not establish")
        if not self._channel:
            self._channel = await self._connection.channel()
            await self._channel.set_qos(prefetch_count=self.prefetch_count)

    async def stop_consuming(self) -> None:
        if self._channel:
            await self._channel.close()
            self._channel = None
        await self.disconnect()

    async def get_channel(self) -> AbstractRobustChannel:
        if not (self._channel and self._channel.is_initialized):
            raise NoChannelError("Channel was not setup")
        return self._channel

    async def process_message(self, message: AbstractIncomingMessage):
        data = message.body.decode()
        task_name = message.headers.get("task_name")
        if not task_name:
            raise NoTaskNameError(f"Task name was not set in message headers")
        handler_coro = self._handlers_registry.get_handler_coro(task_name, data)
        return await handler_coro

    def on_message(self, queue_name: str) -> Callable[[AbstractIncomingMessage], Awaitable[None]]:
        async def handle_message(message: AbstractIncomingMessage) -> None:
            publisher_answer = b"ACK"
            try:
                await self.process_message(message)
            except Exception as e:
                # todo: logging required
                publisher_answer = b"NACK"
            await message.ack()
            if message.reply_to:
                channel = await self.get_channel()
                await channel.default_exchange.publish(
                    Message(body=publisher_answer), routing_key=message.reply_to
                )
        return handle_message

    async def declare_queue(self, queue_name: str) -> Optional[AbstractRobustQueue]:
        channel = await self.get_channel()
        queue = await channel.declare_queue(
            queue_name,
            durable=True,
            arguments={
                "x-max-priority": 10,
            },
        )
        return queue

    async def add_to_consume(self, queue_name: str) -> None:
        queue = await self.declare_queue(queue_name)
        tag = await queue.consume(self.on_message(queue_name))
        self.tags[queue_name] = tag

    async def remove_from_consuming(self, queue_name: str) -> None:
        channel = await self.get_channel()
        queue = await channel.get_queue(queue_name)
        tag = self.tags.pop(queue_name, None)
        if not tag:
            return None
        await queue.cancel(tag)

    async def remove_queue(self, queue_name: str) -> None:
        channel = await self.get_channel()
        await channel.queue_delete(queue_name)
        await channel.exchange_delete(f"{queue_name}_dlx")
        await channel.queue_delete(f"{queue_name}_dlq")
