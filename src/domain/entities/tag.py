from dataclasses import dataclass, field
from enum import Enum

from .user import User


class DefautTagType(Enum):
    WAITING_FOR_SUBSCRIBE = "Ожидают зачисления"


@dataclass
class Tag:
    name: str
    course_id: int
    students: list[User] = field(default_factory=list, init=False)
    id: int = field(default=None, init=False)  # type: ignore
