from dataclasses import dataclass, field
from .user import User


@dataclass
class Tag:
    name: str
    course_id: int
    students: list[User] = field(default_factory=list, init=False)
    id: int = field(default=None, init=False)  # type: ignore
