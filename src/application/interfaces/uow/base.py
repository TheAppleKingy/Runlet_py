from typing import Self, Protocol


class ReadOnlyUoWInterface(Protocol):
    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...


class ReadWriteUoWInterface(ReadOnlyUoWInterface):
    _auto_commit: bool

    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
