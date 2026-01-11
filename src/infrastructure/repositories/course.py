from typing import Optional, Any

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.application.interfaces.repositories import CourseRepositoryInterface
from src.domain.entities import Course, User, Tag
from src.infrastructure.db.tables import users_courses
from .base import BaseAlchemyRepository


class AlchemyCourseRepository(BaseAlchemyRepository, CourseRepositoryInterface):
    async def get_by_id(self, course_id: int) -> Optional[Course]:
        return await self._session.scalar(select(Course).where(Course.id == course_id))

    async def get_by_id_with_rels(self, course_id: int, *rel_models: Any) -> Optional[Course]:
        options = [selectinload(model) for model in rel_models]
        return await self._session.scalar(select(Course).where(Course.id == course_id).options(*options))

    async def get_user_courses(self, user_id: int) -> list[Course]:
        stmt = select(Course).join(
            users_courses, Course.id == users_courses.c.course_id,
        ).where(
            users_courses.c.student_id == user_id
        )
        res = await self._session.scalars(stmt)
        return res.unique().all()
