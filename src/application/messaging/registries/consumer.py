from application.interfaces.broker import MessageConsumerInterface, MessageConsumerFactoryInterface
from application.interfaces.registries import HandlersRegistryInterface


class MessageConsumerRegistry:
    def __init__(self, factory: MessageConsumerFactoryInterface):
        self._factory = factory
        self._consumers_map: dict[str, MessageConsumerInterface] = {}

    async def register(self, queue_name: str, handlers_registry: HandlersRegistryInterface):
        if queue_name in self._consumers_map:
            raise
        consumer = self._factory.create()
        self._consumers_map[queue_name] = consumer
        consumer.set_handlers_map(handlers_registry.as_dict())
        await consumer.start_consuming()
