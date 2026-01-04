from typing import Protocol

from .consumer import MessageConsumerInterface


class MessageConsumerFactoryInterface(Protocol):
    def create(self, *args, **kwargs) -> MessageConsumerInterface: ...
