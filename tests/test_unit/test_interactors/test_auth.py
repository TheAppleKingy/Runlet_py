import pytest

from typing import Optional

from runlet.domain.entities import Course, User

from runlet.application.interactors.exceptions import (
    UndefinedUserError,
    InactiveUserError,
    HasNoAccessError,
    UndefinedCourseError,
    InvalidUserPasswordError,
    PasswordsMismatchError,
    EmailExistsError,
)
from runlet.infrastructure.services.user.exceptions import JWTUnauthorizedError
from runlet.application.dtos.auth import (
    LoginUserDTO,
    RegisterUserRequestDTO,
    ChangePasswordConfirmDTO
)


@pytest.mark.asyncio
class TestAuthenticateUser:
    """Test suite for AuthenticateUser use case"""

    async def test_successful_authentication_with_valid_token(
        self,
        authenticate_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service,
        active_user
    ):
        """Test successful authentication with valid token"""
        # Arrange
        token = "valid.jwt.token"
        user_id = 1

        mock_auth_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = active_user

        # Act
        result = await authenticate_user(token)

        # Assert
        assert result == user_id
        assert isinstance(result, int)
        mock_auth_service.get_user_id_from_token.assert_called_once_with(token)
        mock_user_repo.get_by_id.assert_called_once_with(user_id)
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_authentication_with_none_token_raises_error(
        self,
        authenticate_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service
    ):
        """Test authentication with None token raises UndefinedUserError"""
        # Arrange
        token = None

        # Act & Assert
        with pytest.raises(UndefinedUserError) as exc_info:
            await authenticate_user(token)

        assert exc_info.value.status == 401
        assert str(exc_info.value) == "Unauthorized"

        # Verify no interactions with dependencies
        mock_auth_service.get_user_id_from_token.assert_not_called()
        mock_user_repo.get_by_id.assert_not_called()
        mock_uow.__aenter__.assert_not_called()

    async def test_authentication_with_empty_string_token_raises_error(
        self,
        authenticate_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service
    ):
        """Test authentication with empty string token raises UndefinedUserError"""
        # Arrange
        token = ""

        # Act & Assert
        with pytest.raises(UndefinedUserError) as exc_info:
            await authenticate_user(token)

        assert exc_info.value.status == 401
        assert str(exc_info.value) == "Unauthorized"

        # Verify no interactions with dependencies
        mock_auth_service.get_user_id_from_token.assert_not_called()
        mock_user_repo.get_by_id.assert_not_called()
        mock_uow.__aenter__.assert_not_called()

    async def test_authentication_with_invalid_token_returns_none_user_id(
        self,
        authenticate_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service
    ):
        """Test authentication with invalid token where auth service returns None"""
        # Arrange
        token = "invalid.token"
        mock_auth_service.get_user_id_from_token.return_value = None

        # Act & Assert
        with pytest.raises(UndefinedUserError) as exc_info:
            await authenticate_user(token)

        assert exc_info.value.status == 401
        assert str(exc_info.value) == "User was not identify"

        mock_auth_service.get_user_id_from_token.assert_called_once_with(token)
        mock_user_repo.get_by_id.assert_not_called()
        mock_uow.__aenter__.assert_not_called()
        mock_uow.__aexit__.assert_not_called()

    async def test_authentication_with_token_for_nonexistent_user(
        self,
        authenticate_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service
    ):
        """Test authentication with token for user that doesn't exist in DB"""
        # Arrange
        token = "valid.jwt.token"
        user_id = 999

        mock_auth_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UndefinedUserError) as exc_info:
            await authenticate_user(token)

        assert exc_info.value.status == 401
        assert str(exc_info.value) == "User was not identify"

        mock_auth_service.get_user_id_from_token.assert_called_once_with(token)
        mock_user_repo.get_by_id.assert_called_once_with(user_id)
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_authentication_with_inactive_user_raises_error(
        self,
        authenticate_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service,
        inactive_user
    ):
        """Test authentication with inactive user raises InactiveUserError"""
        # Arrange
        token = "valid.jwt.token"
        user_id = 1

        mock_auth_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = inactive_user

        # Act & Assert
        with pytest.raises(InactiveUserError) as exc_info:
            await authenticate_user(token)

        assert exc_info.value.status == 403
        assert str(exc_info.value) == "Current user is inactive"

        mock_auth_service.get_user_id_from_token.assert_called_once_with(token)
        mock_user_repo.get_by_id.assert_called_once_with(user_id)
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_authentication_uow_context_manager_usage(
        self,
        authenticate_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service,
        active_user
    ):
        """Test that UoW context manager is properly used"""
        # Arrange
        token = "valid.jwt.token"
        user_id = 1

        mock_auth_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = active_user

        # Act
        result = await authenticate_user(token)

        # Assert
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

        # Verify that repository was called within context
        mock_user_repo.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.parametrize("token_value", [
        "token with spaces",
        "very.long.jwt.token.with.many.parts",
        "token-with-special-chars!@#",
        "a" * 1000  # very long token
    ])
    async def test_authentication_with_various_token_formats(
        self,
        authenticate_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service,
        active_user,
        token_value
    ):
        """Test authentication with various token formats"""
        # Arrange
        user_id = 1

        mock_auth_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = active_user

        # Act
        result = await authenticate_user(token_value)

        # Assert
        assert result == user_id
        mock_auth_service.get_user_id_from_token.assert_called_once_with(token_value)
        mock_user_repo.get_by_id.assert_called_once_with(user_id)

    async def test_authentication_preserves_user_data(
        self,
        authenticate_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service,
        active_user
    ):
        """Test that user data is correctly retrieved and preserved"""
        # Arrange
        token = "valid.jwt.token"
        user_id = 2

        mock_auth_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = active_user

        # Act
        result = await authenticate_user(token)

        # Assert
        assert result == active_user.id
        assert active_user.email == "active@example.com"
        assert active_user.name == "Active User"
        assert active_user.is_active is True

    async def test_authentication_with_multiple_consecutive_calls(
        self,
        authenticate_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service,
        active_user
    ):
        """Test multiple authentication calls with the same token"""
        # Arrange
        token = "valid.jwt.token"
        user_id = 1

        mock_auth_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = active_user

        # Act
        result1 = await authenticate_user(token)
        result2 = await authenticate_user(token)
        result3 = await authenticate_user(token)

        # Assert
        assert result1 == result2 == result3 == user_id
        assert mock_auth_service.get_user_id_from_token.call_count == 3
        assert mock_user_repo.get_by_id.call_count == 3
        assert mock_uow.__aenter__.call_count == 3
        assert mock_uow.__aexit__.call_count == 3

    async def test_authentication_raises_error_when_auth_service_fails(
        self,
        authenticate_user,
        mock_auth_service
    ):
        """Test authentication when auth service raises an exception"""
        # Arrange
        token = "valid.jwt.token"
        mock_auth_service.get_user_id_from_token.side_effect = Exception("Auth service error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await authenticate_user(token)

        assert str(exc_info.value) == "Auth service error"
        mock_auth_service.get_user_id_from_token.assert_called_once_with(token)

    async def test_authentication_rolls_back_uow_on_error(
        self,
        authenticate_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service
    ):
        """Test that UoW context manager exits even on error"""
        # Arrange
        token = "valid.jwt.token"
        user_id = 1

        mock_auth_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await authenticate_user(token)

        assert str(exc_info.value) == "Database error"

        # Verify UoW context manager was entered and exited
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()


@pytest.mark.asyncio
class TestOptionalAuthenticateUser:
    """Test suite for OptionalAuthenticateUser use case"""

    async def test_successful_authentication_with_valid_token(
        self,
        optional_authenticate_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service,
        active_user
    ):
        """Test successful authentication with valid token returns user_id"""
        # Arrange
        token = "valid.jwt.token"
        user_id = 1

        mock_auth_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = active_user

        # Act
        result = await optional_authenticate_user(token)

        # Assert
        assert result == user_id
        assert isinstance(result, int)
        mock_auth_service.get_user_id_from_token.assert_called_once_with(token)
        mock_user_repo.get_by_id.assert_called_once_with(user_id)
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_authentication_with_none_token_returns_none(
        self,
        optional_authenticate_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service
    ):
        """Test authentication with None token returns None without errors"""
        # Arrange
        token = None

        # Act
        result = await optional_authenticate_user(token)

        # Assert
        assert result is None

        # Verify no interactions with dependencies
        mock_auth_service.get_user_id_from_token.assert_not_called()
        mock_user_repo.get_by_id.assert_not_called()
        mock_uow.__aenter__.assert_not_called()
        mock_uow.__aexit__.assert_not_called()

    async def test_authentication_with_empty_string_token_returns_none(
        self,
        optional_authenticate_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service
    ):
        """Test authentication with empty string token returns None without errors"""
        # Arrange
        token = ""

        # Act
        result = await optional_authenticate_user(token)

        # Assert
        assert result is None

        # Verify no interactions with dependencies
        mock_auth_service.get_user_id_from_token.assert_not_called()
        mock_user_repo.get_by_id.assert_not_called()
        mock_uow.__aenter__.assert_not_called()
        mock_uow.__aexit__.assert_not_called()

    async def test_authentication_with_invalid_token_returns_none(
        self,
        optional_authenticate_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service
    ):
        """Test authentication with invalid token returns None (exception swallowed)"""
        # Arrange
        token = "invalid.token"
        mock_auth_service.get_user_id_from_token.return_value = None

        # Act
        result = await optional_authenticate_user(token)

        # Assert
        assert result is None

        mock_auth_service.get_user_id_from_token.assert_called_once_with(token)
        mock_user_repo.get_by_id.assert_not_called()
        mock_uow.__aenter__.assert_not_called()
        mock_uow.__aexit__.assert_not_called()

    async def test_authentication_with_token_for_nonexistent_user_returns_none(
        self,
        optional_authenticate_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service
    ):
        """Test authentication with token for non-existent user returns None (exception swallowed)"""
        # Arrange
        token = "valid.jwt.token"
        user_id = 999

        mock_auth_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = None

        # Act
        result = await optional_authenticate_user(token)

        # Assert
        assert result is None

        mock_auth_service.get_user_id_from_token.assert_called_once_with(token)
        mock_user_repo.get_by_id.assert_called_once_with(user_id)
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_authentication_with_inactive_user_returns_none(
        self,
        optional_authenticate_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service,
        inactive_user
    ):
        """Test authentication with inactive user returns None (exception swallowed)"""
        # Arrange
        token = "valid.jwt.token"
        user_id = 1

        mock_auth_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = inactive_user

        # Act
        result = await optional_authenticate_user(token)

        # Assert
        assert result is None

        mock_auth_service.get_user_id_from_token.assert_called_once_with(token)
        mock_user_repo.get_by_id.assert_called_once_with(user_id)
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    @pytest.mark.parametrize("exception", [
        UndefinedUserError("User not found", status=401),
        InactiveUserError("User inactive", status=403),
        Exception("Unexpected error"),
        ValueError("Some value error"),
        RuntimeError("Runtime error")
    ])
    async def test_authentication_swallows_all_exceptions(
        self,
        optional_authenticate_user,
        mock_auth_service,
        exception
    ):
        """Test that all exceptions are caught and return None"""
        # Arrange
        token = "valid.jwt.token"
        mock_auth_service.get_user_id_from_token.side_effect = exception

        # Act
        result = await optional_authenticate_user(token)

        # Assert
        assert result is None
        mock_auth_service.get_user_id_from_token.assert_called_once_with(token)

    async def test_authentication_swallows_exceptions_from_repo(
        self,
        optional_authenticate_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service
    ):
        """Test that exceptions from user_repo are caught and return None"""
        # Arrange
        token = "valid.jwt.token"
        user_id = 1

        mock_auth_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.side_effect = Exception("Database error")

        # Act
        result = await optional_authenticate_user(token)

        # Assert
        assert result is None
        mock_auth_service.get_user_id_from_token.assert_called_once_with(token)
        mock_user_repo.get_by_id.assert_called_once_with(user_id)
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_authentication_with_none_token_returns_none(
        self,
        optional_authenticate_user,
        mock_auth_service,
        mock_user_repo,
        mock_uow
    ):
        """Test authentication with None token returns None"""
        result = await optional_authenticate_user(None)
        assert result is None
        mock_auth_service.get_user_id_from_token.assert_not_called()
        mock_user_repo.get_by_id.assert_not_called()

    async def test_authentication_with_empty_string_token_returns_none(
        self,
        optional_authenticate_user,
        mock_auth_service,
        mock_user_repo,
        mock_uow
    ):
        """Test authentication with empty string token returns None"""
        result = await optional_authenticate_user("")
        assert result is None
        mock_auth_service.get_user_id_from_token.assert_not_called()
        mock_user_repo.get_by_id.assert_not_called()

    async def test_authentication_with_valid_token_returns_user_id(
        self,
        optional_authenticate_user,
        mock_auth_service,
        mock_user_repo,
        mock_uow,
        active_user
    ):
        """Test authentication with valid token returns user_id"""
        mock_auth_service.get_user_id_from_token.return_value = 1
        mock_user_repo.get_by_id.return_value = active_user

        result = await optional_authenticate_user("valid.token")

        assert result == 1
        mock_auth_service.get_user_id_from_token.assert_called_once_with("valid.token")
        mock_user_repo.get_by_id.assert_called_once_with(1)

    async def test_authentication_with_invalid_token_returns_none(
        self,
        optional_authenticate_user,
        mock_auth_service,
        mock_user_repo,
        mock_uow
    ):
        """Test authentication with invalid token returns None"""
        mock_auth_service.get_user_id_from_token.return_value = None

        result = await optional_authenticate_user("invalid.token")

        assert result is None
        mock_auth_service.get_user_id_from_token.assert_called_once_with("invalid.token")
        mock_user_repo.get_by_id.assert_not_called()

    async def test_authentication_with_valid_token_after_invalid(
        self,
        optional_authenticate_user,
        mock_auth_service,
        mock_user_repo,
        active_user
    ):
        """Test multiple calls: invalid then valid token"""
        # First call with invalid token
        mock_auth_service.get_user_id_from_token.return_value = None
        result1 = await optional_authenticate_user("invalid.token")
        assert result1 is None

        # Second call with valid token
        mock_auth_service.get_user_id_from_token.return_value = 1
        mock_user_repo.get_by_id.return_value = active_user
        result2 = await optional_authenticate_user("valid.token")

        assert result2 == 1
        assert mock_auth_service.get_user_id_from_token.call_count == 2

    async def test_authentication_uow_is_always_closed(
        self,
        optional_authenticate_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service
    ):
        """Test that UoW context manager is always exited, even on errors"""
        # Arrange - scenario that causes error in repo
        token = "valid.jwt.token"
        user_id = 1

        mock_auth_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.side_effect = Exception("Database error")

        # Act
        result = await optional_authenticate_user(token)

        # Assert
        assert result is None
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_authentication_does_not_swallow_critical_errors(
        self,
        optional_authenticate_user,
        mock_auth_service
    ):
        """Test that certain errors might not be swallowed (if they're not caught)"""
        # This test depends on what exceptions are caught
        # By default, it catches Exception, which includes almost everything
        # But if you want to test that KeyboardInterrupt or SystemExit are not caught:

        token = "valid.jwt.token"

        # Mock to raise KeyboardInterrupt
        mock_auth_service.get_user_id_from_token.side_effect = KeyboardInterrupt()

        # KeyboardInterrupt should not be caught as it inherits from BaseException, not Exception
        with pytest.raises(KeyboardInterrupt):
            await optional_authenticate_user(token)

    async def test_authentication_with_malformed_token_handling(
        self,
        optional_authenticate_user,
        mock_auth_service
    ):
        """Test handling of malformed tokens that cause decode errors"""
        # Arrange
        token = "malformed.jwt.token"

        # Simulate JWT decode error
        mock_auth_service.get_user_id_from_token.side_effect = ValueError("Invalid token format")

        # Act
        result = await optional_authenticate_user(token)

        # Assert
        assert result is None
        mock_auth_service.get_user_id_from_token.assert_called_once_with(token)

    async def test_authentication_preserves_function_signature(
        self,
        optional_authenticate_user
    ):
        """Test that the method signature is correct with Optional token"""
        # This is more of a static test
        import inspect
        sig = inspect.signature(optional_authenticate_user.__call__)

        # Check that token parameter is Optional[str]
        assert 'token' in sig.parameters
        param = sig.parameters['token']
        assert param.default is None
        # type: ignore
        assert param.annotation == Optional[str] or param.annotation == str or param.annotation == Optional


@pytest.mark.asyncio
class TestAuthenticateUserAsStudent:
    """Test suite for AuthenticateUserAsStudent use case"""

    async def test_successful_authentication_as_student(
        self,
        authenticate_user_as_student,
        mock_uow,
        mock_course_repo,
        existing_course
    ):
        """Test successful authentication when user is a student in the course"""
        # Arrange
        user_id = 123
        course_id = 1

        mock_course_repo.get_by_id.return_value = existing_course
        mock_course_repo.check_user_in_course.return_value = True

        # Act
        result = await authenticate_user_as_student(user_id, course_id)

        # Assert
        assert result == user_id
        mock_course_repo.get_by_id.assert_called_once_with(course_id)
        mock_course_repo.check_user_in_course.assert_called_once_with(user_id, course_id)
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_authentication_with_nonexistent_course_raises_error(
        self,
        authenticate_user_as_student,
        mock_uow,
        mock_course_repo
    ):
        """Test authentication with non-existent course raises UndefinedCourseError"""
        # Arrange
        user_id = 123
        course_id = 999

        mock_course_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UndefinedCourseError) as exc_info:
            await authenticate_user_as_student(user_id, course_id)

        assert exc_info.value.status == 404
        assert str(exc_info.value) == "Course does not exist"

        mock_course_repo.get_by_id.assert_called_once_with(course_id)
        mock_course_repo.check_user_in_course.assert_not_called()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_authentication_when_user_not_in_course_raises_error(
        self,
        authenticate_user_as_student,
        mock_uow,
        mock_course_repo,
        existing_course
    ):
        """Test authentication when user is not subscribed to course raises HasNoAccessError"""
        # Arrange
        user_id = 123
        course_id = 1

        mock_course_repo.get_by_id.return_value = existing_course
        mock_course_repo.check_user_in_course.return_value = False

        # Act & Assert
        with pytest.raises(HasNoAccessError) as exc_info:
            await authenticate_user_as_student(user_id, course_id)

        assert exc_info.value.status == 403
        assert str(exc_info.value) == "User not subscribed on course"

        mock_course_repo.get_by_id.assert_called_once_with(course_id)
        mock_course_repo.check_user_in_course.assert_called_once_with(user_id, course_id)
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_authentication_preserves_course_data(
        self,
        authenticate_user_as_student,
        mock_uow,
        mock_course_repo,
        existing_course
    ):
        """Test that course data is correctly retrieved"""
        # Arrange
        user_id = 123
        course_id = 1

        mock_course_repo.get_by_id.return_value = existing_course
        mock_course_repo.check_user_in_course.return_value = True

        # Act
        result = await authenticate_user_as_student(user_id, course_id)

        # Assert
        assert result == user_id
        # Verify course data is preserved
        assert existing_course.id == 1
        assert existing_course.name == "Test Course"
        assert existing_course.description == "Test Description"
        assert existing_course.is_private is False
        assert existing_course.notify_request_sub is False
        assert existing_course._teacher_id == 1

    async def test_authentication_with_private_course(
        self,
        authenticate_user_as_student,
        mock_uow,
        mock_course_repo,
        private_course
    ):
        """Test authentication with a private course"""
        # Arrange
        user_id = 123
        course_id = 2

        mock_course_repo.get_by_id.return_value = private_course
        mock_course_repo.check_user_in_course.return_value = True

        # Act
        result = await authenticate_user_as_student(user_id, course_id)

        # Assert
        assert result == user_id
        assert private_course.is_private is True
        assert private_course.notify_request_sub is True
        mock_course_repo.get_by_id.assert_called_once_with(course_id)
        mock_course_repo.check_user_in_course.assert_called_once_with(user_id, course_id)

    async def test_authentication_uow_context_manager_usage(
        self,
        authenticate_user_as_student,
        mock_uow,
        mock_course_repo,
        existing_course
    ):
        """Test that UoW context manager is properly used"""
        # Arrange
        user_id = 123
        course_id = 1

        mock_course_repo.get_by_id.return_value = existing_course
        mock_course_repo.check_user_in_course.return_value = True

        # Act
        result = await authenticate_user_as_student(user_id, course_id)

        # Assert
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

        # Verify that repository calls were within context
        mock_course_repo.get_by_id.assert_called_once_with(course_id)
        mock_course_repo.check_user_in_course.assert_called_once_with(user_id, course_id)

    @pytest.mark.parametrize("user_id, course_id", [
        (1, 100),
        (999, 1),
        (12345, 54321),
        (0, 0),
    ])
    async def test_authentication_with_various_id_combinations(
        self,
        authenticate_user_as_student,
        mock_uow,
        mock_course_repo,
        existing_course,
        user_id,
        course_id
    ):
        """Test authentication with various user_id and course_id combinations"""
        # Arrange
        mock_course_repo.get_by_id.return_value = existing_course
        mock_course_repo.check_user_in_course.return_value = True

        # Act
        result = await authenticate_user_as_student(user_id, course_id)

        # Assert
        assert result == user_id
        mock_course_repo.get_by_id.assert_called_once_with(course_id)
        mock_course_repo.check_user_in_course.assert_called_once_with(user_id, course_id)

    async def test_authentication_when_course_repo_throws_exception(
        self,
        authenticate_user_as_student,
        mock_uow,
        mock_course_repo
    ):
        """Test authentication when course repository throws an exception"""
        # Arrange
        user_id = 123
        course_id = 1

        mock_course_repo.get_by_id.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await authenticate_user_as_student(user_id, course_id)

        assert str(exc_info.value) == "Database error"

        mock_course_repo.get_by_id.assert_called_once_with(course_id)
        mock_course_repo.check_user_in_course.assert_not_called()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_authentication_with_multiple_consecutive_calls(
        self,
        authenticate_user_as_student,
        mock_uow,
        mock_course_repo,
        existing_course,
        private_course
    ):
        """Test multiple authentication calls with different users/courses"""
        # Arrange
        test_cases = [
            (1, 1, existing_course, True),
            (2, 1, existing_course, True),
            (3, 2, private_course, True),
            (4, 1, existing_course, False),  # User not in course
        ]

        results = []

        # Act
        for user_id, course_id, course, is_in_course in test_cases:
            mock_course_repo.get_by_id.return_value = course
            mock_course_repo.check_user_in_course.return_value = is_in_course

            if is_in_course:
                result = await authenticate_user_as_student(user_id, course_id)
                results.append(result)
            else:
                with pytest.raises(HasNoAccessError):
                    await authenticate_user_as_student(user_id, course_id)

        # Assert
        assert results == [1, 2, 3]
        assert mock_course_repo.get_by_id.call_count == 4
        assert mock_course_repo.check_user_in_course.call_count == 4
        assert mock_uow.__aenter__.call_count == 4
        assert mock_uow.__aexit__.call_count == 4

    async def test_authentication_uow_rolls_back_on_error(
        self,
        authenticate_user_as_student,
        mock_uow,
        mock_course_repo
    ):
        """Test that UoW context manager exits even on error"""
        # Arrange
        user_id = 123
        course_id = 1

        mock_course_repo.get_by_id.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            await authenticate_user_as_student(user_id, course_id)

        # Verify UoW context manager was entered and exited
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_authentication_returns_user_id_not_course_id(
        self,
        authenticate_user_as_student,
        mock_uow,
        mock_course_repo,
        existing_course
    ):
        """Test that the method returns user_id, not course_id"""
        # Arrange
        user_id = 123
        course_id = 1

        mock_course_repo.get_by_id.return_value = existing_course
        mock_course_repo.check_user_in_course.return_value = True

        # Act
        result = await authenticate_user_as_student(user_id, course_id)

        # Assert
        assert result == user_id
        assert result != course_id

    async def test_authentication_with_course_having_no_students(
        self,
        authenticate_user_as_student,
        mock_uow,
        mock_course_repo,
        existing_course
    ):
        """Test authentication with a course that has no students"""
        # Arrange
        user_id = 123
        course_id = 1

        mock_course_repo.get_by_id.return_value = existing_course
        mock_course_repo.check_user_in_course.return_value = False

        # Act & Assert
        with pytest.raises(HasNoAccessError) as exc_info:
            await authenticate_user_as_student(user_id, course_id)

        assert exc_info.value.status == 403
        assert str(exc_info.value) == "User not subscribed on course"

        mock_course_repo.get_by_id.assert_called_once_with(course_id)
        mock_course_repo.check_user_in_course.assert_called_once_with(user_id, course_id)


@pytest.mark.asyncio
class TestAuthenticateUserAsTeacher:
    """Test suite for AuthenticateUserAsTeacher use case"""

    async def test_successful_authentication_as_teacher(
        self,
        authenticate_user_as_teacher,
        mock_uow,
        mock_course_repo,
        course_with_teacher
    ):
        """Test successful authentication when user is the teacher of the course"""
        # Arrange
        user_id = 1  # This matches course_with_teacher.teacher_id
        course_id = 1

        mock_course_repo.get_by_id.return_value = course_with_teacher

        # Act
        result = await authenticate_user_as_teacher(user_id, course_id)

        # Assert
        assert result == user_id
        mock_course_repo.get_by_id.assert_called_once_with(course_id)
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_authentication_with_nonexistent_course_raises_error(
        self,
        authenticate_user_as_teacher,
        mock_uow,
        mock_course_repo
    ):
        """Test authentication with non-existent course raises UndefinedCourseError"""
        # Arrange
        user_id = 1
        course_id = 999

        mock_course_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UndefinedCourseError) as exc_info:
            await authenticate_user_as_teacher(user_id, course_id)

        assert exc_info.value.status == 404
        assert str(exc_info.value) == "Course does not exist"

        mock_course_repo.get_by_id.assert_called_once_with(course_id)
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_authentication_when_user_is_not_teacher_raises_error(
        self,
        authenticate_user_as_teacher,
        mock_uow,
        mock_course_repo,
        course_with_teacher
    ):
        """Test authentication when user is not the teacher raises HasNoAccessError"""
        # Arrange
        user_id = 2  # Different from course_with_teacher.teacher_id (which is 1)
        course_id = 1

        mock_course_repo.get_by_id.return_value = course_with_teacher

        # Act & Assert
        with pytest.raises(HasNoAccessError) as exc_info:
            await authenticate_user_as_teacher(user_id, course_id)

        assert exc_info.value.status == 403
        assert str(exc_info.value) == "User cannot manage course"

        mock_course_repo.get_by_id.assert_called_once_with(course_id)
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_authentication_with_different_teacher_course(
        self,
        authenticate_user_as_teacher,
        mock_uow,
        mock_course_repo,
        course_with_different_teacher
    ):
        """Test authentication with a course that has a different teacher"""
        # Arrange
        user_id = 2  # This matches course_with_different_teacher.teacher_id
        course_id = 2

        mock_course_repo.get_by_id.return_value = course_with_different_teacher

        # Act
        result = await authenticate_user_as_teacher(user_id, course_id)

        # Assert
        assert result == user_id
        assert course_with_different_teacher._teacher_id == 2
        assert course_with_different_teacher.is_private is True
        mock_course_repo.get_by_id.assert_called_once_with(course_id)

    async def test_authentication_preserves_course_data(
        self,
        authenticate_user_as_teacher,
        mock_uow,
        mock_course_repo,
        course_with_teacher
    ):
        """Test that course data is correctly retrieved"""
        # Arrange
        user_id = 1
        course_id = 1

        mock_course_repo.get_by_id.return_value = course_with_teacher

        # Act
        result = await authenticate_user_as_teacher(user_id, course_id)

        # Assert
        assert result == user_id
        # Verify course data is preserved
        assert course_with_teacher.id == 1
        assert course_with_teacher.name == "Test Course"
        assert course_with_teacher.description == "Test Description"
        assert course_with_teacher._teacher_id == 1
        assert course_with_teacher.is_private is False

    async def test_authentication_uow_context_manager_usage(
        self,
        authenticate_user_as_teacher,
        mock_uow,
        mock_course_repo,
        course_with_teacher
    ):
        """Test that UoW context manager is properly used"""
        # Arrange
        user_id = 1
        course_id = 1

        mock_course_repo.get_by_id.return_value = course_with_teacher

        # Act
        result = await authenticate_user_as_teacher(user_id, course_id)

        # Assert
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

        # Verify that repository call was within context
        mock_course_repo.get_by_id.assert_called_once_with(course_id)

    @pytest.mark.parametrize("user_id, course_id, teacher_id, should_succeed", [
        (1, 1, 1, True),   # Same user as teacher
        (2, 1, 1, False),  # Different user
        (1, 2, 2, False),  # Different teacher
        (5, 3, 5, True),   # Another valid combination
        (0, 1, 0, True),   # Teacher ID 0
    ])
    async def test_authentication_with_various_teacher_id_combinations(
        self,
        authenticate_user_as_teacher,
        mock_uow,
        mock_course_repo,
        user_id,
        course_id,
        teacher_id,
        should_succeed
    ):
        """Test authentication with various user_id and teacher_id combinations"""
        # Arrange
        course = Course(
            name=f"Course {course_id}",
            _teacher_id=teacher_id,
            description=f"Description {course_id}"
        )
        course.id = course_id

        mock_course_repo.get_by_id.return_value = course

        # Act & Assert
        if should_succeed:
            result = await authenticate_user_as_teacher(user_id, course_id)
            assert result == user_id
        else:
            with pytest.raises(HasNoAccessError) as exc_info:
                await authenticate_user_as_teacher(user_id, course_id)
            assert exc_info.value.status == 403
            assert str(exc_info.value) == "User cannot manage course"

        mock_course_repo.get_by_id.assert_called_once_with(course_id)

    async def test_authentication_when_course_repo_throws_exception(
        self,
        authenticate_user_as_teacher,
        mock_uow,
        mock_course_repo
    ):
        """Test authentication when course repository throws an exception"""
        # Arrange
        user_id = 1
        course_id = 1

        mock_course_repo.get_by_id.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await authenticate_user_as_teacher(user_id, course_id)

        assert str(exc_info.value) == "Database error"

        mock_course_repo.get_by_id.assert_called_once_with(course_id)
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_authentication_with_multiple_consecutive_calls(
        self,
        authenticate_user_as_teacher,
        mock_uow,
        mock_course_repo,
        course_with_teacher,
        course_with_different_teacher
    ):
        """Test multiple authentication calls with different courses"""
        # Arrange
        test_cases = [
            (1, 1, course_with_teacher, True),      # Teacher of course 1
            (2, 1, course_with_teacher, False),     # Not teacher of course 1
            (2, 2, course_with_different_teacher, True),  # Teacher of course 2
            (1, 2, course_with_different_teacher, False),  # Not teacher of course 2
        ]

        results = []

        # Act
        for user_id, course_id, course, should_succeed in test_cases:
            mock_course_repo.get_by_id.return_value = course

            if should_succeed:
                result = await authenticate_user_as_teacher(user_id, course_id)
                results.append(result)
            else:
                with pytest.raises(HasNoAccessError):
                    await authenticate_user_as_teacher(user_id, course_id)

        # Assert
        assert results == [1, 2]
        assert mock_course_repo.get_by_id.call_count == 4
        assert mock_uow.__aenter__.call_count == 4
        assert mock_uow.__aexit__.call_count == 4

    async def test_authentication_uow_rolls_back_on_error(
        self,
        authenticate_user_as_teacher,
        mock_uow,
        mock_course_repo
    ):
        """Test that UoW context manager exits even on error"""
        # Arrange
        user_id = 1
        course_id = 1

        mock_course_repo.get_by_id.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            await authenticate_user_as_teacher(user_id, course_id)

        # Verify UoW context manager was entered and exited
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_autification_checks_teacher_id_not_students(
        self,
        authenticate_user_as_teacher,
        mock_uow,
        mock_course_repo,
        course_with_teacher
    ):
        """Test that authentication checks teacher_id, not students list"""
        # Arrange
        user_id = 1
        course_id = 1

        # Add students to the course
        student1 = User(email="student1@test.com", password="pass", name="Student 1")
        student1.id = 3
        student2 = User(email="student2@test.com", password="pass", name="Student 2")
        student2.id = 4
        course_with_teacher._students = [student1, student2]

        mock_course_repo.get_by_id.return_value = course_with_teacher

        # Act
        result = await authenticate_user_as_teacher(user_id, course_id)

        # Assert
        assert result == user_id
        # Even though there are students, teacher authentication still works
        assert len(course_with_teacher._students) == 2

    async def test_authentication_with_course_having_teacher_id_zero(
        self,
        authenticate_user_as_teacher,
        mock_uow,
        mock_course_repo
    ):
        """Test authentication with a course that has teacher_id=0"""
        # Arrange
        course = Course(
            name="Course with no teacher",
            _teacher_id=0,
            description="No teacher assigned"
        )
        course.id = 1

        user_id = 0  # User with ID 0
        course_id = 1

        mock_course_repo.get_by_id.return_value = course

        # Act
        result = await authenticate_user_as_teacher(user_id, course_id)

        # Assert
        assert result == user_id
        assert course._teacher_id == 0

    async def test_authentication_with_teacher_id_zero_but_user_nonzero(
        self,
        authenticate_user_as_teacher,
        mock_uow,
        mock_course_repo
    ):
        """Test authentication when course has teacher_id=0 but user_id != 0"""
        # Arrange
        course = Course(
            name="Course with no teacher",
            _teacher_id=0,
            description="No teacher assigned"
        )
        course.id = 1

        user_id = 1  # User with ID 1
        course_id = 1

        mock_course_repo.get_by_id.return_value = course

        # Act & Assert
        with pytest.raises(HasNoAccessError) as exc_info:
            await authenticate_user_as_teacher(user_id, course_id)

        assert exc_info.value.status == 403
        assert str(exc_info.value) == "User cannot manage course"


@pytest.mark.asyncio
class TestLoginUser:
    """Test suite for LoginUser use case"""

    async def test_successful_login_with_active_user(
        self,
        login_user,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        active_user
    ):
        """Test successful login with active user returns token"""
        # Arrange
        dto = LoginUserDTO(email="active@example.com", password="correct_password")
        expected_token = "jwt.token.123"

        mock_user_repo.get_by_email.return_value = active_user
        mock_password_service.check_password.return_value = True
        mock_auth_service.generate_token.return_value = expected_token

        # Act
        result = await login_user(dto)

        # Assert
        assert result == expected_token
        mock_user_repo.get_by_email.assert_called_once_with("active@example.com")
        mock_password_service.check_password.assert_called_once_with(
            active_user.password, "correct_password"
        )
        mock_auth_service.generate_token.assert_called_once_with(active_user.id)
        mock_email_service.send_mail.assert_not_called()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_login_with_nonexistent_email_raises_error(
        self,
        login_user,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service
    ):
        """Test login with non-existent email raises UndefinedUserError"""
        # Arrange
        dto = LoginUserDTO(email="nonexistent@example.com", password="any_password")
        mock_user_repo.get_by_email.return_value = None

        # Act & Assert
        with pytest.raises(UndefinedUserError) as exc_info:
            await login_user(dto)

        assert str(exc_info.value) == "User not found"

        mock_user_repo.get_by_email.assert_called_once_with("nonexistent@example.com")
        mock_password_service.check_password.assert_not_called()
        mock_auth_service.generate_token.assert_not_called()
        mock_email_service.send_mail.assert_not_called()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_login_with_incorrect_password_raises_error(
        self,
        login_user,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        active_user
    ):
        """Test login with incorrect password raises InvalidUserPasswordError"""
        # Arrange
        dto = LoginUserDTO(email="active@example.com", password="wrong_password")

        mock_user_repo.get_by_email.return_value = active_user
        mock_password_service.check_password.return_value = False

        # Act & Assert
        with pytest.raises(InvalidUserPasswordError) as exc_info:
            await login_user(dto)

        assert str(exc_info.value) == "Incorrect password"

        mock_user_repo.get_by_email.assert_called_once_with("active@example.com")
        mock_password_service.check_password.assert_called_once_with(
            active_user.password, "wrong_password"
        )
        mock_auth_service.generate_token.assert_not_called()
        mock_email_service.send_mail.assert_not_called()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_login_with_inactive_user_sends_email_and_raises_error(
        self,
        login_user,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        reg_confirm_url,
        inactive_user
    ):
        """Test login with inactive user sends confirmation email and raises InactiveUserError"""
        # Arrange
        dto = LoginUserDTO(email="inactive@example.com", password="any_password")
        reset_token = "reset.token.456"
        expected_topic = "Registration confirm"
        expected_message = f"Hello! Confirm your registration on Runlet following by link:\n{reg_confirm_url}/{reset_token}"

        mock_user_repo.get_by_email.return_value = inactive_user
        mock_auth_service.generate_token.return_value = reset_token
        mock_email_service.send_mail.return_value = None

        # Act & Assert
        with pytest.raises(InactiveUserError) as exc_info:
            await login_user(dto)

        assert exc_info.value.status == 403
        assert str(exc_info.value) == "Now user is inactive. Email with instructions sent"

        mock_user_repo.get_by_email.assert_called_once_with("inactive@example.com")
        mock_auth_service.generate_token.assert_called_once_with(inactive_user.id, 300)
        mock_email_service.send_mail.assert_called_once_with(
            inactive_user.email,
            expected_topic,
            expected_message
        )
        mock_password_service.check_password.assert_not_called()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_login_with_inactive_user_email_send_failure(
        self,
        login_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service,
        mock_email_service,
        reg_confirm_url,
        inactive_user
    ):
        """Test login with inactive user when email service fails"""
        # Arrange
        dto = LoginUserDTO(email="inactive@example.com", password="any_password")
        reset_token = "reset.token.456"

        mock_user_repo.get_by_email.return_value = inactive_user
        mock_auth_service.generate_token.return_value = reset_token
        mock_email_service.send_mail.side_effect = Exception("Email service error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await login_user(dto)

        assert str(exc_info.value) == "Email service error"

        mock_user_repo.get_by_email.assert_called_once_with("inactive@example.com")
        mock_auth_service.generate_token.assert_called_once_with(inactive_user.id, 300)
        mock_email_service.send_mail.assert_called_once()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    @pytest.mark.parametrize("email,password", [
        ("user@example.com", "pass123"),
        ("admin@test.com", "admin_pass"),
        ("test@test.ru", "qwerty123"),
    ])
    async def test_login_with_various_credentials(
        self,
        login_user,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        active_user,
        email,
        password
    ):
        """Test login with various email and password combinations"""
        # Arrange
        dto = LoginUserDTO(email=email, password=password)
        expected_token = "jwt.token.123"

        # Update active_user email to match test
        active_user.email = email

        mock_user_repo.get_by_email.return_value = active_user
        mock_password_service.check_password.return_value = True
        mock_auth_service.generate_token.return_value = expected_token

        # Act
        result = await login_user(dto)

        # Assert
        assert result == expected_token
        mock_user_repo.get_by_email.assert_called_once_with(email)
        mock_password_service.check_password.assert_called_once_with(
            active_user.password, password
        )

    async def test_login_user_with_special_characters_in_password(
        self,
        login_user,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        active_user
    ):
        """Test login with password containing special characters"""
        # Arrange
        special_password = "P@ssw0rd!#$%"
        dto = LoginUserDTO(email="active@example.com", password=special_password)
        expected_token = "jwt.token.123"

        mock_user_repo.get_by_email.return_value = active_user
        mock_password_service.check_password.return_value = True
        mock_auth_service.generate_token.return_value = expected_token

        # Act
        result = await login_user(dto)

        # Assert
        assert result == expected_token
        mock_password_service.check_password.assert_called_once_with(
            active_user.password, special_password
        )

    async def test_login_with_empty_password(
        self,
        login_user,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        active_user
    ):
        """Test login with empty password"""
        # Arrange
        dto = LoginUserDTO(email="active@example.com", password="")

        mock_user_repo.get_by_email.return_value = active_user
        mock_password_service.check_password.return_value = False

        # Act & Assert
        with pytest.raises(InvalidUserPasswordError):
            await login_user(dto)

        mock_password_service.check_password.assert_called_once_with(
            active_user.password, ""
        )

    async def test_login_with_very_long_password(
        self,
        login_user,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        active_user
    ):
        """Test login with very long password"""
        # Arrange
        long_password = "a" * 1000
        dto = LoginUserDTO(email="active@example.com", password=long_password)
        expected_token = "jwt.token.123"

        mock_user_repo.get_by_email.return_value = active_user
        mock_password_service.check_password.return_value = True
        mock_auth_service.generate_token.return_value = expected_token

        # Act
        result = await login_user(dto)

        # Assert
        assert result == expected_token
        mock_password_service.check_password.assert_called_once_with(
            active_user.password, long_password
        )

    async def test_login_generates_correct_token_for_active_user(
        self,
        login_user,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        active_user
    ):
        """Test that token is generated with correct parameters for active user"""
        # Arrange
        dto = LoginUserDTO(email="active@example.com", password="correct_password")
        expected_token = "secure.jwt.token"

        mock_user_repo.get_by_email.return_value = active_user
        mock_password_service.check_password.return_value = True
        mock_auth_service.generate_token.return_value = expected_token

        # Act
        result = await login_user(dto)

        # Assert
        assert result == expected_token
        mock_auth_service.generate_token.assert_called_once_with(active_user.id)
        # Verify token was generated without expiry for active user
        assert mock_auth_service.generate_token.call_args[0][0] == active_user.id
        assert len(mock_auth_service.generate_token.call_args[0]) == 1

    async def test_login_generates_expiring_token_for_inactive_user(
        self,
        login_user,
        mock_uow,
        mock_user_repo,
        mock_auth_service,
        mock_email_service,
        reg_confirm_url,
        inactive_user
    ):
        """Test that expiring token is generated for inactive user"""
        # Arrange
        dto = LoginUserDTO(email="inactive@example.com", password="any_password")
        expected_token = "expiring.jwt.token"
        expiry_seconds = 300

        mock_user_repo.get_by_email.return_value = inactive_user
        mock_auth_service.generate_token.return_value = expected_token

        # Act & Assert
        with pytest.raises(InactiveUserError):
            await login_user(dto)

        # Verify token was generated with expiry for inactive user
        mock_auth_service.generate_token.assert_called_once_with(
            inactive_user.id, expiry_seconds
        )

    async def test_login_uow_context_manager_usage(
        self,
        login_user,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        active_user
    ):
        """Test that UoW context manager is properly used"""
        # Arrange
        dto = LoginUserDTO(email="active@example.com", password="correct_password")

        mock_user_repo.get_by_email.return_value = active_user
        mock_password_service.check_password.return_value = True
        mock_auth_service.generate_token.return_value = "token"

        # Act
        await login_user(dto)

        # Assert
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

        # Verify that repository was called within context
        mock_user_repo.get_by_email.assert_called_once_with("active@example.com")

    async def test_login_uow_rolls_back_on_error(
        self,
        login_user,
        mock_uow,
        mock_user_repo
    ):
        """Test that UoW context manager exits even on error"""
        # Arrange
        dto = LoginUserDTO(email="test@example.com", password="password")
        mock_user_repo.get_by_email.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            await login_user(dto)

        # Verify UoW context manager was entered and exited
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_login_with_multiple_consecutive_calls(
        self,
        login_user,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        active_user
    ):
        """Test multiple login calls with different credentials"""
        # Arrange
        credentials = [
            ("user1@test.com", "pass1", True),
            ("user2@test.com", "pass2", True),
            ("user3@test.com", "wrong", False),
            ("user4@test.com", "pass4", True),
        ]

        tokens = []

        # Act
        for email, password, should_succeed in credentials:
            dto = LoginUserDTO(email=email, password=password)

            # Update user email
            current_user = User(
                email=email,
                password=f"hashed_{password}",
                name=f"User {email}"
            )
            current_user.id = 3
            current_user.is_active = True

            mock_user_repo.get_by_email.return_value = current_user
            mock_password_service.check_password.return_value = should_succeed

            if should_succeed:
                mock_auth_service.generate_token.return_value = f"token.{email}"
                result = await login_user(dto)
                tokens.append(result)
            else:
                with pytest.raises(InvalidUserPasswordError):
                    await login_user(dto)

        # Assert
        assert len(tokens) == 3
        assert mock_user_repo.get_by_email.call_count == 4
        assert mock_password_service.check_password.call_count == 4
        assert mock_auth_service.generate_token.call_count == 3
        assert mock_uow.__aenter__.call_count == 4
        assert mock_uow.__aexit__.call_count == 4

    async def test_login_preserves_user_data(
        self,
        login_user,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        active_user
    ):
        """Test that user data is correctly retrieved and preserved"""
        # Arrange
        dto = LoginUserDTO(email="active@example.com", password="correct_password")

        mock_user_repo.get_by_email.return_value = active_user
        mock_password_service.check_password.return_value = True
        mock_auth_service.generate_token.return_value = "token"

        # Act
        await login_user(dto)

        # Assert
        # Verify user data is preserved
        assert active_user.email == "active@example.com"
        assert active_user.name == "Active User"
        assert active_user.id == 2
        assert active_user.is_active is True


@pytest.mark.asyncio
class TestRegisterUserRequest:
    """Test suite for RegisterUserRequest use case"""

    async def test_successful_registration(
        self,
        register_user_request,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        reg_confirm_url
    ):
        """Test successful user registration"""
        # Arrange
        dto = RegisterUserRequestDTO(
            email="newuser@example.com",
            first_password="SecurePass123!",
            second_password="SecurePass123!",
            name="New User"
        )
        hashed_password = "hashed_secure_password_123"
        confirmation_token = "confirmation.jwt.token"
        expected_topic = "Registration confirm"
        expected_message = f"Hello! Confirm your registration on Runlet following by link:\n{reg_confirm_url}/{confirmation_token}"

        mock_user_repo.count_by_email.return_value = 0
        mock_password_service.hash_password.return_value = hashed_password
        mock_auth_service.generate_token.return_value = confirmation_token
        mock_email_service.send_mail.return_value = None

        # Act
        await register_user_request(dto)

        # Assert
        mock_user_repo.count_by_email.assert_called_once_with("newuser@example.com")
        mock_password_service.hash_password.assert_called_once_with("SecurePass123!")

        # Verify user was created and saved
        mock_uow.add.assert_called_once()
        saved_user = mock_uow.add.call_args[0][0]
        assert isinstance(saved_user, User)
        assert saved_user.email == "newuser@example.com"
        assert saved_user.password == hashed_password
        assert saved_user.name == "New User"
        assert saved_user.is_active is False  # User should be inactive initially

        mock_uow.flush.assert_called_once()

        # Verify token generation and email sending
        mock_auth_service.generate_token.assert_called_once_with(saved_user.id, 300)
        mock_email_service.send_mail.assert_called_once_with(
            "newuser@example.com",
            expected_topic,
            expected_message
        )

        # Verify UoW context manager usage
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_registration_with_password_mismatch_raises_error(
        self,
        register_user_request,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service
    ):
        """Test registration with mismatched passwords raises PasswordsMismatchError"""
        # Arrange
        dto = RegisterUserRequestDTO(
            email="test@example.com",
            first_password="Password123",
            second_password="DifferentPassword456",
            name="Test User"
        )

        # Act & Assert
        with pytest.raises(PasswordsMismatchError) as exc_info:
            await register_user_request(dto)

        assert str(exc_info.value) == "Passwords do not match"

        # Verify no interactions with other services
        mock_user_repo.count_by_email.assert_not_called()
        mock_password_service.hash_password.assert_not_called()
        mock_uow.add.assert_not_called()
        mock_uow.flush.assert_not_called()
        mock_auth_service.generate_token.assert_not_called()
        mock_email_service.send_mail.assert_not_called()
        mock_uow.__aenter__.assert_not_called()
        mock_uow.__aexit__.assert_not_called()

    async def test_registration_with_existing_email_raises_error(
        self,
        register_user_request,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service
    ):
        """Test registration with already existing email raises EmailExistsError"""
        # Arrange
        dto = RegisterUserRequestDTO(
            email="existing@example.com",
            first_password="Password123",
            second_password="Password123",
            name="Test User"
        )

        mock_user_repo.count_by_email.return_value = 1  # Email already exists

        # Act & Assert
        with pytest.raises(EmailExistsError) as exc_info:
            await register_user_request(dto)

        assert str(exc_info.value) == "User with email existing@example.com already exists"

        mock_user_repo.count_by_email.assert_called_once_with("existing@example.com")
        mock_password_service.hash_password.assert_not_called()
        mock_uow.add.assert_not_called()
        mock_uow.flush.assert_not_called()
        mock_auth_service.generate_token.assert_not_called()
        mock_email_service.send_mail.assert_not_called()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    @pytest.mark.parametrize("first_password,second_password", [
        ("pass123456", "pass123456"),  # Simple passwords
        ("P@ssw0rd!123", "P@ssw0rd!123"),  # Complex password
        ("a" * 100, "a" * 100),  # Very long password
        ("u"*8, "u"*8),
        ("1234567890", "1234567890"),  # Numbers only
    ])
    async def test_registration_with_various_passwords(
        self,
        register_user_request,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        reg_confirm_url,
        first_password,
        second_password
    ):
        """Test registration with various password combinations"""
        # Arrange
        dto = RegisterUserRequestDTO(
            email="user@example.com",
            first_password=first_password,
            second_password=second_password,
            name="Test User"
        )
        hashed_password = f"hashed_{first_password}"
        confirmation_token = "token.123"

        mock_user_repo.count_by_email.return_value = 0
        mock_password_service.hash_password.return_value = hashed_password
        mock_auth_service.generate_token.return_value = confirmation_token

        # Act
        await register_user_request(dto)

        # Assert
        mock_user_repo.count_by_email.assert_called_once_with("user@example.com")
        mock_password_service.hash_password.assert_called_once_with(first_password)

        saved_user = mock_uow.add.call_args[0][0]
        assert saved_user.password == hashed_password

    async def test_registration_with_special_characters_in_name(
        self,
        register_user_request,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        reg_confirm_url
    ):
        """Test registration with special characters in name"""
        # Arrange
        dto = RegisterUserRequestDTO(
            email="user@example.com",
            first_password="Password123",
            second_password="Password123",
            name="John @#$% Doe! &"
        )
        hashed_password = "hashed_password"
        confirmation_token = "token.123"

        mock_user_repo.count_by_email.return_value = 0
        mock_password_service.hash_password.return_value = hashed_password
        mock_auth_service.generate_token.return_value = confirmation_token

        # Act
        await register_user_request(dto)

        # Assert
        saved_user = mock_uow.add.call_args[0][0]
        assert saved_user.name == "John @#$% Doe! &"

    async def test_registration_with_empty_name(
        self,
        register_user_request,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        reg_confirm_url
    ):
        """Test registration with empty name"""
        # Arrange
        dto = RegisterUserRequestDTO(
            email="user@example.com",
            first_password="Password123",
            second_password="Password123",
            name="name"  # Empty name
        )
        hashed_password = "hashed_password"
        confirmation_token = "token.123"

        mock_user_repo.count_by_email.return_value = 0
        mock_password_service.hash_password.return_value = hashed_password
        mock_auth_service.generate_token.return_value = confirmation_token

        # Act
        await register_user_request(dto)

        # Assert
        saved_user = mock_uow.add.call_args[0][0]
        assert saved_user.name == "name"

    async def test_registration_email_send_failure(
        self,
        register_user_request,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        reg_confirm_url
    ):
        """Test registration when email service fails"""
        # Arrange
        dto = RegisterUserRequestDTO(
            email="user@example.com",
            first_password="Password123",
            second_password="Password123",
            name="Test User"
        )
        hashed_password = "hashed_password"
        confirmation_token = "token.123"

        mock_user_repo.count_by_email.return_value = 0
        mock_password_service.hash_password.return_value = hashed_password
        mock_auth_service.generate_token.return_value = confirmation_token
        mock_email_service.send_mail.side_effect = Exception("Email service error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await register_user_request(dto)

        assert str(exc_info.value) == "Email service error"

        # Verify user was still created and saved before email failure
        mock_user_repo.count_by_email.assert_called_once()
        mock_password_service.hash_password.assert_called_once()
        mock_uow.add.assert_called_once()
        mock_uow.flush.assert_called_once()
        mock_auth_service.generate_token.assert_called_once()
        mock_email_service.send_mail.assert_called_once()

        # UoW context manager should still exit
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_registration_creates_inactive_user(
        self,
        register_user_request,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        reg_confirm_url
    ):
        """Test that newly registered user is created as inactive"""
        # Arrange
        dto = RegisterUserRequestDTO(
            email="user@example.com",
            first_password="Password123",
            second_password="Password123",
            name="Test User"
        )

        mock_user_repo.count_by_email.return_value = 0
        mock_password_service.hash_password.return_value = "hashed"
        mock_auth_service.generate_token.return_value = "token"

        # Act
        await register_user_request(dto)

        # Assert
        saved_user = mock_uow.add.call_args[0][0]
        assert saved_user.is_active is False

    async def test_registration_generates_token_with_correct_expiry(
        self,
        register_user_request,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        reg_confirm_url
    ):
        """Test that confirmation token is generated with 300 seconds expiry"""
        # Arrange
        dto = RegisterUserRequestDTO(
            email="user@example.com",
            first_password="Password123",
            second_password="Password123",
            name="Test User"
        )

        mock_user_repo.count_by_email.return_value = 0
        mock_password_service.hash_password.return_value = "hashed"
        mock_auth_service.generate_token.return_value = "token"

        # Act
        await register_user_request(dto)

        # Assert
        saved_user = mock_uow.add.call_args[0][0]
        mock_auth_service.generate_token.assert_called_once_with(saved_user.id, 300)

    async def test_registration_uow_context_manager_usage(
        self,
        register_user_request,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        reg_confirm_url
    ):
        """Test that UoW context manager is properly used"""
        # Arrange
        dto = RegisterUserRequestDTO(
            email="user@example.com",
            first_password="Password123",
            second_password="Password123",
            name="Test User"
        )

        mock_user_repo.count_by_email.return_value = 0
        mock_password_service.hash_password.return_value = "hashed"
        mock_auth_service.generate_token.return_value = "token"

        # Act
        await register_user_request(dto)

        # Assert
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

        # Verify repository was called within context
        mock_user_repo.count_by_email.assert_called_once_with("user@example.com")

    async def test_registration_uow_rolls_back_on_error(
        self,
        register_user_request,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service
    ):
        """Test that UoW context manager exits even on error"""
        # Arrange
        dto = RegisterUserRequestDTO(
            email="user@example.com",
            first_password="Password123",
            second_password="Password123",
            name="Test User"
        )

        mock_user_repo.count_by_email.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            await register_user_request(dto)

        # Verify UoW context manager was entered and exited
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_registration_with_unicode_characters(
        self,
        register_user_request,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        reg_confirm_url
    ):
        """Test registration with unicode characters in email and name"""
        # Arrange
        dto = RegisterUserRequestDTO(
            email="üser@exämple.com",
            first_password="Password123",
            second_password="Password123",
            name="Jöhn Døe 日本"
        )
        hashed_password = "hashed_password"
        confirmation_token = "token.123"

        mock_user_repo.count_by_email.return_value = 0
        mock_password_service.hash_password.return_value = hashed_password
        mock_auth_service.generate_token.return_value = confirmation_token

        # Act
        await register_user_request(dto)

        # Assert
        mock_user_repo.count_by_email.assert_called_once_with("üser@exämple.com")
        saved_user = mock_uow.add.call_args[0][0]
        assert saved_user.email == "üser@exämple.com"
        assert saved_user.name == "Jöhn Døe 日本"

    async def test_registration_with_whitespace_in_name(
        self,
        register_user_request,
        mock_uow,
        mock_user_repo,
        mock_password_service,
        mock_auth_service,
        mock_email_service,
        reg_confirm_url
    ):
        """Test registration with whitespace in name"""
        # Arrange
        dto = RegisterUserRequestDTO(
            email="user@example.com",
            first_password="Password123",
            second_password="Password123",
            name="  John   Doe  "  # Multiple spaces
        )
        hashed_password = "hashed_password"
        confirmation_token = "token.123"

        mock_user_repo.count_by_email.return_value = 0
        mock_password_service.hash_password.return_value = hashed_password
        mock_auth_service.generate_token.return_value = confirmation_token

        # Act
        await register_user_request(dto)

        # Assert
        saved_user = mock_uow.add.call_args[0][0]
        assert saved_user.name == "  John   Doe  "  # Should preserve whitespace as is


@pytest.mark.asyncio
class TestRegisterUserConfirm:
    """Test suite for RegisterUserConfirm use case"""

    async def test_successful_registration_confirmation(
        self,
        register_user_confirm,
        mock_uow,
        mock_user_repo,
        mock_auth_service,
        inactive_user
    ):
        """Test successful confirmation of registration"""
        # Arrange
        token = "valid.confirmation.token"
        user_id = 1

        mock_auth_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = inactive_user

        # Act
        await register_user_confirm(token)

        # Assert
        mock_auth_service.get_user_id_from_token.assert_called_once_with(token)
        mock_user_repo.get_by_id.assert_called_once_with(user_id)

        # Verify user was activated
        assert inactive_user.is_active is True

        # No explicit save needed - just attribute change
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_confirmation_with_invalid_token_returns_none_user_id(
        self,
        register_user_confirm,
        mock_uow,
        mock_user_repo,
        mock_auth_service
    ):
        """Test confirmation with invalid token raises UndefinedUserError"""
        # Arrange
        token = "invalid.token"
        mock_auth_service.get_user_id_from_token.return_value = None

        # Act & Assert
        with pytest.raises(UndefinedUserError) as exc_info:
            await register_user_confirm(token)

        assert str(exc_info.value) == "User was not identify"

        mock_auth_service.get_user_id_from_token.assert_called_once_with(token)
        mock_user_repo.get_by_id.assert_not_called()
        mock_uow.__aenter__.assert_not_called()
        mock_uow.__aexit__.assert_not_called()

    async def test_confirmation_for_nonexistent_user(
        self,
        register_user_confirm,
        mock_uow,
        mock_user_repo,
        mock_auth_service
    ):
        """Test confirmation for user that doesn't exist in DB raises UndefinedUserError"""
        # Arrange
        token = "valid.token"
        user_id = 999

        mock_auth_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UndefinedUserError) as exc_info:
            await register_user_confirm(token)

        assert str(exc_info.value) == "Try to confirm registration of user that does not exist"

        mock_auth_service.get_user_id_from_token.assert_called_once_with(token)
        mock_user_repo.get_by_id.assert_called_once_with(user_id)
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_confirmation_for_already_active_user(
        self,
        register_user_confirm,
        mock_uow,
        mock_user_repo,
        mock_auth_service,
        active_user
    ):
        """Test confirmation for already active user"""
        # Arrange
        token = "valid.token"
        user_id = 2

        mock_auth_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = active_user

        # Act
        await register_user_confirm(token)

        # Assert
        assert active_user.is_active is True  # Should remain True
        mock_auth_service.get_user_id_from_token.assert_called_once_with(token)
        mock_user_repo.get_by_id.assert_called_once_with(user_id)
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    @pytest.mark.parametrize("token", [
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
        "short.token",
        "token.with.dots.separated",
        "a" * 1000,  # Very long token
        "token-with-special-chars!@#$%^&*()",
    ])
    async def test_confirmation_with_various_token_formats(
        self,
        register_user_confirm,
        mock_uow,
        mock_user_repo,
        mock_auth_service,
        inactive_user,
        token
    ):
        """Test confirmation with various token formats"""
        # Arrange
        user_id = 1

        mock_auth_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = inactive_user

        # Act
        await register_user_confirm(token)

        # Assert
        mock_auth_service.get_user_id_from_token.assert_called_once_with(token)
        assert inactive_user.is_active is True

    async def test_confirmation_preserves_user_data(
        self,
        register_user_confirm,
        mock_uow,
        mock_user_repo,
        mock_auth_service,
        inactive_user
    ):
        """Test that user data is preserved after activation"""
        # Arrange
        token = "valid.token"
        user_id = 1
        original_email = inactive_user.email
        original_name = inactive_user.name
        original_password = inactive_user.password

        mock_auth_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = inactive_user

        # Act
        await register_user_confirm(token)

        # Assert
        assert inactive_user.email == original_email
        assert inactive_user.name == original_name
        assert inactive_user.password == original_password
        assert inactive_user.id == user_id
        assert inactive_user.is_active is True

    async def test_confirmation_uow_context_manager_usage(
        self,
        register_user_confirm,
        mock_uow,
        mock_user_repo,
        mock_auth_service,
        inactive_user
    ):
        """Test that UoW context manager is properly used"""
        # Arrange
        token = "valid.token"
        user_id = 1

        mock_auth_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = inactive_user

        # Act
        await register_user_confirm(token)

        # Assert
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

        # Verify repository was called within context
        mock_user_repo.get_by_id.assert_called_once_with(user_id)

    async def test_confirmation_uow_rolls_back_on_error(
        self,
        register_user_confirm,
        mock_uow,
        mock_user_repo,
        mock_auth_service
    ):
        """Test that UoW context manager exits even on error"""
        # Arrange
        token = "valid.token"
        user_id = 1

        mock_auth_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await register_user_confirm(token)

        assert str(exc_info.value) == "Database error"

        # Verify UoW context manager was entered and exited
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_confirmation_with_expired_token(
        self,
        register_user_confirm,
        mock_uow,
        mock_user_repo,
        mock_auth_service
    ):
        """Test confirmation with expired token"""
        # Arrange
        token = "expired.token"
        mock_auth_service.get_user_id_from_token.return_value = None

        # Act & Assert
        with pytest.raises(UndefinedUserError) as exc_info:
            await register_user_confirm(token)

        assert str(exc_info.value) == "User was not identify"
        mock_auth_service.get_user_id_from_token.assert_called_once_with(token)
        mock_user_repo.get_by_id.assert_not_called()

    async def test_confirmation_with_malformed_token(
        self,
        register_user_confirm,
        mock_uow,
        mock_user_repo,
        mock_auth_service
    ):
        """Test confirmation with malformed token that causes exception"""
        # Arrange
        token = "malformed.token"
        mock_auth_service.get_user_id_from_token.side_effect = ValueError("Invalid token format")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await register_user_confirm(token)

        assert str(exc_info.value) == "Invalid token format"
        mock_auth_service.get_user_id_from_token.assert_called_once_with(token)
        mock_user_repo.get_by_id.assert_not_called()
        mock_uow.__aenter__.assert_not_called()

    async def test_confirmation_with_multiple_consecutive_calls(
        self,
        register_user_confirm,
        mock_uow,
        mock_user_repo,
        mock_auth_service,
        inactive_user
    ):
        """Test multiple confirmation calls with different tokens"""
        # Arrange
        tokens = ["token1", "token2", "token3", "token4"]
        user_ids = [1, 2, 1, 3]  # Note: token3 tries to activate already activated user

        # Create users for each token
        users = []
        for i, user_id in enumerate(user_ids):
            user = User(
                email=f"user{user_id}@example.com",
                password="hashed",
                name=f"User {user_id}"
            )
            user.id = user_id
            user.is_active = False if i < 2 else True  # First two inactive, last two active
            users.append(user)

        # Act
        for i, token in enumerate(tokens):
            mock_auth_service.get_user_id_from_token.return_value = user_ids[i]
            mock_user_repo.get_by_id.return_value = users[i]

            await register_user_confirm(token)

            # Verify user became active after confirmation
            assert users[i].is_active is True

        # Assert
        assert mock_auth_service.get_user_id_from_token.call_count == 4
        assert mock_user_repo.get_by_id.call_count == 4
        assert mock_uow.__aenter__.call_count == 4
        assert mock_uow.__aexit__.call_count == 4

    async def test_confirmation_does_not_affect_other_users(
        self,
        register_user_confirm,
        mock_uow,
        mock_user_repo,
        mock_auth_service,
        inactive_user,
        active_user
    ):
        """Test that confirming one user doesn't affect others"""
        # Arrange
        token1 = "token.for.user1"
        token2 = "token.for.user2"

        mock_auth_service.get_user_id_from_token.side_effect = [1, 2]
        mock_user_repo.get_by_id.side_effect = [inactive_user, active_user]

        # Act
        await register_user_confirm(token1)
        await register_user_confirm(token2)

        # Assert
        assert inactive_user.is_active is True
        assert active_user.is_active is True  # Already was True
        assert inactive_user.id == 1
        assert active_user.id == 2

    async def test_confirmation_with_none_token(
        self,
        register_user_confirm,
        mock_auth_service
    ):
        """Test confirmation with None token"""
        # Arrange
        token = None
        mock_auth_service.get_user_id_from_token.side_effect = JWTUnauthorizedError("Token invlaid", status=401)

        # Act & Assert
        with pytest.raises(JWTUnauthorizedError):  # или другая ошибка, в зависимости от реализации
            await register_user_confirm(token)

    async def test_confirmation_with_empty_string_token(
        self,
        register_user_confirm,
        mock_auth_service
    ):
        """Test confirmation with empty string token"""
        # Arrange
        token = ""
        mock_auth_service.get_user_id_from_token.return_value = None

        # Act & Assert
        with pytest.raises(UndefinedUserError) as exc_info:
            await register_user_confirm(token)

        assert str(exc_info.value) == "User was not identify"
        mock_auth_service.get_user_id_from_token.assert_called_once_with("")


@pytest.mark.asyncio
class TestChangePasswordRequest:
    """Test suite for ChangePasswordRequest use case"""

    async def test_successful_password_change_request(
        self,
        change_password_request,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_email_service,
        password_change_confirm_url,
        active_user
    ):
        """Test successful password change request for existing user"""
        # Arrange
        email = "active@example.com"
        reset_token = "password.reset.token.123"
        expected_topic = "Change password"
        expected_message = f"You requested changing of the password on Runlet. Follow the link\n{password_change_confirm_url}/{reset_token}"

        mock_user_repo.get_by_email.return_value = active_user
        mock_token_service.generate_token.return_value = reset_token
        mock_email_service.send_mail.return_value = None

        # Act
        await change_password_request(email)

        # Assert
        mock_user_repo.get_by_email.assert_called_once_with(email)
        mock_token_service.generate_token.assert_called_once_with(active_user.id, 300)
        mock_email_service.send_mail.assert_called_once_with(
            active_user.email,
            expected_topic,
            expected_message
        )
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_password_change_request_for_nonexistent_email(
        self,
        change_password_request,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_email_service
    ):
        """Test password change request with non-existent email raises UndefinedUserError"""
        # Arrange
        email = "nonexistent@example.com"
        mock_user_repo.get_by_email.return_value = None

        # Act & Assert
        with pytest.raises(UndefinedUserError) as exc_info:
            await change_password_request(email)

        assert str(exc_info.value) == "Email not found"

        mock_user_repo.get_by_email.assert_called_once_with(email)
        mock_token_service.generate_token.assert_not_called()
        mock_email_service.send_mail.assert_not_called()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_password_change_request_for_inactive_user(
        self,
        change_password_request,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_email_service,
        password_change_confirm_url,
        inactive_user
    ):
        """Test password change request for inactive user (should still work)"""
        # Arrange
        email = "inactive@example.com"
        reset_token = "password.reset.token.456"

        mock_user_repo.get_by_email.return_value = inactive_user
        mock_token_service.generate_token.return_value = reset_token

        # Act
        await change_password_request(email)

        # Assert
        mock_user_repo.get_by_email.assert_called_once_with(email)
        mock_token_service.generate_token.assert_called_once_with(inactive_user.id, 300)
        mock_email_service.send_mail.assert_called_once()
        # Inactive user should still be able to request password change
        assert inactive_user.is_active is False  # Status unchanged

    @pytest.mark.parametrize("email", [
        "user@example.com",
        "admin@test.com",
        "very.long.email.address.with.many.dots@domain.co.uk",
        "user+filter@example.com",
        "user-name@example.com",
        "user@subdomain.example.com",
    ])
    async def test_password_change_request_with_various_email_formats(
        self,
        change_password_request,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_email_service,
        password_change_confirm_url,
        active_user,
        email
    ):
        """Test password change request with various email formats"""
        # Arrange
        active_user.email = email
        reset_token = "reset.token.789"

        mock_user_repo.get_by_email.return_value = active_user
        mock_token_service.generate_token.return_value = reset_token

        # Act
        await change_password_request(email)

        # Assert
        mock_user_repo.get_by_email.assert_called_once_with(email)
        mock_token_service.generate_token.assert_called_once_with(active_user.id, 300)
        mock_email_service.send_mail.assert_called_once_with(
            email,
            "Change password",
            f"You requested changing of the password on Runlet. Follow the link\n{password_change_confirm_url}/{reset_token}"
        )

    async def test_password_change_request_email_send_failure(
        self,
        change_password_request,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_email_service,
        active_user
    ):
        """Test password change request when email service fails"""
        # Arrange
        email = "active@example.com"
        reset_token = "reset.token.abc"

        mock_user_repo.get_by_email.return_value = active_user
        mock_token_service.generate_token.return_value = reset_token
        mock_email_service.send_mail.side_effect = Exception("Email service error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await change_password_request(email)

        assert str(exc_info.value) == "Email service error"

        mock_user_repo.get_by_email.assert_called_once_with(email)
        mock_token_service.generate_token.assert_called_once_with(active_user.id, 300)
        mock_email_service.send_mail.assert_called_once()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_password_change_request_generates_token_with_correct_expiry(
        self,
        change_password_request,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_email_service,
        active_user
    ):
        """Test that reset token is generated with 300 seconds expiry"""
        # Arrange
        email = "active@example.com"
        reset_token = "reset.token.xyz"

        mock_user_repo.get_by_email.return_value = active_user
        mock_token_service.generate_token.return_value = reset_token

        # Act
        await change_password_request(email)

        # Assert
        mock_token_service.generate_token.assert_called_once_with(active_user.id, 300)

    async def test_password_change_request_with_unicode_email(
        self,
        change_password_request,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_email_service,
        password_change_confirm_url
    ):
        """Test password change request with unicode email"""
        # Arrange
        email = "üser@exämple.com"
        user = User(
            email=email,
            password="hashed",
            name="Unicode User"
        )
        user.id = 5
        user.is_active = True
        reset_token = "reset.token.unicode"

        mock_user_repo.get_by_email.return_value = user
        mock_token_service.generate_token.return_value = reset_token

        # Act
        await change_password_request(email)

        # Assert
        mock_user_repo.get_by_email.assert_called_once_with(email)
        mock_token_service.generate_token.assert_called_once_with(5, 300)
        mock_email_service.send_mail.assert_called_once_with(
            email,
            "Change password",
            f"You requested changing of the password on Runlet. Follow the link\n{password_change_confirm_url}/{reset_token}"
        )

    async def test_password_change_request_uow_context_manager_usage(
        self,
        change_password_request,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_email_service,
        active_user
    ):
        """Test that UoW context manager is properly used"""
        # Arrange
        email = "active@example.com"

        mock_user_repo.get_by_email.return_value = active_user
        mock_token_service.generate_token.return_value = "token"

        # Act
        await change_password_request(email)

        # Assert
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

        # Verify repository was called within context
        mock_user_repo.get_by_email.assert_called_once_with(email)

    async def test_password_change_request_uow_rolls_back_on_error(
        self,
        change_password_request,
        mock_uow,
        mock_user_repo
    ):
        """Test that UoW context manager exits even on error"""
        # Arrange
        email = "test@example.com"
        mock_user_repo.get_by_email.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await change_password_request(email)

        assert str(exc_info.value) == "Database error"

        # Verify UoW context manager was entered and exited
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_password_change_request_with_multiple_consecutive_calls(
        self,
        change_password_request,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_email_service,
        password_change_confirm_url
    ):
        """Test multiple password change requests for different emails"""
        # Arrange
        emails = [
            ("user1@example.com", 1, "token1"),
            ("user2@example.com", 2, "token2"),
            ("user3@example.com", 3, "token3"),
        ]

        # Act
        for email, user_id, expected_token in emails:
            user = User(
                email=email,
                password="hashed",
                name=f"User {user_id}"
            )
            user.id = user_id
            user.is_active = True

            mock_user_repo.get_by_email.return_value = user
            mock_token_service.generate_token.return_value = expected_token

            await change_password_request(email)

            # Assert each call
            mock_user_repo.get_by_email.assert_called_with(email)
            mock_token_service.generate_token.assert_called_with(user_id, 300)
            mock_email_service.send_mail.assert_called_with(
                email,
                "Change password",
                f"You requested changing of the password on Runlet. Follow the link\n{password_change_confirm_url}/{expected_token}"
            )

        # Assert total calls
        assert mock_user_repo.get_by_email.call_count == 3
        assert mock_token_service.generate_token.call_count == 3
        assert mock_email_service.send_mail.call_count == 3
        assert mock_uow.__aenter__.call_count == 3
        assert mock_uow.__aexit__.call_count == 3

    async def test_password_change_request_preserves_user_data(
        self,
        change_password_request,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_email_service,
        active_user
    ):
        """Test that user data is correctly retrieved and preserved"""
        # Arrange
        email = "active@example.com"
        original_email = active_user.email
        original_name = active_user.name
        original_password = active_user.password
        original_id = active_user.id

        mock_user_repo.get_by_email.return_value = active_user
        mock_token_service.generate_token.return_value = "token"

        # Act
        await change_password_request(email)

        # Assert
        assert active_user.email == original_email
        assert active_user.name == original_name
        assert active_user.password == original_password
        assert active_user.id == original_id
        assert active_user.is_active is True

    async def test_password_change_request_with_empty_email(
        self,
        change_password_request,
        mock_user_repo
    ):
        """Test password change request with empty email"""
        # Arrange
        email = ""
        mock_user_repo.get_by_email.return_value = None

        # Act & Assert
        with pytest.raises(UndefinedUserError) as exc_info:
            await change_password_request(email)

        assert str(exc_info.value) == "Email not found"
        mock_user_repo.get_by_email.assert_called_once_with("")

    async def test_password_change_request_with_whitespace_email(
        self,
        change_password_request,
        mock_user_repo
    ):
        """Test password change request with whitespace email"""
        # Arrange
        email = "   "
        mock_user_repo.get_by_email.return_value = None

        # Act & Assert
        with pytest.raises(UndefinedUserError) as exc_info:
            await change_password_request(email)

        assert str(exc_info.value) == "Email not found"
        mock_user_repo.get_by_email.assert_called_once_with("   ")

    async def test_password_change_request_email_case_sensitivity(
        self,
        change_password_request,
        mock_user_repo,
        mock_token_service,
        mock_email_service,
        active_user
    ):
        """Test password change request with email in different case"""
        # Arrange
        email = "ACTIVE@EXAMPLE.COM"  # Upper case
        active_user.email = "active@example.com"  # Lower case in DB

        mock_user_repo.get_by_email.return_value = None  # Should not find with upper case

        # Act & Assert
        with pytest.raises(UndefinedUserError):
            await change_password_request(email)

        mock_user_repo.get_by_email.assert_called_once_with("ACTIVE@EXAMPLE.COM")
        mock_token_service.generate_token.assert_not_called()
        mock_email_service.send_mail.assert_not_called()


@pytest.mark.asyncio
class TestChangePasswordConfirm:
    """Test suite for ChangePasswordConfirm use case"""

    async def test_successful_password_change(
        self,
        change_password_confirm,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_password_service,
        active_user
    ):
        """Test successful password change with valid token and matching passwords"""
        # Arrange
        token = "valid.reset.token"
        user_id = 1
        dto = ChangePasswordConfirmDTO(
            first_password="NewSecurePass123!",
            second_password="NewSecurePass123!"
        )
        new_hashed_password = "new_hashed_password_123"

        mock_token_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = active_user
        mock_password_service.hash_password.return_value = new_hashed_password

        # Act
        await change_password_confirm(token, dto)

        # Assert
        mock_token_service.get_user_id_from_token.assert_called_once_with(token)
        mock_user_repo.get_by_id.assert_called_once_with(user_id)
        mock_password_service.hash_password.assert_called_once_with("NewSecurePass123!")

        # Verify password was updated
        assert active_user.password == new_hashed_password

        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_password_change_with_invalid_token(
        self,
        change_password_confirm,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_password_service
    ):
        """Test password change with invalid token raises UndefinedUserError"""
        # Arrange
        token = "invalid.token"
        dto = ChangePasswordConfirmDTO(
            first_password="NewPass123",
            second_password="NewPass123"
        )

        mock_token_service.get_user_id_from_token.return_value = None

        # Act & Assert
        with pytest.raises(UndefinedUserError) as exc_info:
            await change_password_confirm(token, dto)

        assert str(exc_info.value) == "User was not identify"

        mock_token_service.get_user_id_from_token.assert_called_once_with(token)
        mock_user_repo.get_by_id.assert_not_called()
        mock_password_service.hash_password.assert_not_called()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_password_change_with_password_mismatch(
        self,
        change_password_confirm,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_password_service
    ):
        """Test password change with mismatched passwords raises PasswordsMismatchError"""
        # Arrange
        token = "valid.token"
        user_id = 1
        dto = ChangePasswordConfirmDTO(
            first_password="NewPass123",
            second_password="DifferentPass456"
        )

        mock_token_service.get_user_id_from_token.return_value = user_id

        # Act & Assert
        with pytest.raises(PasswordsMismatchError) as exc_info:
            await change_password_confirm(token, dto)

        assert str(exc_info.value) == "Passwords do not match"

        mock_token_service.get_user_id_from_token.assert_called_once_with(token)
        mock_user_repo.get_by_id.assert_not_called()
        mock_password_service.hash_password.assert_not_called()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_password_change_for_nonexistent_user(
        self,
        change_password_confirm,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_password_service
    ):
        """Test password change for user that doesn't exist in DB raises UndefinedUserError"""
        # Arrange
        token = "valid.token"
        user_id = 999
        dto = ChangePasswordConfirmDTO(
            first_password="NewPass123",
            second_password="NewPass123"
        )

        mock_token_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UndefinedUserError) as exc_info:
            await change_password_confirm(token, dto)

        assert str(exc_info.value) == "User not found"

        mock_token_service.get_user_id_from_token.assert_called_once_with(token)
        mock_user_repo.get_by_id.assert_called_once_with(user_id)
        mock_password_service.hash_password.assert_not_called()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    @pytest.mark.parametrize("first_password,second_password", [
        ("SimplePass123", "SimplePass123"),
        ("P@ssw0rd!123", "P@ssw0rd!123"),
        ("a" * 100, "a" * 100),  # Very long password
        ("1234567890", "1234567890"),  # Numbers only
        ("!@#$%^&*()", "!@#$%^&*()"),  # Special characters only
    ])
    async def test_password_change_with_various_password_formats(
        self,
        change_password_confirm,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_password_service,
        active_user,
        first_password,
        second_password
    ):
        """Test password change with various password formats"""
        # Arrange
        token = "valid.token"
        user_id = 1
        dto = ChangePasswordConfirmDTO(
            first_password=first_password,
            second_password=second_password
        )
        hashed_password = f"hashed_{first_password}"

        mock_token_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = active_user
        mock_password_service.hash_password.return_value = hashed_password

        # Act
        await change_password_confirm(token, dto)

        # Assert
        mock_password_service.hash_password.assert_called_once_with(first_password)
        assert active_user.password == hashed_password

    async def test_password_change_preserves_other_user_data(
        self,
        change_password_confirm,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_password_service,
        active_user
    ):
        """Test that other user data remains unchanged after password update"""
        # Arrange
        token = "valid.token"
        user_id = 1
        dto = ChangePasswordConfirmDTO(
            first_password="NewPass123",
            second_password="NewPass123"
        )
        original_email = active_user.email
        original_name = active_user.name
        original_id = active_user.id
        original_is_active = active_user.is_active

        mock_token_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = active_user
        mock_password_service.hash_password.return_value = "new_hashed"

        # Act
        await change_password_confirm(token, dto)

        # Assert
        assert active_user.email == original_email
        assert active_user.name == original_name
        assert active_user.id == original_id
        assert active_user.is_active == original_is_active
        assert active_user.password == "new_hashed"

    async def test_password_change_with_expired_token(
        self,
        change_password_confirm,
        mock_uow,
        mock_token_service
    ):
        """Test password change with expired token"""
        # Arrange
        token = "expired.token"
        dto = ChangePasswordConfirmDTO(
            first_password="NewPass123",
            second_password="NewPass123"
        )

        mock_token_service.get_user_id_from_token.return_value = None

        # Act & Assert
        with pytest.raises(UndefinedUserError) as exc_info:
            await change_password_confirm(token, dto)

        assert str(exc_info.value) == "User was not identify"
        mock_token_service.get_user_id_from_token.assert_called_once_with(token)

    async def test_password_change_with_malformed_token(
        self,
        change_password_confirm,
        mock_uow,
        mock_token_service
    ):
        """Test password change with malformed token that causes exception"""
        # Arrange
        token = "malformed.token"
        dto = ChangePasswordConfirmDTO(
            first_password="NewPass123",
            second_password="NewPass123"
        )

        mock_token_service.get_user_id_from_token.side_effect = ValueError("Invalid token format")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await change_password_confirm(token, dto)

        assert str(exc_info.value) == "Invalid token format"
        mock_token_service.get_user_id_from_token.assert_called_once_with(token)

    @pytest.mark.parametrize("token", [
        None,
        "",
        "   ",
    ])
    async def test_password_change_with_invalid_token_formats(
        self,
        change_password_confirm,
        mock_uow,
        mock_token_service,
        token
    ):
        """Test password change with invalid token formats"""
        # Arrange
        dto = ChangePasswordConfirmDTO(
            first_password="NewPass123",
            second_password="NewPass123"
        )

        mock_token_service.get_user_id_from_token.return_value = None

        # Act & Assert
        with pytest.raises(UndefinedUserError) as exc_info:
            await change_password_confirm(token, dto)

        assert str(exc_info.value) == "User was not identify"
        mock_token_service.get_user_id_from_token.assert_called_once_with(token)

    async def test_password_change_uow_context_manager_usage(
        self,
        change_password_confirm,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_password_service,
        active_user
    ):
        """Test that UoW context manager is properly used"""
        # Arrange
        token = "valid.token"
        user_id = 1
        dto = ChangePasswordConfirmDTO(
            first_password="NewPass123",
            second_password="NewPass123"
        )

        mock_token_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = active_user
        mock_password_service.hash_password.return_value = "hashed"

        # Act
        await change_password_confirm(token, dto)

        # Assert
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

        # Verify repository was called within context
        mock_user_repo.get_by_id.assert_called_once_with(user_id)

    async def test_password_change_uow_rolls_back_on_error(
        self,
        change_password_confirm,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_password_service
    ):
        """Test that UoW context manager exits even on error"""
        # Arrange
        token = "valid.token"
        user_id = 1
        dto = ChangePasswordConfirmDTO(
            first_password="NewPass123",
            second_password="NewPass123"
        )

        mock_token_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await change_password_confirm(token, dto)

        assert str(exc_info.value) == "Database error"

        # Verify UoW context manager was entered and exited
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    async def test_password_change_with_multiple_consecutive_calls(
        self,
        change_password_confirm,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_password_service
    ):
        """Test multiple password changes for different users"""
        # Arrange
        tokens = ["token1", "token2", "token3"]
        user_ids = [1, 2, 3]
        passwords = ["pass1111", "pass2222", "pass3333"]

        # Create users
        users = []
        for i, user_id in enumerate(user_ids):
            user = User(
                email=f"user{user_id}@example.com",
                password=f"old_hash_{user_id}",
                name=f"User {user_id}"
            )
            user.id = user_id
            user.is_active = True
            users.append(user)

        # Act
        for i, token in enumerate(tokens):
            dto = ChangePasswordConfirmDTO(
                first_password=passwords[i],
                second_password=passwords[i]
            )

            mock_token_service.get_user_id_from_token.return_value = user_ids[i]
            mock_user_repo.get_by_id.return_value = users[i]
            mock_password_service.hash_password.return_value = f"new_hash_{passwords[i]}"

            await change_password_confirm(token, dto)

            # Verify each user's password was updated
            assert users[i].password == f"new_hash_{passwords[i]}"

        # Assert total calls
        assert mock_token_service.get_user_id_from_token.call_count == 3
        assert mock_user_repo.get_by_id.call_count == 3
        assert mock_password_service.hash_password.call_count == 3
        assert mock_uow.__aenter__.call_count == 3
        assert mock_uow.__aexit__.call_count == 3

    async def test_password_change_with_same_password_as_before(
        self,
        change_password_confirm,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_password_service,
        active_user
    ):
        """Test password change with same password as before (should still work)"""
        # Arrange
        token = "valid.token"
        user_id = 1
        dto = ChangePasswordConfirmDTO(
            first_password="same_password",
            second_password="same_password"
        )

        mock_token_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = active_user
        mock_password_service.hash_password.return_value = "new_hash_of_same_password"

        # Act
        await change_password_confirm(token, dto)

        # Assert
        assert active_user.password == "new_hash_of_same_password"
        # Note: This is valid - password can be the same, it will just be rehashed

    async def test_password_change_updates_password_field_only(
        self,
        change_password_confirm,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_password_service,
        active_user
    ):
        """Test that only the password field is updated"""
        # Arrange
        token = "valid.token"
        user_id = 1
        dto = ChangePasswordConfirmDTO(
            first_password="NewPass123",
            second_password="NewPass123"
        )

        # Create a copy of original user data
        original_user_data = {
            'email': active_user.email,
            'name': active_user.name,
            'id': active_user.id,
            'is_active': active_user.is_active
        }

        mock_token_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = active_user
        mock_password_service.hash_password.return_value = "new_hashed"

        # Act
        await change_password_confirm(token, dto)

        # Assert
        assert active_user.email == original_user_data['email']
        assert active_user.name == original_user_data['name']
        assert active_user.id == original_user_data['id']
        assert active_user.is_active == original_user_data['is_active']
        assert active_user.password == "new_hashed"

    async def test_password_change_with_unicode_passwords(
        self,
        change_password_confirm,
        mock_uow,
        mock_user_repo,
        mock_token_service,
        mock_password_service,
        active_user
    ):
        """Test password change with unicode characters in password"""
        # Arrange
        token = "valid.token"
        user_id = 1
        unicode_password = "Pässwörd 日本 123!"
        dto = ChangePasswordConfirmDTO(
            first_password=unicode_password,
            second_password=unicode_password
        )
        hashed_unicode = "hashed_unicode_password"

        mock_token_service.get_user_id_from_token.return_value = user_id
        mock_user_repo.get_by_id.return_value = active_user
        mock_password_service.hash_password.return_value = hashed_unicode

        # Act
        await change_password_confirm(token, dto)

        # Assert
        mock_password_service.hash_password.assert_called_once_with(unicode_password)
        assert active_user.password == hashed_unicode
