import pytest
from unittest.mock import AsyncMock, MagicMock

from src.domain.entities import (
    User,
    Course
)
from src.application.interfaces.uow import UoWInterface
from src.application.interfaces.repositories import *
from src.application.interfaces.services import *
from src.application.interactors import *


@pytest.fixture
def mock_uow():
    """Create a mock UoW"""
    uow = AsyncMock(spec=UoWInterface)
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow


@pytest.fixture
def mock_user_repo():
    """Create a mock user repository"""
    return AsyncMock(spec=UserRepositoryInterface)


@pytest.fixture
def mock_course_repo():
    """Create a mock course repository"""
    return AsyncMock(spec=CourseRepositoryInterface)


@pytest.fixture
def mock_email_service():
    """Create a mock email service"""
    return AsyncMock(spec=EmailServiceInterface)


@pytest.fixture
def mock_auth_service():
    """Create a mock authentication service"""
    return MagicMock(spec=AuthenticationServiceInterface)


@pytest.fixture
def mock_token_service():
    """Create a mock token service"""
    return MagicMock(spec=AuthenticationServiceInterface)


@pytest.fixture
def mock_password_service():
    """Create a mock password service"""
    return MagicMock(spec=PasswordServiceInterface)


@pytest.fixture
def reg_confirm_url():
    """Registration confirmation URL"""
    return "https://runlet.app/confirm-registration"


@pytest.fixture
def password_change_confirm_url():
    """Password change confirmation URL"""
    return "https://runlet.app/change-password"


@pytest.fixture
def authenticate_user(mock_uow, mock_user_repo, mock_auth_service):
    """Create AuthenticateUser instance with mocks"""
    return AuthenticateUser(
        uow=mock_uow,
        user_repo=mock_user_repo,
        auth_service=mock_auth_service
    )


@pytest.fixture
def existing_course():
    """Create a test course"""
    course = Course(
        name="Test Course",
        _teacher_id=1,
        description="Test Description",
        is_private=False,
        notify_request_sub=False
    )
    course.id = 1
    return course


@pytest.fixture
def private_course():
    """Create a test private course"""
    course = Course(
        name="Private Course",
        _teacher_id=1,
        description="Private Description",
        is_private=True,
        notify_request_sub=True
    )
    course.id = 2
    return course


@pytest.fixture
def course_with_teacher():
    """Create a test course with teacher_id=1"""
    course = Course(
        name="Test Course",
        _teacher_id=1,
        description="Test Description",
        is_private=False,
        notify_request_sub=False
    )
    course.id = 1
    return course


@pytest.fixture
def course_with_different_teacher():
    """Create a test course with teacher_id=2"""
    course = Course(
        name="Other Course",
        _teacher_id=2,
        description="Other Description",
        is_private=True,
        notify_request_sub=True
    )
    course.id = 2
    return course


@pytest.fixture
def active_user():
    """Create a test active user"""
    user = User(
        email="active@example.com",
        password="hashed_password",
        name="Active User"
    )
    # Set id and is_active after creation since they're init=False
    user.id = 2
    user.is_active = True
    return user


@pytest.fixture
def inactive_user():
    """Create a test inactive user"""
    user = User(
        email="inactive@example.com",
        password="hashed_password",
        name="Inactive User"
    )
    user.id = 1
    user.is_active = False
    return user


@pytest.fixture
def optional_authenticate_user(mock_uow, mock_user_repo, mock_auth_service):
    """Create OptionalAuthenticateUser instance with mocks"""
    return OptionalAuthenticateUser(
        uow=mock_uow,
        user_repo=mock_user_repo,
        auth_service=mock_auth_service
    )


@pytest.fixture
def authenticate_user_as_student(mock_uow, mock_course_repo):
    """Create AuthenticateUserAsStudent instance with mocks"""
    return AuthenticateUserAsStudent(
        uow=mock_uow,
        course_repo=mock_course_repo
    )


@pytest.fixture
def authenticate_user_as_teacher(mock_uow, mock_course_repo):
    """Create AuthenticateUserAsTeacher instance with mocks"""
    return AuthenticateUserAsTeacher(
        uow=mock_uow,
        course_repo=mock_course_repo
    )


@pytest.fixture
def login_user(
    mock_uow,
    mock_user_repo,
    mock_password_service,
    mock_auth_service,
    mock_email_service,
    reg_confirm_url
):
    """Create LoginUser instance with mocks"""
    return LoginUser(
        uow=mock_uow,
        user_repo=mock_user_repo,
        password_service=mock_password_service,
        auth_service=mock_auth_service,
        email_service=mock_email_service,
        reg_confirm_url=reg_confirm_url
    )


@pytest.fixture
def register_user_request(
    mock_uow,
    mock_user_repo,
    mock_password_service,
    mock_auth_service,
    mock_email_service,
    reg_confirm_url
):
    """Create RegisterUserRequest instance with mocks"""
    return RegisterUserRequest(
        uow=mock_uow,
        user_repo=mock_user_repo,
        password_service=mock_password_service,
        auth_service=mock_auth_service,
        email_service=mock_email_service,
        reg_confirm_url=reg_confirm_url
    )


@pytest.fixture
def register_user_confirm(mock_uow, mock_user_repo, mock_auth_service):
    """Create RegisterUserConfirm instance with mocks"""
    return RegisterUserConfirm(
        uow=mock_uow,
        user_repo=mock_user_repo,
        auth_service=mock_auth_service
    )


@pytest.fixture
def change_password_request(
    mock_uow,
    mock_user_repo,
    mock_token_service,
    mock_email_service,
    password_change_confirm_url
):
    """Create ChangePasswordRequest instance with mocks"""
    return ChangePasswordRequest(
        uow=mock_uow,
        user_repo=mock_user_repo,
        token_service=mock_token_service,
        email_service=mock_email_service,
        password_change_confirm_url=password_change_confirm_url
    )


@pytest.fixture
def change_password_confirm(
    mock_uow,
    mock_user_repo,
    mock_token_service,
    mock_password_service
):
    """Create ChangePasswordConfirm instance with mocks"""
    return ChangePasswordConfirm(
        uow=mock_uow,
        user_repo=mock_user_repo,
        token_service=mock_token_service,
        password_service=mock_password_service
    )
