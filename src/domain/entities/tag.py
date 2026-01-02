from dataclasses import dataclass, field


@dataclass(frozen=True)
class Tag:
    id: int = field(default=None)
    name: str = field(default="")
