from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession
from domain.interfaces.repositories import UserRepositoryInterface


class ReadUserUow:
    def __init__(self, session: AsyncSession, user_repo: UserRepositoryInterface):
        self._session = session

    async def __aenter__(self) -> Self:
        transaction = await self._session.begin()
