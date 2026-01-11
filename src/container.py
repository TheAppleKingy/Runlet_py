from collections.abc import AsyncGenerator

from fastapi import Depends, Cookie
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.application.messaging.registries import MessageConsumerRegistry
from src.application.use_cases.user import *

from src.infrastructure.services.user import *
from src.infrastructure.services import *
from src.infrastructure.configs import (
    db_conf,
    email_conf,
    rabbit_conf,
    app_conf
)
from src.infrastructure.repositories import *
from src.infrastructure.broker.factories import RabbitMQConsumerFactory
from src.infrastructure.uow import AlchemyReadUow, AlchemyReadWriteUow

from src.interfaces.broker.rabbitmq.callback import callback_registry

from src.domain.interfaces.repositories import *

_engine = create_async_engine(db_conf.conn_url())
_session_factory = async_sessionmaker(_engine, expire_on_commit=True, autoflush=False)
rabbit_consumer_factory = RabbitMQConsumerFactory()
consumers_registry = MessageConsumerRegistry(rabbit_consumer_factory)
consumers_registry.register("callback", callback_registry)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with _session_factory() as session:
        yield session


def get_read_uow(session: AsyncSession):
    return AlchemyReadUow(session)


def get_rw_uow(session: AsyncSession):
    return AlchemyReadWriteUow(session)


def get_user_repository(session: AsyncSession):
    return AlchemyUserRepository(session)


def get_jwt_auth_service():
    return JWTAuthenticationService(app_conf.token_expire_time, app_conf.secret)


def get_password_service():
    return PasswordService()


def get_email_service():
    return AsyncEmailService()


def get_auth_usecase(session: AsyncSession = Depends(get_db_session)):
    return AuthenticateUser(
        get_read_uow(session),
        get_user_repository(session),
        get_jwt_auth_service()
    )


def get_register_request_usecase(session: AsyncSession = Depends(get_db_session)):
    return RegisterUserRequest(
        get_rw_uow(session),
        get_user_repository(session),
        get_password_service(),
        get_jwt_auth_service(),
        get_email_service(),
        app_conf.reg_confirm_url
    )


def get_register_confirm_usecase(session: AsyncSession = Depends(get_db_session)):
    return RegisterUserConfirm(
        get_rw_uow(session),
        get_user_repository(session),
        get_jwt_auth_service()
    )


def get_login_usecase(session: AsyncSession = Depends(get_db_session)):
    return LoginUser(
        get_read_uow(session),
        get_user_repository(session),
        get_password_service(),
        get_jwt_auth_service()
    )


async def auth_user(token: str = Cookie(default=None, include_in_schema=False)):
    use_case = get_auth_usecase()
    return await use_case.execute(token)
