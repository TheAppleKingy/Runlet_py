from application.interfaces.services import EmailServiceInterface, AuthenticationServiceInterface, PasswordServiceInterface
from application.messaging.registries import MessageConsumerRegistry
from infrastructure.services.user import PasswordService, JWTAuthenticationService
from infrastructure.broker.factories import RabbitMQConsumerFactory
from interfaces.http import AuthenticatedUserId
from interfaces.broker.rabbitmq.callback import callback_registry
from application.use_cases.user import AuthenticateUser

rabbit_consumer_factory = RabbitMQConsumerFactory()
consumers_registry = MessageConsumerRegistry(rabbit_consumer_factory)
consumers_registry.register("callback", callback_registry)


def get_jwt_auth_service() -> AuthenticationServiceInterface:
    return JWTAuthenticationService()


def get_password_service() -> PasswordServiceInterface:
    return PasswordService()


def auth_user() -> AuthenticatedUserId:
    service = get_jwt_auth_service()
