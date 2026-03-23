from typing import Optional

from runlet.application.interfaces.uow import UoWInterface
from runlet.application.interfaces.services import (
    AuthenticationServiceInterface,
    PasswordServiceInterface,
    EmailServiceInterface,
    EmailMessageTextTemplate
)
from runlet.application.dtos.auth import (
    LoginUserDTO,
    RegisterUserRequestDTO,
    ChangePasswordConfirmDTO,
)
from runlet.application.interfaces.repositories import UserRepositoryInterface
from .exceptions import (
    UndefinedUserError,
    InvalidUserPasswordError,
    PasswordsMismatchError,
    EmailExistsError,
    InactiveUserError,
    UndefinedCourseError,
    HasNoAccessError
)
from runlet.domain.entities import User
from .base import _CourseRepoRelatedInteractor


class _BaseAuthInteractor:
    def __init__(
        self,
        uow: UoWInterface,
        user_repo: UserRepositoryInterface,
        auth_service: AuthenticationServiceInterface,
    ):
        self._uow = uow
        self._auth_service = auth_service
        self._user_repo = user_repo

    async def __call__(self, token: str):
        user_id = self._auth_service.get_user_id_from_token(token)
        if not user_id:
            raise UndefinedUserError("User was not identify", status=401)
        async with self._uow:
            user = await self._user_repo.get_by_id(user_id)
            if not user:
                raise UndefinedUserError("User was not identify", status=401)
            if not user.is_active:
                raise InactiveUserError("Current user is inactive", status=403)
        return user_id


class AuthenticateUser(_BaseAuthInteractor):
    async def __call__(self, token: str | None) -> int:
        if not token:
            raise UndefinedUserError("Unauthorized", status=401)
        return await super().__call__(token)


class OptionalAuthenticateUser(_BaseAuthInteractor):
    async def __call__(self, token: Optional[str] = None):
        if not token:
            return None
        try:
            return await super().__call__(token)
        except Exception:
            return None


class AuthenticateUserAsStudent(_CourseRepoRelatedInteractor):
    async def __call__(self, user_id: int, course_id: int) -> int:
        async with self._uow:
            course = await self._course_repo.get_by_id(course_id)
            if not course:
                raise UndefinedCourseError("Course does not exist", status=404)
            if not await self._course_repo.check_user_in_course(user_id, course_id):
                raise HasNoAccessError("User not subscribed on course", status=403)
        return user_id


class AuthenticateUserAsTeacher(_CourseRepoRelatedInteractor):
    async def __call__(self, user_id: int, course_id: int) -> int:
        async with self._uow:
            course = await self._course_repo.get_by_id(course_id)
        if not course:
            raise UndefinedCourseError("Course does not exist", status=404)
        if course.teacher_id != user_id:
            raise HasNoAccessError("User cannot manage course", status=403)
        return user_id


class _BaseLoginRegRequestInteractor:
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


class LoginUser(_BaseLoginRegRequestInteractor):
    async def __call__(self, dto: LoginUserDTO) -> str:
        async with self._uow:
            user = await self._user_repo.get_by_email(dto.email)
        if not user:
            raise UndefinedUserError("User not found")
        if not user.is_active:
            token = self._auth_service.generate_token(user.id, 300)
            topic, message = EmailMessageTextTemplate.registration(f"{self._reg_confirm_url}/{token}")
            await self._email_service.send_mail(user.email, topic, message)
            raise InactiveUserError("Now user is inactive. Email with instructions sent", status=403)
        if not self._password_service.check_password(user.password, dto.password):
            raise InvalidUserPasswordError("Incorrect password")
        return self._auth_service.generate_token(user.id)


class RegisterUserRequest(_BaseLoginRegRequestInteractor):
    async def __call__(self, dto: RegisterUserRequestDTO):
        if dto.first_password != dto.second_password:
            raise PasswordsMismatchError("Passwords do not match")
        async with self._uow as uow:
            if await self._user_repo.count_by_email(dto.email):
                raise EmailExistsError(f"User with email {dto.email} already exists")
            registered = User(dto.email, self._password_service.hash_password(
                dto.first_password), dto.name)
            uow.add(registered)
            await uow.flush()
            token = self._auth_service.generate_token(registered.id, 300)
            topic, message = EmailMessageTextTemplate.registration(f"{self._reg_confirm_url}/{token}")
            await self._email_service.send_mail(registered.email, topic, message)


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

    async def __call__(self, token: str):
        user_id = self._auth_service.get_user_id_from_token(token)
        if not user_id:
            raise UndefinedUserError("User was not identify")
        async with self._uow:
            confirmed = await self._user_repo.get_by_id(user_id)
            if not confirmed:
                raise UndefinedUserError("Try to confirm registration of user that does not exist")
            confirmed.is_active = True


class ChangePasswordRequest:
    def __init__(
        self,
        uow: UoWInterface,
        user_repo: UserRepositoryInterface,
        token_service: AuthenticationServiceInterface,
        email_service: EmailServiceInterface,
        password_change_confirm_url: str
    ):
        self._uow = uow
        self._user_repo = user_repo
        self._token_service = token_service
        self._email_service = email_service
        self._password_change_confirm_url = password_change_confirm_url

    async def __call__(self, email: str):
        async with self._uow:
            user = await self._user_repo.get_by_email(email)
            if not user:
                raise UndefinedUserError("Email not found")
            token = self._token_service.generate_token(user.id, 300)
            topic, msg = EmailMessageTextTemplate.change_password(f"{self._password_change_confirm_url}/{token}")
            await self._email_service.send_mail(user.email, topic, msg)


class ChangePasswordConfirm:
    def __init__(
        self,
        uow: UoWInterface,
        user_repo: UserRepositoryInterface,
        token_service: AuthenticationServiceInterface,
        password_service: PasswordServiceInterface
    ):
        self._uow = uow
        self._user_repo = user_repo
        self._token_service = token_service
        self._password_service = password_service

    async def __call__(self, token: str, dto: ChangePasswordConfirmDTO):
        async with self._uow:
            user_id = self._token_service.get_user_id_from_token(token)
            if not user_id:
                raise UndefinedUserError("User was not identify")
            if dto.first_password != dto.second_password:
                raise PasswordsMismatchError("Passwords do not match")
            user = await self._user_repo.get_by_id(user_id)
            if not user:
                raise UndefinedUserError("User not found")
            user.password = self._password_service.hash_password(dto.first_password)
