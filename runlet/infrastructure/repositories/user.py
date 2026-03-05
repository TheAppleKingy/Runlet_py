# mypy: disable-error-code="arg-type"
from typing import Optional

from sqlalchemy import select, func

from runlet.domain.entities import (
    User,
    Attempt,
    Tag
)
from runlet.application.interfaces.repositories import UserRepositoryInterface
from runlet.infrastructure.db.tables import (
    users,
    users_tags,
    users_courses
)
from .base import BaseAlchemyRepository


class AlchemyUserRepository(BaseAlchemyRepository, UserRepositoryInterface):
    async def get_by_id(self, user_id: int) -> Optional[User]:
        return await self._session.scalar(select(User).where(User.id == user_id))

    async def get_by_ids(self, user_ids: list[int]) -> list[User]:
        res = await self._session.scalars(select(User).where(users.c.id.in_(user_ids)))
        return res.all()  # type: ignore

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self._session.scalar(select(User).where(User.email == email))

    async def count_by_email(self, email: str) -> int:
        return await self._session.scalar(select(func.count(User.id)).where(User.email == email)) or 0

    async def find_by_name(
        self,
        course_id: int,
        namelike: str,
        tag_id: Optional[int],
        page: int = 1,
        size: int = 10
    ) -> tuple[list[User], int]:
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
        res = await self._session.scalars(stmt.limit(size).order_by(User.name).offset((page - 1) * size))
        count = await self._session.scalar(select(func.count()).select_from(stmt)) or 0
        return res.unique().all(), (count + size - 1) // size  # type: ignore[return-value]

    async def get_by_id_with_attempts_seen_info(
        self,
        course_id: int,
    ) -> list[tuple[User, Optional[bool]]]:
        stmt = (
            select(User).add_columns(Attempt.seen).join(
                users_courses, users_courses.c.student_id == User.id
            ).join(
                Attempt, Attempt.user_id == User.id, isouter=True
            ).where(
                users_courses.c.course_id == course_id,
            )
        )
        res = await self._session.execute(stmt)
        return res.unique().all()  # type: ignore[return-value]

    async def get_paginated_by_tag(self, course_id: int, tag_id: int, page: int = 1, size: int = 7) -> tuple[list[User], int]:
        stmt = (
            select(User).
            join(users_tags, User.id == users_tags.c.user_id).join(Tag, Tag.id == users_tags.c.tag_id).
            where(Tag.course_id == course_id, Tag.id == tag_id).
            order_by(User.name).limit(size).offset((page - 1) * size)
        )
        count_stmt = (
            select(func.count(User.id))
            .where(
                users.c.id.in_(
                    select(users_tags.c.user_id)
                    .where(users_tags.c.tag_id == tag_id)
                )
            )
        )
        tags_res = await self._session.scalars(stmt)
        count = await self._session.scalar(count_stmt) or 0
        return tags_res.unique().all(), (count + size - 1) // size  # type: ignore[return-value]

    async def get_paginated_by_course(self, course_id: int, page: int = 1, size: int = 7) -> tuple[list[User], int]:
        stmt = (
            select(User).
            join(users_courses, users_courses.c.student_id == User.id).
            where(users_courses.c.course_id == course_id).
            order_by(User.name).limit(size).offset((page - 1) * size)
        )
        count_stmt = (
            select(func.count(User.id))
            .where(
                users.c.id.in_(
                    select(users_courses.c.student_id)
                    .where(users_courses.c.course_id == course_id)
                )
            )
        )
        courses_res = await self._session.scalars(stmt)
        count = await self._session.scalar(count_stmt) or 0
        return courses_res.unique().all(), (count + size - 1) // size  # type: ignore[return-value]
