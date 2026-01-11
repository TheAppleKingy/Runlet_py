from typing import Optional

from sqlalchemy import select

from src.application.interfaces.repositories import CourseRepositoryInterface
from src.domain.entities import Course, User
from src.infrastructure.db.tables import users_courses
from .base import BaseAlchemyRepository


class AlchemyCourseRepository(BaseAlchemyRepository, CourseRepositoryInterface):
    async def get_by_id(self, course_id: int) -> Optional[Course]:
        return await self._session.scalar(select(Course).where(Course.id == course_id))

    async def get_user_courses(self, user_id: int) -> list[Course]:
        stmt = select(Course).join(
            users_courses, Course.id == users_courses.c.course_id,
        ).where(
            users_courses.c.student_id == user_id
        )
        res = await self._session.scalars(stmt)
        return res.unique().all()
