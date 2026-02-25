# ruff: noqa: F405
from typing import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine
)
from dishka import (
    make_async_container,
    Scope,
    provide,
    Provider
)
from dishka.integrations.fastapi import FastapiProvider

from runlet.application.interactors import *  # noqa: F403
from runlet.application.interfaces.repositories import *  # noqa: F403
from runlet.application.interfaces.uow import UoWInterface
from runlet.application.interfaces.message_publisher import MessagePublisherInterface
from runlet.application.interfaces.services import *  # noqa: F403
from runlet.infrastructure.services.user import *  # noqa: F403
from runlet.infrastructure.services import *  # noqa: F403
from runlet.infrastructure.configs import (
    DBConfig,
    EmailConfig,
    AppConfig,
    RabbitMQConfig
)
from runlet.infrastructure.repositories import *  # noqa: F403
from runlet.infrastructure.uow import AlchemyUoW
from runlet.infrastructure.broker import RabbitPublisher
from runlet.domain.value_objects import (
    AuthenticatedUserId,
    AuthenticatedStudentId,
    AuthenticatedTeacherId,
    AuthenticatedNotStrictlyUserId
)


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


class BrokerProvider(Provider):
    scope = Scope.APP

    @provide
    def rabbit_conf(self) -> RabbitMQConfig:
        return RabbitMQConfig()  # type: ignore[call-arg]

    @provide
    def publisher(self, conf: RabbitMQConfig) -> MessagePublisherInterface:
        return RabbitPublisher(conf.conn_url)


class RepoProvider(Provider):
    scope = Scope.REQUEST

    uow = provide(AlchemyUoW, provides=UoWInterface)
    attempt_repo = provide(AlchemyAttemptRepository, provides=AttemptRepositoryInterface)
    module_repo = provide(AlchemyModuleRepository, provides=ModuleRepositoryInterface)
    user_repo = provide(AlchemyUserRepository, provides=UserRepositoryInterface)
    course_repo = provide(AlchemyCourseRepository, provides=CourseRepositoryInterface)
    problem_repo = provide(AlchemyProblemRepository, provides=ProblemRepositoryInterface)


class ApplicationServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def get_app_conf(self) -> AppConfig:
        return AppConfig()  # type: ignore

    @provide(scope=Scope.APP)
    def get_email_conf(self) -> EmailConfig:
        return EmailConfig()  # type: ignore

    password_service = provide(PasswordService, provides=PasswordServiceInterface)
    email_service = provide(BrokerEmailService, provides=EmailServiceInterface)

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

    @provide
    def change_password_request(
        self,
        conf: AppConfig,
        uow: UoWInterface,
        user_repo: UserRepositoryInterface,
        token_service: AuthenticationServiceInterface,
        email_service: EmailServiceInterface
    ) -> ChangePasswordRequest:
        return ChangePasswordRequest(
            uow,
            user_repo,
            token_service,
            email_service,
            conf.password_change_confirm_url
        )


interactors_provider = UseCaseProvider(scope=Scope.REQUEST)
interactors_provider.provide_all(
    AuthenticateUser,
    OptionalAuthenticateUser,
    RegisterUserConfirm,
    CreateCourse,
    UpdateCourseData,
    ShowTeacherCourseModulesToRateStudents,
    ShowTeacherCourseTagsToRateStudents,
    CreateUpdateProblem,
    DeleteProblems,
    ManageStudents,
    ManageTags,
    ManageModules,
    ShowStudentCourses,
    ShowStudentCourse,
    ShowCourse,
    ShowMain,
    AuthenticateUserAsTeacher,
    AuthenticateUserAsStudent,
    RequestSubscribeOnCourse,
    SubscribeOnCourseByLink,
    SubscribeOnCourse,
    ShowTeacherCourseData,
    ChangePasswordConfirm,
    ShowStudentProblems,
    ShowProblemStudents,
    ShowTagsToUpdate,
    ShowProblemDataToUpdate,
    SearchStudents,
    ShowMyProfile,
    ShowProblemToSolve,
    ShowStudentProblemInfoToRate,
    SendProblemSolution,
    HandleTestResult,
    RateStudent
)


class AuthProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def auth_user(self, r: Request, interactor: AuthenticateUser) -> AuthenticatedUserId:
        return AuthenticatedUserId(await interactor(r.cookies.get("token")))

    @provide
    async def optional_auth_user(self, r: Request, interactor: OptionalAuthenticateUser) -> AuthenticatedNotStrictlyUserId:
        return AuthenticatedUserId(await interactor(r.cookies.get("token")))

    @provide
    async def auth_student(
        self,
        r: Request,
        interactor: AuthenticateUserAsStudent,
        user_id: AuthenticatedUserId
    ) -> AuthenticatedStudentId:
        return AuthenticatedStudentId(await interactor(user_id, int(
            r.path_params.get("course_id")  # type: ignore
        )))

    @provide
    async def auth_teacher(
        self,
        r: Request,
        interactor: AuthenticateUserAsTeacher,
        user_id: AuthenticatedUserId
    ) -> AuthenticatedTeacherId:
        return AuthenticatedTeacherId(await interactor(user_id, int(
            r.path_params.get("course_id")  # type: ignore
        )))


container = make_async_container(
    interactors_provider,
    DBProvider(),
    RepoProvider(),
    ApplicationServiceProvider(),
    AuthProvider(),
    BrokerProvider(),
    FastapiProvider()
)
