from application.interfaces.uow import ReadUserUoW, ReadWriteUserUoW
from application.interfaces.services import AuthenticationServiceInterface, PasswordServiceInterface, EmailServiceInterface
from application.dtos.auth import LoginUserDTO, RegisterUserRequestDTO
from .exceptions import UndefinedUserError, InvalidUserPasswordError, PasswordsMismatchError, EmailExistsError


class AuthenticateUser:
    def __init__(
        self,
        uow: ReadUserUoW,
        auth_service: AuthenticationServiceInterface,
    ):
        self._uow = uow
        self._auth_service = auth_service

    async def execute(self, token: str):
        user_id = self._auth_service.get_user_id_from_token(token)
        if not user_id:
            raise UndefinedUserError("User was not identify by token")
        async with self._uow as uow:
            user = await uow.user_repo.get_by_id(user_id)
        if not user:
            raise UndefinedUserError("User was not identify by token")


class LoginUser:
    def __init__(
        self,
        uow: ReadUserUoW,
        password_service: PasswordServiceInterface,
        auth_service: AuthenticationServiceInterface
    ):
        self._uow = uow
        self._password_service = password_service
        self._auth_service = auth_service

    async def execute(self, dto: LoginUserDTO) -> str:
        async with self._uow as uow:
            user = await uow.user_repo.get_by_email(dto.email)
        if not user:
            raise UndefinedUserError(f"User with email {dto.email} not found")
        if not self._password_service.check_password(user.password, dto.password):
            raise InvalidUserPasswordError("Incorrect password")
        return self._auth_service.generate_token(user.id)


class RegisterUserRequest:
    def __init__(
        self,
        uow: ReadWriteUserUoW,
        password_service: PasswordServiceInterface,
        auth_service: AuthenticationServiceInterface,
        email_service: EmailServiceInterface
    ):
        self._uow = uow
        self._password_service = password_service
        self._auth_service = auth_service
        self._email_service = email_service

    async def execute(self, dto: RegisterUserRequestDTO) -> str:
        if dto.first_password != dto.second_password:
            raise PasswordsMismatchError("Passwords do not match")
        async with self._uow as uow:
            if await uow.user_repo.count_by_email(dto.email):
                raise EmailExistsError(f"User with email {dto.email} already exists")
            created = await uow.user_repo.create(dto.name, dto.email, dto.first_password)
            message = f"Hello! Confirm your registration on Runlet following by link:\n{self._auth_service.reg_confirm_url}"
            self._email_service.send_mail(created.email, "Registration confirm", message)
            return self._auth_service.generate_token(created.id)


class RegisterUserConfirm:
    def __init__(
        self,
        uow: ReadWriteUserUoW,
        auth_service: AuthenticationServiceInterface,
    ):
        self._uow = uow
        self._auth_service = auth_service

    async def execute(self, token: str):
        user_id = self._auth_service.get_user_id_from_token(token)
        if not user_id:
            raise UndefinedUserError("User wan not identify")
        async with self._uow as uow:
            confirmed = await uow.user_repo.get_by_id(user_id)
            if not confirmed:
                raise
            if confirmed.is_active:
                raise
            confirmed.is_active = True
