from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction
from src.application.interfaces.uow import UoWInterface, T
from src.logger import logger


class AlchemyUoW(UoWInterface):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._auto: bool = True
        self._t: AsyncSessionTransaction = None

    async def __aenter__(self) -> Self:
        # logger.critical(f"{self._session.in_transaction()}, {self._session.get_transaction()}")
        self._t = await self._session.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        async def handle_transaction():
            if self._t:
                if exc_type is not None:
                    await self._t.rollback()
                else:
                    await self._t.commit()

        if self._auto:
            await handle_transaction()
        self._t = None
        self._auto = True
        return False

    def __call__(self, *_):
        """
        Calling __call__ sets attribute _auto to False an that means that
        you start manage transaction manually(commit, rollback)
        """
        self._auto = False
        return self

    async def commit(self) -> None:
        if self._t:
            await self._t.commit()

    async def rollback(self) -> None:
        if self._t:
            await self._t.rollback()

    async def flush(self) -> None:
        return await self._session.flush()

    def save(self, *ents: T):
        return self._session.add_all(ents)

    def in_transaction(self) -> bool:
        return self._session.in_transaction()
