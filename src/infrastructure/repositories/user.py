from typing import Optional

from sqlalchemy import select, func

from src.domain.entities import User
from src.application.interfaces.repositories import UserRepositoryInterface
from src.infrastructure.db.tables import (
    users,
    users_tags,
    users_courses
)
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
        # type: ignore
        return await self._session.scalar(select(func.count(User.id)).where(User.email == email)) or 0

    async def find_by_name(self, course_id: int, namelike: str, tag_id: Optional[int] = None) -> list[User]:
        ilike_clause = users.c.name.ilike(f"{namelike}%")
        if tag_id:
            stmt = (
                select(User).join(users_tags, users_tags.c.user_id == User.id)
                .where(users_tags.c.tag_id == tag_id, ilike_clause)
            )

        else:
            stmt = (
                select(User).join(users_courses, users_courses.c.student_id == User.id)
                .where(users_courses.c.course_id == course_id, ilike_clause)
            )
        res = await self._session.scalars(stmt.limit(10))
        return res.unique().all()  # type: ignore[return-value]
