from typing import Callable, Awaitable

from aio_pika import Message
from aio_pika.abc import AbstractRobustChannel, AbstractIncomingMessage, AbstractRobustQueue, ConsumerTag

from .client import RabbitMQClient
from .exceptions import NoConnectionError, NoChannelError, NoTaskNameError


class RabbitConsumer(RabbitMQClient):
    def __init__(self, prefetch_count: int = 0):
        super().__init__()
        self._tag: ConsumerTag = None
        self._channel: AbstractRobustChannel = None
        self._handlers_map: dict[str, Callable[[str | bytes], Awaitable[None]]] = {}
        self._queue_name: str = None
        self._prefetch_count: int = prefetch_count

    async def _get_channel(self) -> AbstractRobustChannel:
        if not (self._channel and self._channel.is_initialized):
            raise NoChannelError("Channel was not setup")
        return self._channel

    async def _process_message(self, message: AbstractIncomingMessage):
        data = message.body.decode()
        task_name = message.headers.get("task_name")
        if not task_name:
            raise NoTaskNameError(f"Task name was not set in message headers")
        if not task_name in self._handlers_map:
            raise
        handler_coro = self._handlers_map[task_name](data)
        return await handler_coro

    def _on_message(self) -> Callable[[AbstractIncomingMessage], Awaitable[None]]:
        async def handle_message(message: AbstractIncomingMessage) -> None:
            publisher_answer = b"ACK"
            try:
                await self._process_message(message)
            except Exception as e:
                # todo: logging required
                publisher_answer = b"NACK"
            await message.ack()
            if message.reply_to:
                channel = await self._get_channel()
                await channel.default_exchange.publish(
                    Message(body=publisher_answer), routing_key=message.reply_to
                )
        return handle_message

    async def _declare_queue(self, queue_name: str) -> AbstractRobustQueue:
        channel = await self._get_channel()
        queue = await channel.declare_queue(
            queue_name,
            durable=True,
            arguments={
                "x-max-priority": 10,
            },
        )
        self._queue_name = queue.name
        return queue

    async def init_channel(self) -> None:
        if not self._connection:
            raise NoConnectionError("Unable to initialize consumer: connection was not establish")
        if not self._channel:
            self._channel = await self._connection.channel()
            await self._channel.set_qos(prefetch_count=self._prefetch_count)

    async def start_consuming(self, queue_name: str) -> None:
        if self._queue_name:
            raise
        if not self._handlers_map:
            raise
        queue = await self._declare_queue(queue_name)
        self._tag = await queue.consume(self._on_message())
        # todo: logging

    async def stop_consuming(self) -> None:
        if self._channel:
            await self._channel.close()
            self._channel = None
        await self.disconnect()

    def set_handlers_map(self, handlers_map: dict[str, Callable[[str | bytes], Awaitable[None]]]) -> None:
        self._handlers_map = handlers_map
