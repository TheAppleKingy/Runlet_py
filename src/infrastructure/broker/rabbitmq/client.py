from typing import Optional

from aio_pika import connect_robust
from aio_pika.abc import AbstractRobustConnection

from ...configs import rabbit_conf


class RabbitMQClient:
    def __init__(self):
        self._connection: Optional[AbstractRobustConnection] = None

    async def connect(self) -> None:
        if not self._connection or self._connection.is_closed:
            self._connection = await connect_robust(rabbit_conf.conn_url())

    async def disconnect(self) -> None:
        if self._connection:
            await self._connection.close()
            self._connection = None
