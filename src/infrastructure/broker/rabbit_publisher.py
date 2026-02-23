from aio_pika import (
    connect_robust,
    Message,
    DeliveryMode
)
from aio_pika.abc import (
    AbstractRobustChannel,
    AbstractRobustConnection
)
from src.application.interfaces.message_publisher import MessagePublisherInterface


class RabbitPublisher(MessagePublisherInterface):
    def __init__(
        self,
        conn_url: str,
        queue_name: str,
        task_name: str
    ):
        self._conn_url = conn_url
        self._connection: AbstractRobustConnection = None  # type: ignore[assignment]
        self._channel: AbstractRobustChannel = None  # type: ignore[assignment]
        self._queue_name = queue_name
        self._task_name = task_name

    async def connect(self):
        if not self._connection or self._connection.is_closed:
            self._connection = await connect_robust(self._conn_url)

    async def _check_connection(self):
        await self.connect()
        return self._connection

    async def _get_channel(self):
        if not self._channel or self._channel.is_closed:
            conn = await self._check_connection()
            self._channel = await conn.channel()
        return self._channel

    async def disconnect(self):
        if self._channel and self._channel.is_initialized:
            await self._channel.close()
        self._channel = None
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
        self._connection = None

    async def publish(self, data: str):
        chan = await self._get_channel()
        await chan.default_exchange.publish(
            Message(
                data.encode(),
                headers={"task_name": self._task_name},
                delivery_mode=DeliveryMode.PERSISTENT
            ),
            routing_key=self._queue_name
        )
