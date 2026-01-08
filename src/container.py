from collections.abc import AsyncGenerator

from sqlalchemy import exc
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from application.interfaces.services import EmailServiceInterface, AuthenticationServiceInterface, PasswordServiceInterface
from application.messaging.registries import MessageConsumerRegistry
from infrastructure.services.user import *
from infrastructure.services import *
from infrastructure.configs import (
    db_conf,
    email_conf,
    rabbit_conf,
    app_conf
)
from infrastructure.broker.factories import RabbitMQConsumerFactory
from interfaces.http import AuthenticatedUserId
from interfaces.broker.rabbitmq.callback import callback_registry
from application.use_cases.user import AuthenticateUser

_engine = create_async_engine(db_conf.conn_url())
_async_session_factory = async_sessionmaker(_engine, expire_on_commit=True, autoflush=False)

rabbit_consumer_factory = RabbitMQConsumerFactory()
consumers_registry = MessageConsumerRegistry(rabbit_consumer_factory)
consumers_registry.register("callback", callback_registry)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with _async_session_factory() as session:
        yield session


def get_jwt_auth_service() -> AuthenticationServiceInterface:
    return JWTAuthenticationService()


def get_password_service() -> PasswordServiceInterface:
    return PasswordService()


def email_service() -> EmailServiceInterface:
    return AsyncEmailService()


def auth_user() -> AuthenticatedUserId:
    service = get_jwt_auth_service()
