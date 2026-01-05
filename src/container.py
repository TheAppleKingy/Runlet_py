from application.interfaces.services import EmailServiceInterface, AuthenticationServiceInterface, PasswordServiceInterface
from infrastructure.services.user import PasswordService, JWTAuthenticationService
from interfaces.http import AuthenticatedUserId
from application.use_cases.user import AuthenticateUser


def get_jwt_auth_service() -> AuthenticationServiceInterface:
    return JWTAuthenticationService()


def get_password_service() -> PasswordServiceInterface:
    return PasswordService()


def auth_user() -> AuthenticatedUserId:
    service = get_jwt_auth_service()
