from typing import Self, Protocol, TypeVar


class HasId:
    id: int


T = TypeVar("DomainEnt", bound=HasId)


class UoWInterface(Protocol):
    """
    UoW that manages transaction starting when enter the context. Management of transaction going on automatically
    that mean commit will be called after exit from context or rollback if exception will be raised inside context.
    To manage transaction manually enter the context via __call__() method but keep attention in this case.
    """

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...

    def __call__(self, *_) -> Self:
        """
        :return: UoW instance that will NOT manage current transaction automatically. Commit or rollback should
        be called manually
        :rtype: Self
        """

    def save(self, *ents: T) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
    async def flush(self) -> None: ...
    def in_transaction(self) -> bool: ...
