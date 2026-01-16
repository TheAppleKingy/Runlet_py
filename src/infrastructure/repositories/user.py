from typing import Optional

from sqlalchemy import select, func, insert

from src.domain.entities import User
from src.application.interfaces.repositories import UserRepositoryInterface
from src.infrastructure.db.tables import users
from .base import BaseAlchemyRepository


class AlchemyUserRepository(BaseAlchemyRepository, UserRepositoryInterface):
    async def get_by_id(self, user_id: int) -> Optional[User]:
        return await self._session.scalar(select(User).where(User.id == user_id))  # type: ignore

    async def get_by_ids(self, user_ids: list[int]) -> list[User]:
        res = await self._session.scalars(select(User).where(users.c.id.in_(user_ids)))
        return res.all()  # type: ignore

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self._session.scalar(select(User).where(User.email == email))  # type: ignore

    async def count_by_email(self, email: str) -> int:
        return await self._session.scalar(select(func.count(User.id)).where(User.email == email)) or 0 # type: ignore

    async def create(self, name: str, email: str, password: str) -> User:
        res = await self._session.execute(insert(User).values(name=name, email=email, password=password).returning(User))
        return res.scalar()  # type: ignore
