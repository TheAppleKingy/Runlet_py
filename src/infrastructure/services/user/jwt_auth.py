import jwt
import time

from typing import Optional

from .exceptions import JWTUnauthorizedError


class JWTAuthenticationService:
    def __init__(self, reg_confirm_url: str, secret: str, exp: int):
        self.reg_confirm_url = reg_confirm_url
        self.secret = secret
        self.exp = exp

    def generate_token(self, user_id: int, additional: dict = {}) -> str:
        exp = time.time() + self.exp
        return jwt.encode(
            payload={
                "user_id": user_id,
                "exp": int(exp),
                **additional
            },
            key=self.secret,
            algorithm="HS256"
        )

    def get_user_id_from_token(self, token: str) -> Optional[int]:
        try:
            payload = jwt.decode(token, self.secret, ["HS256"])
            return payload.get("user_id")
        except jwt.InvalidTokenError:
            raise JWTUnauthorizedError("Token invlaid", status=401)
