from typing import Optional, Any, Sequence

from sqlalchemy import select, exists, func
from sqlalchemy.orm import selectinload

from src.application.interfaces.repositories import CourseRepositoryInterface
from src.domain.entities import Course
from src.infrastructure.db.tables import users_courses
from .base import BaseAlchemyRepository


class AlchemyCourseRepository(BaseAlchemyRepository, CourseRepositoryInterface):
    async def get_by_id(self, course_id: int) -> Optional[Course]:
        return await self._session.scalar(select(Course).where(Course.id == course_id))

    async def get_all_paginated(self, page: int = 1, size: int = 10):
        page = max(1, page)
        size = min(100, max(1, size))
        count_stmt = select(func.count()).select_from(
            select(Course).order_by(Course.id).subquery())
        total = await self._session.scalar(count_stmt)
        offset = (page - 1) * size
        if offset >= total:  # type: ignore
            return []
        res = await self._session.scalars(select(Course).offset(offset).limit(size))
        return res.all(), page, size, total

    async def get_student_courses(self, student_id: int) -> list[Course]:
        stmt = select(Course).join(
            users_courses, Course.id == users_courses.c.course_id,
        ).where(
            users_courses.c.student_id == student_id
        )
        res = await self._session.scalars(stmt)
        return res.unique().all()  # type: ignore

    async def get_teacher_courses(self, teacher_id: int) -> list[Course]:
        res = await self._session.scalars(select(Course).where(Course._teacher_id == teacher_id))
        return res.all()  # type: ignore

    async def get_by_id_with_rels(self, course_id: int, *rels_chains: Sequence[Any]) -> Optional[Course]:
        options = []
        for list_models in rels_chains:
            depth = len(list_models)
            if depth <= 0:
                raise
            root_rel = selectinload(list_models[0])
            for i in range(1, depth):
                root_rel = getattr(root_rel, "selectinload")(list_models[i])
            options.append(root_rel)
        return await self._session.scalar(select(Course).where(Course.id == course_id).options(*options))

    async def check_user_in_course(self, user_id: int, course_id: int) -> bool:
        return await self._session.scalar(  # type: ignore
            select(
                exists(
                    select(1).select_from(users_courses).where(users_courses.c.student_id ==
                                                               user_id, users_courses.c.course_id == course_id)
                )
            )
        )
