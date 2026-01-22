import pytest
from unittest.mock import AsyncMock, MagicMock, Mock

from src.application.use_cases.auth import (
    AuthenticateUser,
    AuthenticateUserAsStudent,
    AuthenticateUserAsTeacher,
    LoginUser,
    RegisterUserRequest,
    RegisterUserConfirm
)


@pytest.fixture
def mock_uow():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None

    return uow


@pytest.fixture
def mock_user_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_auth_service():
    service = MagicMock()
    return service


@pytest.fixture
def mock_course_repo():
    return AsyncMock()


@pytest.fixture
def mock_password_service():
    return Mock()


@pytest.fixture
def mock_email_service():
    return AsyncMock()


@pytest.fixture
def login_user(
    mock_uow,
    mock_user_repo,
    mock_password_service,
    mock_auth_service
):
    return LoginUser(
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service
    )


@pytest.fixture
def authenticate_user(mock_uow, mock_user_repo, mock_auth_service):
    return AuthenticateUser(mock_uow, mock_user_repo, mock_auth_service)


@pytest.fixture
def auth_student(mock_uow, mock_course_repo):
    return AuthenticateUserAsStudent(mock_uow, mock_course_repo)


@pytest.fixture
def auth_teacher(mock_uow, mock_course_repo):
    return AuthenticateUserAsTeacher(mock_uow, mock_course_repo)


@pytest.fixture
def register_user_request(
    mock_uow,
    mock_user_repo,
    mock_password_service,
    mock_auth_service,
    mock_email_service
):
    return RegisterUserRequest(
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        reg_confirm_url="https://example.com/confirm"
    )


@pytest.fixture
def register_user_confirm(mock_uow, mock_user_repo, mock_auth_service):
    return RegisterUserConfirm(mock_uow, mock_user_repo, mock_auth_service)
