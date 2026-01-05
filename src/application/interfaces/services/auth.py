from typing import Protocol, Optional


class AuthenticationServiceInterface(Protocol):
    reg_confirm_url: str

    def generate_token(self, user_id: int, additional: dict = {}) -> str: ...
    def get_user_id_from_token(self, token: str) -> Optional[int]: ...
