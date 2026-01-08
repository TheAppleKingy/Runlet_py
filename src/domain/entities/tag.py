from dataclasses import dataclass, field
from .user import User


@dataclass
class Tag:
    name: str
    id: int = field(default=None, init=False)
    users: list[User] = field(default_factory=list)
