from src.infrastructure.services.user import JWTAuthenticationService
from src.infrastructure.services.user.exceptions import JWTUnauthorizedError
import jwt
import time
import pytest


def test_generate_token_contains_user_id():
    """Токен должен содержать переданный user_id"""
    service = JWTAuthenticationService(exp_time=3600, secret="test_secret_123")
    user_id = 42

    token = service.generate_token(user_id)
    decoded_id = service.get_user_id_from_token(token)

    assert decoded_id == user_id


def test_generate_token_default_expiration():
    """Должна использоваться дефолтная экспирация из __init__"""
    exp_time = 500
    service = JWTAuthenticationService(exp_time=exp_time, secret="test")

    token = service.generate_token(1)

    # Декодируем без проверки exp
    payload = jwt.decode(token, "test", ["HS256"], options={"verify_exp": False})

    expected_exp = int(time.time() + exp_time)
    # Допуск ±2 секунды
    assert abs(payload["exp"] - expected_exp) <= 2


def test_generate_token_custom_expiration():
    """Должна работать кастомная экспирация"""
    service = JWTAuthenticationService(exp_time=1000, secret="test")
    custom_exp = 200

    token = service.generate_token(1, exp=custom_exp)

    payload = jwt.decode(token, "test", ["HS256"], options={"verify_exp": False})
    expected_exp = int(time.time() + custom_exp)
    assert abs(payload["exp"] - expected_exp) <= 2


def test_expired_token_raises_error():
    """Просроченный токен должен вызывать JWTUnauthorizedError"""
    service = JWTAuthenticationService(exp_time=3600, secret="test")

    # Создаем токен с истекшим временем
    expired_token = jwt.encode(
        payload={"user_id": 1, "exp": int(time.time() - 10)},
        key="test",
        algorithm="HS256"
    )

    with pytest.raises(JWTUnauthorizedError) as exc_info:
        service.get_user_id_from_token(expired_token)

    assert "Token invlaid" in str(exc_info.value)
    assert exc_info.value.status == 401


def test_wrong_secret_raises_error():
    """Токен с неправильным секретом должен вызывать ошибку"""
    service1 = JWTAuthenticationService(exp_time=3600, secret="secret1")
    service2 = JWTAuthenticationService(exp_time=3600, secret="secret2")

    token = service1.generate_token(1)

    with pytest.raises(JWTUnauthorizedError) as exc_info:
        service2.get_user_id_from_token(token)  # Пробуем декодировать с другим секретом


def test_malformed_token_raises_error():
    """Кривой токен должен вызывать ошибку"""
    service = JWTAuthenticationService(exp_time=3600, secret="test")

    with pytest.raises(JWTUnauthorizedError):
        service.get_user_id_from_token("not.a.valid.token")


def test_token_without_user_id_returns_none():
    """Токен без user_id должен возвращать None"""
    service = JWTAuthenticationService(exp_time=3600, secret="test")

    # Создаем токен без user_id
    token_without_user_id = jwt.encode(
        payload={"exp": int(time.time() + 3600)},
        key="test",
        algorithm="HS256"
    )

    result = service.get_user_id_from_token(token_without_user_id)
    assert result is None


def test_token_with_extra_fields():
    """Токен с дополнительными полями должен нормально декодироваться"""
    service = JWTAuthenticationService(exp_time=3600, secret="test")

    # Создаем токен с дополнительными полями
    extra_token = jwt.encode(
        payload={
            "user_id": 1,
            "exp": int(time.time() + 3600),
            "extra_field": "some_value",
            "another_field": 123
        },
        key="test",
        algorithm="HS256"
    )

    result = service.get_user_id_from_token(extra_token)
    assert result == 1


def test_same_user_different_tokens():
    """Токены для одного пользователя, сгенерированные в разное время, должны быть разными"""
    service = JWTAuthenticationService(exp_time=3600, secret="test")

    token1 = service.generate_token(1)
    time.sleep(0.2)  # Ждем немного
    token2 = service.generate_token(1)

    assert token1 != token2


def test_different_secrets_create_different_tokens():
    """Сервисы с разными секретами должны создавать разные токены для одного user_id"""
    service1 = JWTAuthenticationService(exp_time=3600, secret="secret1")
    service2 = JWTAuthenticationService(exp_time=3600, secret="secret2")

    token1 = service1.generate_token(1)
    token2 = service2.generate_token(1)

    assert token1 != token2, "Токены с разными секретами должны быть разными"

    # Каждый токен должен декодироваться только своим сервисом
    assert service1.get_user_id_from_token(token1) == 1
    assert service2.get_user_id_from_token(token2) == 1


def test_init_with_different_exp_times():
    """Сервисы с разным временем жизни должны работать корректно"""
    service_short = JWTAuthenticationService(exp_time=60, secret="test")  # 1 минута
    service_long = JWTAuthenticationService(exp_time=86400, secret="test")  # 1 день

    token_short = service_short.generate_token(1)
    token_long = service_long.generate_token(1)

    payload_short = jwt.decode(token_short, "test", ["HS256"], options={"verify_exp": False})
    payload_long = jwt.decode(token_long, "test", ["HS256"], options={"verify_exp": False})

    # Проверяем что exp разные
    assert payload_short["exp"] < payload_long["exp"]
