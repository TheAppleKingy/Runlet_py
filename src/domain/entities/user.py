from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass, field
if TYPE_CHECKING:
    from .course import Course
    from .tag import Tag


@dataclass
class User:
    email: str
    password: str
    name: str = ""
    is_active: bool = field(default=False, init=False)
    id: int = field(default=None, init=False)
    tags: list[Tag] = field(default_factory=list, init=None)
    courses: list[Course] = field(default_factory=list, init=False)
