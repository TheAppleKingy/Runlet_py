from src.application.interfaces.uow import UoWInterface
from src.application.interfaces.services import AuthenticationServiceInterface, PasswordServiceInterface, EmailServiceInterface
from src.application.dtos.auth import LoginUserDTO, RegisterUserRequestDTO
from src.application.interfaces.repositories import UserRepositoryInterface, CourseRepositoryInterface
from .exceptions import (
    UndefinedUserError,
    InvalidUserPasswordError,
    PasswordsMismatchError,
    EmailExistsError,
    InactiveUserError,
    UndefinedCourseError,
    HasNoAccessError
)
from src.logger import logger

__all__ = [
    "AuthenticateUser",
    "LoginUser",
    "RegisterUserRequest",
    "RegisterUserConfirm",
    "AuthenticateUserAsTeacher",
    "AuthenticateUserAsStudent"
]


class AuthenticateUser:
    def __init__(
        self,
        uow: UoWInterface,
        user_repo: UserRepositoryInterface,
        auth_service: AuthenticationServiceInterface,
    ):
        self._uow = uow
        self._auth_service = auth_service
        self._user_repo = user_repo

    async def execute(self, token: str) -> int:
        user_id = self._auth_service.get_user_id_from_token(token)
        if not user_id:
            raise UndefinedUserError("User was not identify by token", status=403)
        async with self._uow:
            user = await self._user_repo.get_by_id(user_id)
            if not user:
                raise UndefinedUserError("User was not identify by token", status=403)
            if not user.is_active:
                raise InactiveUserError("Current user is inactive", 403)
        return user_id


class AuthenticateUserAsStudent:
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface
    ):
        self._course_repo = course_repo
        self._uow = uow

    async def execute(self, user_id: int, course_id: int) -> int:
        async with self._uow:
            subscribed = await self._course_repo.check_user_in_course(user_id, course_id)
        if not subscribed:
            raise PermissionError("User not subscribed on course")
        return user_id


class AuthenticateUserAsTeacher:
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface
    ):
        self._course_repo = course_repo
        self._uow = uow

    async def execute(self, user_id: int, course_id: int) -> int:
        async with self._uow:
            course = await self._course_repo.get_by_id(course_id)
        if not course:
            return user_id
        if course.teacher_id != user_id:
            raise HasNoAccessError(f"User {user_id} cannot manage course {course.id}", 403)
        return user_id


class LoginUser:
    def __init__(
        self,
        uow: UoWInterface,
        user_repo: UserRepositoryInterface,
        password_service: PasswordServiceInterface,
        auth_service: AuthenticationServiceInterface
    ):
        self._uow = uow
        self._user_repo = user_repo
        self._password_service = password_service
        self._auth_service = auth_service

    async def execute(self, dto: LoginUserDTO) -> str:
        async with self._uow:
            user = await self._user_repo.get_by_email(dto.email)
        if not user:
            raise UndefinedUserError(f"User with email {dto.email} not found")
        if not self._password_service.check_password(user.password, dto.password):
            raise InvalidUserPasswordError("Incorrect password")
        return self._auth_service.generate_token(user.id)


class RegisterUserRequest:
    def __init__(
        self,
        uow: UoWInterface,
        user_repo: UserRepositoryInterface,
        password_service: PasswordServiceInterface,
        auth_service: AuthenticationServiceInterface,
        email_service: EmailServiceInterface,
        reg_confirm_url: str
    ):
        self._uow = uow
        self._user_repo = user_repo
        self._password_service = password_service
        self._auth_service = auth_service
        self._email_service = email_service
        self._reg_confirm_url = reg_confirm_url

    async def execute(self, dto: RegisterUserRequestDTO):
        if dto.first_password != dto.second_password:
            raise PasswordsMismatchError("Passwords do not match")
        async with self._uow:
            if await self._user_repo.count_by_email(dto.email):
                raise EmailExistsError(f"User with email {dto.email} already exists")
            created = await self._user_repo.create(dto.name, dto.email, self._password_service.hash_password(dto.first_password))
            token = self._auth_service.generate_token(created.id, 300)
            message = f"Hello! Confirm your registration on Runlet following by link:\n{self._reg_confirm_url}/{token}"
            await self._email_service.send_mail(created.email, "Registration confirm", message)


class RegisterUserConfirm:
    def __init__(
        self,
        uow: UoWInterface,
        user_repo: UserRepositoryInterface,
        auth_service: AuthenticationServiceInterface,
    ):
        self._uow = uow
        self._user_repo = user_repo
        self._auth_service = auth_service

    async def execute(self, token: str):
        user_id = self._auth_service.get_user_id_from_token(token)
        if not user_id:
            raise UndefinedUserError("User was not identify")
        async with self._uow:
            confirmed = await self._user_repo.get_by_id(user_id)
            if not confirmed:
                raise UndefinedUserError("Try to confirm registration of user that does not exist")
            confirmed.is_active = True
