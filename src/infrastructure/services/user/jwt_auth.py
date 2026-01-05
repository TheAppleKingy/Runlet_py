import jwt
import time

from typing import Optional

from infrastructure.configs import app_conf
from .exceptions import JWTUnauthorizedError


class JWTAuthenticationService:
    def generate_token(self, user_id: int, additional: dict = {}) -> str:
        exp = time.time() + app_conf.token_expire_time
        return jwt.encode(
            payload={
                "user_id": user_id,
                "exp": int(exp),
                **additional
            },
            key=app_conf.secret,
            algorithm="HS256"
        )

    def get_user_id_from_token(self, token: str) -> Optional[int]:
        try:
            payload = jwt.decode(token, app_conf.secret, ["HS256"])
            return payload.get("user_id")
        except jwt.InvalidTokenError:
            raise JWTUnauthorizedError("Token invlaid")
