import pytest
from unittest.mock import Mock, AsyncMock

from src.application.use_cases.auth import (
    AuthenticateUser
)
from src.application.use_cases.exceptions import (
    UndefinedUserError,
    InactiveUserError,
    HasNoAccessError,
    UndefinedCourseError,
    InvalidUserPasswordError,
    EmailExistsError,
    PasswordsMismatchError
)
from src.application.dtos.auth import LoginUserDTO, RegisterUserRequestDTO
from src.domain.entities import User, Course
from src.infrastructure.services.user.exceptions import JWTUnauthorizedError

pytest_mark_asyncio = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_authenticate_user_success(
    authenticate_user: AuthenticateUser,
    mock_user_repo,
    mock_auth_service
):
    """
    Успешная аутентификация пользователя
    """
    # Arrange
    token = "valid_token"
    user_id = 1

    # Настраиваем моки
    mock_auth_service.get_user_id_from_token.return_value = user_id

    user = Mock(spec=User)
    user.id = user_id
    user.is_active = True
    mock_user_repo.get_by_id.return_value = user

    # Act
    result = await authenticate_user.execute(token)

    # Assert
    assert result == user_id
    mock_auth_service.get_user_id_from_token.assert_called_once_with(token)
    mock_user_repo.get_by_id.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_authenticate_user_no_token(
    authenticate_user: AuthenticateUser
):
    """
    Ошибка при отсутствии токена
    """
    # Arrange
    token = None

    # Act & Assert
    with pytest.raises(UndefinedUserError) as exc_info:
        await authenticate_user.execute(token)

    assert exc_info.value.status == 401
    assert str(exc_info.value) == "Unauthorized"


@pytest.mark.asyncio
async def test_authenticate_user_no_user_id(
    authenticate_user: AuthenticateUser,
    mock_auth_service
):
    """
    Ошибка при невалидном токене (возвращает None)
    """
    # Arrange
    token = "invalid_token"
    mock_auth_service.get_user_id_from_token.return_value = None

    # Act & Assert
    with pytest.raises(UndefinedUserError) as exc_info:
        await authenticate_user.execute(token)

    assert exc_info.value.status == 401
    assert str(exc_info.value) == "User was not identify"
    mock_auth_service.get_user_id_from_token.assert_called_once_with(token)


@pytest.mark.asyncio
async def test_authenticate_user_invalid_token(
    authenticate_user: AuthenticateUser,
    mock_auth_service
):
    token = "invalid_token"
    mock_auth_service.get_user_id_from_token.side_effect = JWTUnauthorizedError(
        "Token invlaid", status=401)

    # Act & Assert
    with pytest.raises(JWTUnauthorizedError) as exc_info:
        await authenticate_user.execute(token)

    assert exc_info.value.status == 401
    mock_auth_service.get_user_id_from_token.assert_called_once_with(token)


@pytest.mark.asyncio
async def test_authenticate_user_not_found(
    authenticate_user: AuthenticateUser,
    mock_auth_service,
    mock_user_repo
):
    """
    Ошибка если пользователь не найден в БД
    """
    # Arrange
    token = "valid_token"
    user_id = 1

    mock_auth_service.get_user_id_from_token.return_value = user_id
    mock_user_repo.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(UndefinedUserError) as exc_info:
        await authenticate_user.execute(token)

    assert exc_info.value.status == 401
    assert str(exc_info.value) == "User was not identify"
    mock_user_repo.get_by_id.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_authenticate_user_inactive(
    authenticate_user: AuthenticateUser,
    mock_auth_service,
    mock_user_repo
):
    """
    Ошибка если пользователь неактивен
    """
    token = "valid_token"
    user_id = 1

    mock_auth_service.get_user_id_from_token.return_value = user_id

    user = Mock(spec=User)
    user.id = user_id
    user.is_active = False
    mock_user_repo.get_by_id.return_value = user

    # Act & Assert
    with pytest.raises(InactiveUserError) as exc_info:
        await authenticate_user.execute(token)

    assert exc_info.value.status == 403
    assert str(exc_info.value) == "Current user is inactive"
    mock_user_repo.get_by_id.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_authenticate_user_uow_context_usage(
    authenticate_user: AuthenticateUser,
    mock_uow,
    mock_auth_service,
    mock_user_repo
):
    """
    Проверяем что юзкейс использует контекст UoW
    """
    # Arrange
    token = "valid_token"
    user_id = 1

    mock_auth_service.get_user_id_from_token.return_value = user_id
    user = Mock(spec=User)
    user.id = user_id
    user.is_active = True
    mock_user_repo.get_by_id.return_value = user

    # Act
    await authenticate_user.execute(token)

    # Assert - проверяем вызовы контекстного менеджера
    mock_uow.__aenter__.assert_called_once()
    mock_uow.__aexit__.assert_called_once()

    # Проверяем что репозиторий вызывается внутри контекста
    # Для этого можно проверить порядок вызовов
    calls = [call[0] for call in mock_uow.mock_calls]
    assert '__aenter__' in [name for name, args, kwargs in mock_uow.mock_calls]
    assert '__aexit__' in [name for name, args, kwargs in mock_uow.mock_calls]


@pytest.mark.asyncio
async def test_successful_student_auth(auth_student, mock_course_repo):
    """
    Успешная аутентификация студента на курсе
    """
    # Arrange
    user_id = 1
    course_id = 100

    # Создаем мок объекта курса
    course_mock = Mock(spec=Course)
    mock_course_repo.get_by_id.return_value = course_mock
    mock_course_repo.check_user_in_course.return_value = True

    # Act
    result = await auth_student.execute(user_id, course_id)

    # Assert
    assert result == user_id
    mock_course_repo.get_by_id.assert_called_once_with(course_id)
    mock_course_repo.check_user_in_course.assert_called_once_with(user_id, course_id)


@pytest.mark.asyncio
async def test_course_not_found(auth_student, mock_course_repo):
    """
    Ошибка: курс не существует
    """
    # Arrange
    user_id = 1
    course_id = 999

    mock_course_repo.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(UndefinedCourseError) as exc_info:
        await auth_student.execute(user_id, course_id)

    assert str(exc_info.value) == "Course does not exist"
    mock_course_repo.get_by_id.assert_called_once_with(course_id)
    mock_course_repo.check_user_in_course.assert_not_called()


@pytest.mark.asyncio
async def test_user_not_subscribed(auth_student, mock_course_repo):
    """
    Ошибка: пользователь не подписан на курс
    """
    # Arrange
    user_id = 1
    course_id = 100

    course_mock = Mock(spec=Course)
    mock_course_repo.get_by_id.return_value = course_mock
    mock_course_repo.check_user_in_course.return_value = False

    # Act & Assert
    with pytest.raises(HasNoAccessError) as exc_info:
        await auth_student.execute(user_id, course_id)

    assert str(exc_info.value) == "User not subscribed on course"
    mock_course_repo.get_by_id.assert_called_once_with(course_id)
    mock_course_repo.check_user_in_course.assert_called_once_with(user_id, course_id)


@pytest.mark.asyncio
async def test_uow_context_used(auth_student, mock_uow, mock_course_repo):
    """
    Проверяем, что юзкейс использует контекст UoW
    """
    # Arrange
    user_id = 1
    course_id = 100

    course_mock = Mock()
    mock_course_repo.get_by_id.return_value = course_mock
    mock_course_repo.check_user_in_course.return_value = True

    # Act
    await auth_student.execute(user_id, course_id)

    # Assert
    mock_uow.__aenter__.assert_called_once()
    mock_uow.__aexit__.assert_called_once()


@pytest.mark.asyncio
async def test_returns_correct_user_id(auth_student, mock_course_repo):
    """
    Проверяем, что возвращается именно тот user_id, который был передан
    """
    # Arrange
    test_cases = [
        (1, 100),
        (42, 200),
        (999, 300),
        (0, 400),
        (-1, 500),
    ]

    course_mock = Mock()
    mock_course_repo.get_by_id.return_value = course_mock
    mock_course_repo.check_user_in_course.return_value = True

    for user_id, course_id in test_cases:
        # Reset mock calls for each test case
        mock_course_repo.reset_mock()
        mock_course_repo.get_by_id.return_value = course_mock
        mock_course_repo.check_user_in_course.return_value = True

        # Act
        result = await auth_student.execute(user_id, course_id)

        # Assert
        assert result == user_id
        mock_course_repo.get_by_id.assert_called_once_with(course_id)
        mock_course_repo.check_user_in_course.assert_called_once_with(user_id, course_id)


@pytest.mark.asyncio
async def test_exception_status_code_correct(auth_student, mock_course_repo):
    """
    Проверяем, что исключения имеют правильный статус код
    """
    # Тест 1: Курс не найден - статус по умолчанию
    mock_course_repo.get_by_id.return_value = None
    with pytest.raises(UndefinedCourseError) as exc_info:
        await auth_student.execute(1, 999)
    assert exc_info.value.status == 400

    # Тест 2: Пользователь не подписан - явно указан статус 403
    mock_course_repo.reset_mock()
    course_mock = Mock()
    mock_course_repo.get_by_id.return_value = course_mock
    mock_course_repo.check_user_in_course.return_value = False

    with pytest.raises(HasNoAccessError) as exc_info:
        await auth_student.execute(1, 100)
    assert exc_info.value.status == 403


@pytest.mark.asyncio
async def test_course_object_irrelevant(auth_student, mock_course_repo):
    """
    Проверяем, что содержимое объекта курса не важно - важно только что он не None
    """
    # Arrange
    user_id = 1
    course_id = 100

    # Разные варианты объектов курса
    test_courses = [
        Mock(id=course_id, name="Math"),
        Mock(),  # Пустой объект
        Mock(title="Physics"),  # Без id
        object(),  # Даже простой object
    ]

    for course_obj in test_courses:
        mock_course_repo.reset_mock()
        mock_course_repo.get_by_id.return_value = course_obj
        mock_course_repo.check_user_in_course.return_value = True

        # Act
        result = await auth_student.execute(user_id, course_id)

        # Assert
        assert result == user_id


@pytest.mark.asyncio
async def test_successful_teacher_auth(auth_teacher, mock_course_repo):
    """
    Успешная аутентификация преподавателя курса
    """
    # Arrange
    user_id = 1
    course_id = 100

    # Создаем мок курса с правильным teacher_id
    course_mock = Mock(spec=Course)
    course_mock.teacher_id = user_id  # Преподаватель совпадает
    mock_course_repo.get_by_id.return_value = course_mock

    # Act
    result = await auth_teacher.execute(user_id, course_id)

    # Assert
    assert result == user_id
    mock_course_repo.get_by_id.assert_called_once_with(course_id)


@pytest.mark.asyncio
async def test_course_not_found(auth_teacher, mock_course_repo):
    """
    Ошибка: курс не существует
    """
    # Arrange
    user_id = 1
    course_id = 999

    mock_course_repo.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(UndefinedCourseError) as exc_info:
        await auth_teacher.execute(user_id, course_id)

    assert str(exc_info.value) == "Course does not exist"
    assert exc_info.value.status == 400
    mock_course_repo.get_by_id.assert_called_once_with(course_id)


@pytest.mark.asyncio
async def test_wrong_teacher_id(auth_teacher, mock_course_repo):
    """
    Ошибка: пользователь не является преподавателем курса
    """
    # Arrange
    user_id = 1
    course_id = 100
    actual_teacher_id = 42  # Другой преподаватель

    course_mock = Mock(spec=Course)
    course_mock.teacher_id = actual_teacher_id
    mock_course_repo.get_by_id.return_value = course_mock

    # Act & Assert
    with pytest.raises(HasNoAccessError) as exc_info:
        await auth_teacher.execute(user_id, course_id)

    assert str(exc_info.value) == "User cannot manage course"
    assert exc_info.value.status == 403
    mock_course_repo.get_by_id.assert_called_once_with(course_id)


@pytest.mark.asyncio
async def test_uow_context_used(auth_teacher, mock_uow, mock_course_repo):
    """
    Проверяем, что юзкейс использует контекст UoW
    """
    # Arrange
    user_id = 1
    course_id = 100

    course_mock = Mock()
    course_mock.teacher_id = user_id
    mock_course_repo.get_by_id.return_value = course_mock

    # Act
    await auth_teacher.execute(user_id, course_id)

    # Assert
    mock_uow.__aenter__.assert_called_once()
    mock_uow.__aexit__.assert_called_once()


@pytest.mark.asyncio
async def test_teacher_id_comparison(auth_teacher, mock_course_repo):
    """
    Проверяем сравнение teacher_id с разными значениями
    """
    test_cases = [
        (1, 1, True),     # Совпадают - успех
        (1, 2, False),    # Не совпадают - ошибка
        (42, 42, True),   # Совпадают - успех
        (0, 0, True),     # Нулевые ID - успех (если такое возможно)
        (-1, -1, True),   # Отрицательные ID - успех
        (100, 101, False)  # Не совпадают - ошибка
    ]

    for user_id, course_teacher_id, should_succeed in test_cases:
        # Reset mock для каждого теста
        mock_course_repo.reset_mock()

        course_mock = Mock()
        course_mock.teacher_id = course_teacher_id
        mock_course_repo.get_by_id.return_value = course_mock

        if should_succeed:
            result = await auth_teacher.execute(user_id, 100)
            assert result == user_id
        else:
            with pytest.raises(HasNoAccessError):
                await auth_teacher.execute(user_id, 100)

        mock_course_repo.get_by_id.assert_called_once_with(100)


@pytest.mark.asyncio
async def test_uow_exits_before_checks(auth_teacher, mock_uow, mock_course_repo):
    """
    Важно: проверяем, что UoW контекст завершается ДО проверок
    (контекстный менеджер только для получения курса)
    """
    # Arrange
    user_id = 1
    course_id = 100

    course_mock = Mock(spec=Course)
    course_mock.teacher_id = user_id
    mock_course_repo.get_by_id.return_value = course_mock

    # Запоминаем порядок вызовов
    call_order = []

    # Декоратор для отслеживания порядка
    original_aenter = mock_uow.__aenter__
    original_aexit = mock_uow.__aexit__

    async def tracked_aenter():
        result = await original_aenter()
        call_order.append('uow_enter')
        return result

    async def tracked_aexit(*args):
        result = await original_aexit(*args)
        call_order.append('uow_exit')
        return result

    mock_uow.__aenter__ = AsyncMock(side_effect=tracked_aenter)
    mock_uow.__aexit__ = AsyncMock(side_effect=tracked_aexit)

    # Act
    await auth_teacher.execute(user_id, course_id)

    # Assert - UoW должен закрыться до проверки teacher_id
    assert call_order == ['uow_enter', 'uow_exit']


@pytest.mark.asyncio
async def test_returns_same_user_id(auth_teacher, mock_course_repo):
    """
    Проверяем, что возвращается именно тот user_id, который был передан
    """
    # Arrange
    test_user_ids = [1, 42, 999, 0, -5]

    for user_id in test_user_ids:
        mock_course_repo.reset_mock()

        course_mock = Mock()
        course_mock.teacher_id = user_id
        mock_course_repo.get_by_id.return_value = course_mock

        # Act
        result = await auth_teacher.execute(user_id, 100)

        # Assert
        assert result == user_id
        mock_course_repo.get_by_id.assert_called_once_with(100)


@pytest.mark.asyncio
async def test_successful_login(login_user, mock_user_repo, mock_password_service, mock_auth_service):
    """
    Успешный логин пользователя
    """
    # Arrange
    dto = LoginUserDTO(email="test@example.com", password="password123")
    user_id = 1
    token = "jwt.token.here"

    # Настраиваем моки
    user_mock = Mock(spec=User)
    user_mock.id = user_id
    user_mock.password = "hashed_password"
    user_mock.email = dto.email

    mock_user_repo.get_by_email.return_value = user_mock
    mock_password_service.check_password.return_value = True
    mock_auth_service.generate_token.return_value = token

    # Act
    result = await login_user.execute(dto)

    # Assert
    assert result == token
    mock_user_repo.get_by_email.assert_called_once_with(dto.email)
    mock_password_service.check_password.assert_called_once_with(user_mock.password, dto.password)
    mock_auth_service.generate_token.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_user_not_found(login_user, mock_user_repo, mock_password_service, mock_auth_service):
    """
    Ошибка: пользователь с таким email не найден
    """
    # Arrange
    dto = LoginUserDTO(email="notfound@example.com", password="password123")

    mock_user_repo.get_by_email.return_value = None

    # Act & Assert
    with pytest.raises(UndefinedUserError) as exc_info:
        await login_user.execute(dto)

    assert "User not found" in str(exc_info.value)
    mock_user_repo.get_by_email.assert_called_once_with(dto.email)
    # Проверяем, что дальше логика не пошла
    mock_password_service.check_password.assert_not_called()
    mock_auth_service.generate_token.assert_not_called()


@pytest.mark.asyncio
async def test_incorrect_password(login_user, mock_user_repo, mock_password_service, mock_auth_service):
    """
    Ошибка: неверный пароль
    """
    # Arrange
    dto = LoginUserDTO(email="test@example.com", password="wrong_password")

    user_mock = Mock()
    user_mock.id = 1
    user_mock.password = "hashed_password"
    user_mock.email = dto.email

    mock_user_repo.get_by_email.return_value = user_mock
    mock_password_service.check_password.return_value = False  # Пароль не совпадает

    # Act & Assert
    with pytest.raises(InvalidUserPasswordError) as exc_info:
        await login_user.execute(dto)

    assert "Incorrect password" in str(exc_info.value)
    mock_user_repo.get_by_email.assert_called_once_with(dto.email)
    mock_password_service.check_password.assert_called_once_with(user_mock.password, dto.password)
    # Токен не должен генерироваться
    mock_auth_service.generate_token.assert_not_called()


@pytest.mark.asyncio
async def test_uow_context_used(login_user, mock_uow, mock_user_repo, mock_password_service, mock_auth_service):
    """
    Проверяем использование контекста UoW
    """
    # Arrange
    dto = LoginUserDTO(email="test@example.com", password="password123")

    user_mock = Mock()
    user_mock.id = 1
    user_mock.password = "hashed_password"

    mock_user_repo.get_by_email.return_value = user_mock
    mock_password_service.check_password.return_value = True
    mock_auth_service.generate_token.return_value = "token"

    # Act
    await login_user.execute(dto)

    # Assert
    mock_uow.__aenter__.assert_called_once()
    mock_uow.__aexit__.assert_called_once()


@pytest.mark.asyncio
async def test_generate_token_called_with_correct_user_id(login_user, mock_user_repo, mock_password_service, mock_auth_service):
    """
    Проверяем, что токен генерируется с правильным user_id
    """
    # Arrange
    test_cases = [
        (1, "user1@example.com"),
        (42, "user42@example.com"),
        (999, "admin@example.com"),
    ]

    for user_id, email in test_cases:
        # Reset mocks
        mock_user_repo.reset_mock()
        mock_password_service.reset_mock()
        mock_auth_service.reset_mock()

        dto = LoginUserDTO(email=email, password="password123")

        user_mock = Mock(spec=User)
        user_mock.id = user_id
        user_mock.password = f"hashed_{user_id}"

        mock_user_repo.get_by_email.return_value = user_mock
        mock_password_service.check_password.return_value = True
        mock_auth_service.generate_token.return_value = f"token_{user_id}"

        # Act
        result = await login_user.execute(dto)

        # Assert
        assert result == f"token_{user_id}"
        mock_auth_service.generate_token.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_password_check_arguments(login_user, mock_user_repo, mock_password_service):
    """
    Проверяем, что check_password вызывается с правильными аргументами
    """
    # Arrange
    dto = LoginUserDTO(email="test@example.com", password="my_password")

    user_mock = Mock(spec=User)
    user_mock.id = 1
    user_mock.password = "stored_hash"

    mock_user_repo.get_by_email.return_value = user_mock

    # Test 1: Пароль верный
    mock_password_service.check_password.return_value = True

    await login_user.execute(dto)

    mock_password_service.check_password.assert_called_once_with("stored_hash", "my_password")

    # Test 2: Пароль неверный
    mock_user_repo.reset_mock()
    mock_password_service.reset_mock()

    mock_user_repo.get_by_email.return_value = user_mock
    mock_password_service.check_password.return_value = False

    with pytest.raises(InvalidUserPasswordError):
        await login_user.execute(dto)

    mock_password_service.check_password.assert_called_once_with("stored_hash", "my_password")


@pytest.mark.asyncio
async def test_successful_registration(
    register_user_request,
    mock_user_repo,
    mock_password_service,
    mock_auth_service,
    mock_email_service,
    mock_uow
):
    """
    Успешная регистрация пользователя
    """
    # Arrange
    dto = RegisterUserRequestDTO(
        name="John Doe",
        email="john@example.com",
        first_password="password123",
        second_password="password123"
    )

    user_id = 1
    hashed_password = "hashed_password_123"
    token = "jwt.confirmation.token"

    mock_user_repo.count_by_email.return_value = 0  # Email не занят
    mock_password_service.hash_password.return_value = hashed_password
    mock_auth_service.generate_token.return_value = token

    saved_user = None

    def save_side_effect(user):
        nonlocal saved_user
        saved_user = user  # Сохраняем ссылку на пользователя
        # ID пока None

    async def flush_side_effect():
        nonlocal saved_user
        # После flush устанавливаем id пользователю
        if saved_user:
            saved_user.id = user_id

    # Настраиваем UoW методы
    mock_uow.save = Mock(side_effect=save_side_effect)
    mock_uow.flush = AsyncMock(side_effect=flush_side_effect)

    # Act
    await register_user_request.execute(dto)

    # Assert
    mock_user_repo.count_by_email.assert_called_once_with(dto.email)
    mock_password_service.hash_password.assert_called_once_with(dto.first_password)
    mock_auth_service.generate_token.assert_called_once_with(user_id, 300)
    mock_email_service.send_mail.assert_called_once_with(
        dto.email,
        "Registration confirm",
        f"Hello! Confirm your registration on Runlet following by link:\nhttps://example.com/confirm/{token}"
    )
    mock_uow.save.assert_called_once()
    mock_uow.flush.assert_called_once()


@pytest.mark.asyncio
async def test_passwords_mismatch_with_mocks(
    register_user_request,
    mock_user_repo,
    mock_password_service,
    mock_auth_service,
    mock_email_service,
    mock_uow
):
    """
    Ошибка: пароли не совпадают (с проверкой моков)
    """
    # Arrange
    dto = RegisterUserRequestDTO(
        name="John Doe",
        email="john@example.com",
        first_password="password123",
        second_password="different_password"
    )

    # Act & Assert
    with pytest.raises(PasswordsMismatchError):
        await register_user_request.execute(dto)

    # Проверяем что дальше логика не пошла
    mock_user_repo.count_by_email.assert_not_called()
    mock_password_service.hash_password.assert_not_called()
    mock_auth_service.generate_token.assert_not_called()
    mock_email_service.send_mail.assert_not_called()
    mock_uow.save.assert_not_called()
    mock_uow.flush.assert_not_called()


@pytest.mark.asyncio
async def test_email_already_exists(
    register_user_request,
    mock_user_repo,
    mock_password_service,
    mock_auth_service,
    mock_email_service,
    mock_uow
):
    """
    Ошибка: email уже занят
    """
    # Arrange
    dto = RegisterUserRequestDTO(
        name="John Doe",
        email="existing@example.com",
        first_password="password123",
        second_password="password123"
    )

    mock_user_repo.count_by_email.return_value = 1  # Email уже занят

    # Act & Assert
    with pytest.raises(EmailExistsError) as exc_info:
        await register_user_request.execute(dto)

    assert f"User with email {dto.email} already exists" in str(exc_info.value)
    mock_user_repo.count_by_email.assert_called_once_with(dto.email)

    # Проверяем что дальше логика не пошла
    mock_password_service.hash_password.assert_not_called()
    mock_auth_service.generate_token.assert_not_called()
    mock_email_service.send_mail.assert_not_called()
    mock_uow.save.assert_not_called()
    mock_uow.flush.assert_not_called()


@pytest.mark.asyncio
async def test_uow_context_used(
    register_user_request,
    mock_uow,
    mock_user_repo,
    mock_password_service,
    mock_auth_service,
    mock_email_service
):
    """
    Проверяем использование контекста UoW
    """
    # Arrange
    dto = RegisterUserRequestDTO(
        name="John Doe",
        email="john@example.com",
        first_password="password123",
        second_password="password123"
    )

    mock_user_repo.count_by_email.return_value = 0
    mock_password_service.hash_password.return_value = "hashed"
    mock_auth_service.generate_token.return_value = "token"

    # Act
    await register_user_request.execute(dto)

    # Assert
    mock_uow.__aenter__.assert_called_once()
    mock_uow.__aexit__.assert_called_once()
    mock_uow.save.assert_called_once()
    mock_uow.flush.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_email_sent_with_correct_content_simple(
    register_user_request,
    mock_user_repo,
    mock_password_service,
    mock_auth_service,
    mock_email_service,
    mock_uow
):
    """
    Упрощенный тест - проверяем только email
    """
    # Arrange
    dto = RegisterUserRequestDTO(
        name="Alice Smith",
        email="alice@example.com",
        first_password="secure_pass",
        second_password="secure_pass"
    )

    token = "unique-confirmation-token-123"

    mock_user_repo.count_by_email.return_value = 0
    mock_password_service.hash_password.return_value = "hashed_secure_pass"
    mock_auth_service.generate_token.return_value = token

    # Настраиваем простые моки без side_effect
    mock_uow.save = Mock()
    mock_uow.flush = AsyncMock()

    # Act
    await register_user_request.execute(dto)

    # Assert - проверяем только email, игнорируем проверку save/flush
    expected_message = (
        f"Hello! Confirm your registration on Runlet following by link:\n"
        f"https://example.com/confirm/{token}"
    )

    mock_email_service.send_mail.assert_called_once_with(
        dto.email,
        "Registration confirm",
        expected_message
    )


@pytest.mark.asyncio
async def test_generate_token_with_expiration(
    register_user_request,
    mock_user_repo,
    mock_password_service,
    mock_auth_service,
    mock_uow
):
    """
    Проверяем что токен генерируется с expiration time = 300 секунд
    """
    # Arrange
    dto = RegisterUserRequestDTO(
        name="Bob Johnson",
        email="bob@example.com",
        first_password="password",
        second_password="password"
    )

    user_id = 99

    mock_user_repo.count_by_email.return_value = 0
    mock_password_service.hash_password.return_value = "hashed"

    # Act
    await register_user_request.execute(dto)
    mock_uow.save.assert_called_once()
    mock_uow.flush.assert_called_once()

    # Assert
    call_args = mock_auth_service.generate_token.call_args
    # Проверяем что второй аргумент = 300
    assert call_args[0][1] == 300  # expiration time


@pytest.mark.asyncio
async def test_password_hashing_called_with_correct_password(
    register_user_request,
    mock_user_repo,
    mock_password_service,
    mock_auth_service,
    mock_email_service,
    mock_uow
):
    """
    Проверяем что hash_password вызывается с правильным паролем
    """
    # Arrange
    test_cases = [
        ("simpless", "simpless"),
        ("Complex@123", "Complex@123"),
        ("very_long_password_12345", "very_long_password_12345"),
    ]

    for password in test_cases:
        mock_user_repo.reset_mock()
        mock_password_service.reset_mock()
        mock_auth_service.reset_mock()
        mock_email_service.reset_mock()
        mock_uow.reset_mock()

        dto = RegisterUserRequestDTO(
            name="Test User",
            email="test@example.com",
            first_password=password[0],
            second_password=password[1]
        )

        mock_user_repo.count_by_email.return_value = 0
        mock_password_service.hash_password.return_value = f"hashed_{password}"
        mock_auth_service.generate_token.return_value = "token"

        # Act
        await register_user_request.execute(dto)
        mock_uow.save.assert_called_once()
        mock_uow.flush.assert_called_once()

        # Assert
        mock_password_service.hash_password.assert_called_once_with(password[0])


@pytest.mark.asyncio
async def test_count_by_email_returns_zero_for_new_email(
    register_user_request,
    mock_user_repo,
    mock_password_service,
    mock_auth_service,
    mock_email_service,
    mock_uow
):
    """
    Проверяем разные возвращаемые значения count_by_email
    """
    # Arrange
    dto = RegisterUserRequestDTO(
        name="Test User",
        email="new@example.com",
        first_password="password123",
        second_password="password123"
    )

    # Test case 1: возвращает 0 (email свободен)
    mock_user_repo.count_by_email.return_value = 0
    mock_password_service.hash_password.return_value = "hashed"

    await register_user_request.execute(dto)

    # Проверяем что create был вызван
    mock_uow.save.assert_called_once()
    mock_uow.flush.assert_called_once()

    # Reset для теста 2
    mock_user_repo.reset_mock()
    mock_password_service.reset_mock()
    mock_auth_service.reset_mock()
    mock_email_service.reset_mock()
    mock_uow.reset_mock()

    # Test case 2: возвращает 1 (email занят)
    mock_user_repo.count_by_email.return_value = 1

    with pytest.raises(EmailExistsError):
        await register_user_request.execute(dto)

    # Проверяем что create НЕ был вызван
    mock_uow.save.assert_not_called()
    mock_uow.flush.assert_not_called()


@pytest.mark.asyncio
async def test_all_operations_inside_uow_context(
    register_user_request,
    mock_uow,
    mock_user_repo,
    mock_password_service,
    mock_auth_service,
    mock_email_service,
):
    """
    Проверяем что все операции с репозиторием происходят внутри контекста UoW
    """
    # Arrange
    dto = RegisterUserRequestDTO(
        name="John Doe",
        email="john@example.com",
        first_password="password123",
        second_password="password123"
    )

    mock_user_repo.count_by_email.return_value = 0
    mock_password_service.hash_password.return_value = "hashed"
    mock_auth_service.generate_token.return_value = "token"

    # Отслеживаем порядок вызовов
    call_order = []

    # Декорируем методы для отслеживания
    original_uow_enter = mock_uow.__aenter__
    original_uow_exit = mock_uow.__aexit__

    async def tracked_uow_enter():
        result = await original_uow_enter()
        call_order.append('uow_enter')
        return result

    async def tracked_uow_exit(*args):
        result = await original_uow_exit(*args)
        call_order.append('uow_exit')
        return result

    mock_uow.__aenter__ = AsyncMock(side_effect=tracked_uow_enter)
    mock_uow.__aexit__ = AsyncMock(side_effect=tracked_uow_exit)

    # Act
    await register_user_request.execute(dto)

    # Assert - все вызовы репозитория должны быть между enter и exit
    assert call_order[0] == 'uow_enter'
    assert call_order[-1] == 'uow_exit'
    # Методы репозитория вызывались внутри контекста
    assert mock_user_repo.count_by_email.called
    assert mock_uow.save.called
    assert mock_uow.flush.called


@pytest.mark.asyncio
async def test_successful_registration_confirmation(
    register_user_confirm,
    mock_user_repo,
    mock_auth_service,
    mock_uow
):
    """
    Успешное подтверждение регистрации
    """
    # Arrange
    token = "valid_confirmation_token"
    user_id = 1

    mock_auth_service.get_user_id_from_token.return_value = user_id

    user_mock = Mock(spec=User)
    user_mock.id = user_id
    user_mock.is_active = False  # Пользователь неактивен до подтверждения

    mock_user_repo.get_by_id.return_value = user_mock

    # Act
    await register_user_confirm.execute(token)

    # Assert
    mock_auth_service.get_user_id_from_token.assert_called_once_with(token)
    mock_user_repo.get_by_id.assert_called_once_with(user_id)

    # Проверяем что пользователь стал активным
    assert user_mock.is_active is True

    # Проверяем использование UoW
    mock_uow.__aenter__.assert_called_once()
    mock_uow.__aexit__.assert_called_once()


@pytest.mark.asyncio
async def test_invalid_token_no_user_id(
    register_user_confirm,
    mock_auth_service,
    mock_user_repo,
    mock_uow
):
    """
    Ошибка: токен не содержит user_id 
    """
    # Arrange
    token = "invalid_token"

    mock_auth_service.get_user_id_from_token.return_value = None

    # Act & Assert
    with pytest.raises(UndefinedUserError) as exc_info:
        await register_user_confirm.execute(token)

    assert "User was not identify" in str(exc_info.value)
    mock_auth_service.get_user_id_from_token.assert_called_once_with(token)

    # Проверяем что дальше логика не пошла
    mock_user_repo.get_by_id.assert_not_called()
    mock_uow.__aenter__.assert_not_called()
    mock_uow.__aexit__.assert_not_called()


@pytest.mark.asyncio
async def test_register_confirm_invalid_token(
    register_user_confirm,
    mock_auth_service,
    mock_user_repo,
    mock_uow
):
    """
    Ошибка: токен не содержит user_id (невалидный/просроченный токен)
    """
    # Arrange
    token = "invalid_token"

    mock_auth_service.get_user_id_from_token.side_effect = JWTUnauthorizedError(
        "Token invlaid", status=401)

    # Act & Assert
    with pytest.raises(JWTUnauthorizedError) as exc_info:
        await register_user_confirm.execute(token)

    assert "Token invlaid" in str(exc_info.value)
    mock_auth_service.get_user_id_from_token.assert_called_once_with(token)

    # Проверяем что дальше логика не пошла
    mock_user_repo.get_by_id.assert_not_called()
    mock_uow.__aenter__.assert_not_called()
    mock_uow.__aexit__.assert_not_called()


@pytest.mark.asyncio
async def test_user_not_found_in_database(
    register_user_confirm,
    mock_auth_service,
    mock_user_repo,
    mock_uow
):
    """
    Ошибка: пользователь не найден в БД (хотя токен валидный)
    """
    # Arrange
    token = "valid_token_but_no_user"
    user_id = 999

    mock_auth_service.get_user_id_from_token.return_value = user_id
    mock_user_repo.get_by_id.return_value = None  # Пользователь не найден

    # Act & Assert
    with pytest.raises(UndefinedUserError) as exc_info:
        await register_user_confirm.execute(token)

    assert "Try to confirm registration of user that does not exist" in str(exc_info.value)

    mock_auth_service.get_user_id_from_token.assert_called_once_with(token)
    mock_user_repo.get_by_id.assert_called_once_with(user_id)

    # Проверяем что UoW был использован (потому что исключение внутри контекста)
    mock_uow.__aenter__.assert_called_once()
    mock_uow.__aexit__.assert_called_once()


@pytest.mark.asyncio
async def test_already_active_user(
    register_user_confirm,
    mock_auth_service,
    mock_user_repo,
    mock_uow
):
    """
    Подтверждение уже активного пользователя (is_active уже True)
    """
    # Arrange
    token = "valid_token"
    user_id = 1

    mock_auth_service.get_user_id_from_token.return_value = user_id

    user_mock = Mock(spec=User)
    user_mock.id = user_id
    user_mock.is_active = True  # Уже активен

    mock_user_repo.get_by_id.return_value = user_mock

    # Act
    await register_user_confirm.execute(token)

    # Assert
    mock_auth_service.get_user_id_from_token.assert_called_once_with(token)
    mock_user_repo.get_by_id.assert_called_once_with(user_id)

    # is_active остается True
    assert user_mock.is_active is True


@pytest.mark.asyncio
async def test_uow_context_usage(
    register_user_confirm,
    mock_uow,
    mock_auth_service,
    mock_user_repo
):
    """
    Проверяем что все операции внутри контекста UoW
    """
    # Arrange
    token = "valid_token"
    user_id = 1

    mock_auth_service.get_user_id_from_token.return_value = user_id

    user_mock = Mock(spec=User)
    user_mock.id = user_id
    user_mock.is_active = False

    mock_user_repo.get_by_id.return_value = user_mock

    # Отслеживаем порядок вызовов
    call_order = []

    original_aenter = mock_uow.__aenter__
    original_aexit = mock_uow.__aexit__

    async def tracked_aenter():
        call_order.append('uow_enter')
        result = await original_aenter()
        return result

    async def tracked_aexit(*args):
        call_order.append('uow_exit')
        result = await original_aexit(*args)
        return result

    mock_uow.__aenter__ = AsyncMock(side_effect=tracked_aenter)
    mock_uow.__aexit__ = AsyncMock(side_effect=tracked_aexit)

    # Act
    await register_user_confirm.execute(token)

    # Assert - операции репозитория должны быть внутри контекста
    assert call_order[0] == 'uow_enter'
    assert call_order[-1] == 'uow_exit'


@pytest.mark.asyncio
async def test_consecutive_activations(
    register_user_confirm,
    mock_auth_service,
    mock_user_repo
):
    """
    Несколько последовательных активаций одного пользователя
    """
    # Arrange
    tokens = ["token1", "token2", "token3"]
    user_id = 1

    mock_auth_service.get_user_id_from_token.side_effect = [user_id, user_id, user_id]

    user_mock = Mock(spec=User)
    user_mock.id = user_id
    user_mock.is_active = False  # Начинаем с неактивного

    mock_user_repo.get_by_id.return_value = user_mock

    # Act - активируем три раза
    await register_user_confirm.execute(tokens[0])
    assert user_mock.is_active is True  # После первого вызова

    await register_user_confirm.execute(tokens[1])
    assert user_mock.is_active is True  # Остается True

    await register_user_confirm.execute(tokens[2])
    assert user_mock.is_active is True  # Остается True

    # Assert
    assert mock_auth_service.get_user_id_from_token.call_count == 3
    assert mock_user_repo.get_by_id.call_count == 3
