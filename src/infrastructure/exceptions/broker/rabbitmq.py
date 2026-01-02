from ..base import InfrastructureError


class RabbitMQClientError(InfrastructureError):
    pass


class NoConnectionError(RabbitMQClientError):
    pass


class NoChannelError(RabbitMQClientError):
    pass


class NoTaskNameError(InfrastructureError):
    pass
