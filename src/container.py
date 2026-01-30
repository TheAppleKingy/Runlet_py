from typing import Optional, AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
from ploomby.rabbit import RabbitConsumerFactory
from ploomby.registry import MessageConsumerRegistry
from dishka import make_async_container, Scope, provide, Provider
from dishka.integrations.fastapi import FastapiProvider

from src.application.use_cases import *
from src.application.interfaces.repositories import *
from src.application.interfaces.uow import UoWInterface
from src.application.interfaces.services import *
from src.infrastructure.services.user import *
from src.infrastructure.services import *
from src.infrastructure.configs import (
    DBConfig,
    EmailConfig,
    AppConfig
)
from src.infrastructure.repositories import *
from src.infrastructure.uow import AlchemyUoW
from src.interfaces.broker.rabbitmq import callback_registry
from src.domain.value_objects import (
    AuthenticatedUserId,
    AuthenticatedStudentId,
    AuthenticatedTeacherId,
    AuthenticatedNotStrictlyUserId
)


# _consumer_factory = RabbitConsumerFactory(rabbit_conf.conn_url())
# consumer_registry = MessageConsumerRegistry(callback_registry, _consumer_factory)


class DBProvider(Provider):
    scope = Scope.APP

    @provide
    def get_db_conf(self) -> DBConfig:
        return DBConfig()  # type: ignore

    @provide
    def get_engine(self, config: DBConfig) -> AsyncEngine:
        return create_async_engine(config.conn_url)

    @provide
    def get_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            engine,
            expire_on_commit=False,
            autoflush=False,
            autobegin=False
        )

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self,
        sessionmaker: async_sessionmaker[AsyncSession]
    ) -> AsyncGenerator[AsyncSession, None]:
        async with sessionmaker() as session:
            try:
                yield session
            finally:
                await session.close()


class RepoProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_uow(self, session: AsyncSession) -> UoWInterface:
        return AlchemyUoW(session)

    @provide
    def get_user_alchemy_repo(self, session: AsyncSession) -> UserRepositoryInterface:
        return AlchemyUserRepository(session)

    @provide
    def get_course_alchemy_repo(self, session: AsyncSession) -> CourseRepositoryInterface:
        return AlchemyCourseRepository(session)


class ApplicationServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def get_app_conf(self) -> AppConfig:
        return AppConfig()  # type: ignore

    @provide(scope=Scope.APP)
    def get_email_conf(self) -> EmailConfig:
        return EmailConfig()  # type: ignore

    password_service = provide(PasswordService, provides=PasswordServiceInterface)
    email_service = provide(AsyncEmailService, provides=EmailServiceInterface)

    @provide(provides=AuthenticationServiceInterface)
    def get_jwt_auth_service(self, conf: AppConfig) -> AuthenticationServiceInterface:
        return JWTAuthenticationService(conf.token_expire_time, conf.secret)


class UseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_register_user_request(
        self,
        conf: AppConfig,
        uow: UoWInterface,
        user_repo: UserRepositoryInterface,
        password_service: PasswordServiceInterface,
        auth_service: AuthenticationServiceInterface,
        email_service: EmailServiceInterface,
    ) -> RegisterUserRequest:
        return RegisterUserRequest(
            uow,
            user_repo,
            password_service,
            auth_service,
            email_service,
            conf.reg_confirm_url
        )

    @provide
    def get_generate_invite_link(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
        token_service: AuthenticationServiceInterface,
        conf: AppConfig
    ) -> GenerateInviteLink:
        return GenerateInviteLink(
            uow,
            course_repo,
            conf.invite_confirm_url,
            conf.invite_expire_time,
            token_service
        )

    @provide
    def login(
        self,
        conf: AppConfig,
        uow: UoWInterface,
        user_repo: UserRepositoryInterface,
        password_service: PasswordServiceInterface,
        auth_service: AuthenticationServiceInterface,
        email_service: EmailServiceInterface,
    ) -> LoginUser:
        return LoginUser(
            uow,
            user_repo,
            password_service,
            auth_service,
            email_service,
            conf.reg_confirm_url
        )


use_case_provider = UseCaseProvider()
use_case_provider.provide_all(
    AuthenticateUser,
    OptionalAuthenticateUser,
    RegisterUserConfirm,
    CreateCourse,
    UpdateCourseData,
    ShowTeacherCourseToManageStudents,
    ShowTeacherCourseToManageProblems,
    AddProblem,
    DeleteProblems,
    AddStudents,
    DeleteStudents,
    AddTags,
    DeleteTags,
    DeleteModules,
    ShowStudentCourses,
    ShowStudentCourse,
    ShowCourse,
    ShowMain,
    AuthenticateUserAsTeacher,
    AuthenticateUserAsStudent,
    RequestSubscribeOnCourse,
    SubscribeOnCourseByLink,
    SubscribeOnCourse,
)


class AuthProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def auth_user(self, r: Request, use_case: AuthenticateUser) -> AuthenticatedUserId:
        return AuthenticatedUserId(await use_case.execute(r.cookies.get("token")))

    @provide
    async def optional_auth_user(self, r: Request, use_case: OptionalAuthenticateUser) -> AuthenticatedNotStrictlyUserId:
        return AuthenticatedUserId(await use_case.execute(r.cookies.get("token")))

    @provide
    async def auth_student(
        self,
        r: Request,
        use_case: AuthenticateUserAsStudent,
        user_id: AuthenticatedUserId
    ) -> AuthenticatedStudentId:
        return AuthenticatedStudentId(await use_case.execute(user_id, int(
            r.path_params.get("course_id")  # type: ignore
        )))

    @provide
    async def auth_teacher(
        self,
        r: Request,
        use_case: AuthenticateUserAsTeacher,
        user_id: AuthenticatedUserId
    ) -> AuthenticatedTeacherId:
        return AuthenticatedTeacherId(await use_case.execute(user_id, int(
            r.path_params.get("course_id")  # type: ignore
        )))


container = make_async_container(
    use_case_provider,
    DBProvider(),
    RepoProvider(),
    ApplicationServiceProvider(),
    AuthProvider(),
    FastapiProvider()
)
