from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .course import Course

from .tag import Tag


class User:
    def __init__(
        self,
        email: str,
        password: str,
        name: str = "",
        id_: int = None,
        tags: list[Tag] = None,
        courses: list[Course] = None,
    ):
        self.id = id_
        self.name = name
        self.email = email
        self.password = password
        self.tags = tags if tags is not None else []
        self.courses = courses if courses is not None else []
