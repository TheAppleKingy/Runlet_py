from typing import Optional

from sqlalchemy import select, func, insert
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import User


class AlchemyUserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        return await self._session.scalar(select(User).where(User.id == user_id))

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self._session.scalar(select(User).where(User.email == email))

    async def count_by_email(self, email: str) -> int:
        return await self._session.scalar(select(func.count(User.id)).where(User.email == email)) or 0

    async def create(self, name: str, email: str, password: str) -> User:
        res = await self._session.execute(insert(User).values(name=name, email=email, password=password).returning(User))
        return res.scalar()
