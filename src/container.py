from collections.abc import AsyncGenerator

from fastapi import Depends, Cookie, Path
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.application.messaging.registries import MessageConsumerRegistry
from src.application.use_cases import *
from src.application.interfaces.repositories import *

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
from src.infrastructure.uow import AlchemyUoW

from src.interfaces.broker.rabbitmq.callback import callback_registry

from src.logger import logger


_engine = create_async_engine(db_conf.conn_url())
_session_factory = async_sessionmaker(
    _engine, expire_on_commit=False, autoflush=False, autobegin=False)
rabbit_consumer_factory = RabbitMQConsumerFactory()
consumers_registry = MessageConsumerRegistry(rabbit_consumer_factory)
consumers_registry.register("callback", callback_registry)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with _session_factory() as session:
        yield session


def get_uow(session: AsyncSession):
    return AlchemyUoW(session)


def get_user_repository(session: AsyncSession):
    return AlchemyUserRepository(session)


def get_course_repository(session: AsyncSession):
    return AlchemyCourseRepository(session)


def get_jwt_auth_service():
    return JWTAuthenticationService(app_conf.token_expire_time, app_conf.secret)


def get_password_service():
    return PasswordService()


def get_email_service():
    return AsyncEmailService()


def get_auth_usecase(session: AsyncSession = Depends(get_db_session)):
    return AuthenticateUser(
        get_uow(session),
        get_user_repository(session),
        get_jwt_auth_service()
    )


def get_register_request_usecase(session: AsyncSession = Depends(get_db_session)):
    return RegisterUserRequest(
        get_uow(session),
        get_user_repository(session),
        get_password_service(),
        get_jwt_auth_service(),
        get_email_service(),
        app_conf.reg_confirm_url
    )


def get_register_confirm_usecase(session: AsyncSession = Depends(get_db_session)):
    return RegisterUserConfirm(
        get_uow(session),
        get_user_repository(session),
        get_jwt_auth_service()
    )


def get_create_course_use_case(session: AsyncSession = Depends(get_db_session)):
    return CreateCourse(
        get_uow(session)
    )


def get_add_problems_modules_use_case(session: AsyncSession = Depends(get_db_session)):
    return AddProblemsModules(
        get_uow(session)
    )


def get_update_course_data_use_case(session: AsyncSession = Depends(get_db_session)):
    return UpdateCourseData(
        get_uow(session),
        get_course_repository(session)
    )


def get_show_teacher_course_use_case(session: AsyncSession = Depends(get_db_session)):
    return ShowTeacherCourse(
        get_uow(session),
        get_course_repository(session)
    )


def get_add_course_tags_use_case(session: AsyncSession = Depends(get_db_session)):
    return AddCourseTags(
        get_uow(session),
        get_course_repository(session),
        get_user_repository(session)
    )


def get_login_usecase(session: AsyncSession = Depends(get_db_session)):
    return LoginUser(
        get_uow(session),
        get_user_repository(session),
        get_password_service(),
        get_jwt_auth_service()
    )


def get_show_student_courses_use_case(session: AsyncSession = Depends(get_db_session)):
    return ShowStudentCourses(
        get_uow(session),
        get_course_repository(session)
    )


def get_show_student_course_use_case(session: AsyncSession = Depends(get_db_session)):
    return ShowStudentCourse(
        get_uow(session),
        get_course_repository(session),
    )


def get_auth_user_as_teacher_use_case(session: AsyncSession = Depends(get_db_session)):
    return AuthenticateUserAsTeacher(
        get_uow(session),
        get_course_repository(session)
    )


def get_auth_user_as_student_use_case(session: AsyncSession = Depends(get_db_session)):
    return AuthenticateUserAsStudent(
        get_uow(session),
        get_course_repository(session)
    )


async def auth_user(use_case: AuthenticateUser = Depends(get_auth_usecase), token: str = Cookie(default=None, include_in_schema=False)):
    return await use_case.execute(token)


async def auth_teacher(course_id: int = Path(...), use_case: AuthenticateUserAsTeacher = Depends(get_auth_user_as_teacher_use_case), user_id: int = Depends(auth_user)):
    return await use_case.execute(user_id, course_id)


async def auth_student(course_id: int = Path(...), use_case: AuthenticateUserAsStudent = Depends(get_auth_user_as_student_use_case), user_id: int = Depends(auth_user)):
    return await use_case.execute(user_id, course_id)
