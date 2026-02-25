from dataclasses import dataclass, field


@dataclass
class User:
    email: str
    password: str
    name: str = ""
    is_active: bool = field(default=False, init=False)
    id: int = field(default=None, init=False)  # type: ignore
