from typing import Optional, NewType, TypeVar, Protocol


AuthenticatedUserId = NewType("AuthenticatedUserId", int)
AuthenticatedStudentId = NewType("AuthenticatedStudentId", int)
AuthenticatedTeacherId = NewType("AuthenticatedTeacherId", int)
AuthenticatedNotStrictlyUserId = Optional[AuthenticatedUserId]


class HasId(Protocol):
    id: int


class HasNameType(Protocol):
    name: str


Named = TypeVar("Named", bound=HasNameType)
DomainEnt = TypeVar("DomainEnt", bound=HasId)
