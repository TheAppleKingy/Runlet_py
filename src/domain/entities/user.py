from dataclasses import dataclass, field
from typing import Optional

from .tag import Tag


@dataclass
class User:
    id: Optional[int] = None
    email: str = field(default="")
    password: str = field(default="")
    tags: list[Tag] = field(default_factory=list, init=False)
