from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class Tag:
    def __init__(self, id_: int = None, name: str = "", users: list[User] = None):
        self.id = id_
        self.name = name
        self.users = users if users is not None else []
