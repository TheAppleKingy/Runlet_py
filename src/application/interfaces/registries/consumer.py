from typing import Protocol


class MessageConsumerRegistry(Protocol):
    async def register(self, *args, **kwargs): ...
