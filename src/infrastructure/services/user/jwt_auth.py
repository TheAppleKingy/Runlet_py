import jwt
import time

from typing import Optional

from .exceptions import JWTUnauthorizedError

from src.logger import logger


class JWTAuthenticationService:
    def __init__(
        self,
        exp_time: int,
        secret: str
    ):
        self._exp = exp_time
        self._secret = secret

    def generate_token(self, user_id: int, exp: Optional[int] = None) -> str:
        res = time.time()
        res += exp or self._exp

        return jwt.encode(
            payload={
                "user_id": user_id,
                "exp": int(res),
            },
            key=self._secret,
            algorithm="HS256"
        )

    def get_user_id_from_token(self, token: str) -> Optional[int]:
        try:
            payload = jwt.decode(token, self._secret, ["HS256"])
            return payload.get("user_id")
        except jwt.InvalidTokenError:
            raise JWTUnauthorizedError("Token invlaid", status=401)
