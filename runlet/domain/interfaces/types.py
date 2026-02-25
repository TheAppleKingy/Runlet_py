from typing import Optional, NewType, TypeVar, Protocol, Literal


AuthenticatedUserId = NewType("AuthenticatedUserId", int)
AuthenticatedStudentId = NewType("AuthenticatedStudentId", int)
AuthenticatedTeacherId = NewType("AuthenticatedTeacherId", int)
AuthenticatedNotStrictlyUserId = Optional[AuthenticatedUserId]


class HasNameType(Protocol):
    name: str


Named = TypeVar("Named", bound=HasNameType)
DomainEnt = TypeVar("DomainEnt")


CodeName = Literal[
    "py",
    "go",
    "js",
    "cpp",
    "cs"
]
