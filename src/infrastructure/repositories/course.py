from typing import Optional, Any

from sqlalchemy import select, exists
from sqlalchemy.orm import selectinload

from src.application.interfaces.repositories import CourseRepositoryInterface
from src.domain.entities import Course, User, Tag, Module
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

    async def get_by_id_with_rels(self, course_id: int, *rels: Any) -> Optional[Course]:
        options = [selectinload(model) for model in rels]
        return await self._session.scalar(select(Course).where(Course.id == course_id).options(*options))

    async def get_by_id_to_manage_students(self, course_id: int) -> Optional[Course]:
        return await self._session.scalar(
            select(Course).where(Course.id == course_id).options(
                selectinload(Course._tags).selectinload(Tag.students),
                selectinload(Course._students)
            )
        )

    async def get_by_id_for_students(self, course_id: int) -> Optional[Course]:
        return await self._session.scalar(
            select(Course).where(Course.id == course_id).options(
                selectinload(Course._modules).selectinload(Module._problems)
            )
        )

    async def get_course_full_rels(self, course_id: int) -> Optional[Course]:
        return await self._session.scalar(
            select(Course).where(Course.id == course_id)
            .options(
                selectinload(Course._modules).selectinload(Module._problems),
                selectinload(Course._tags).selectinload(Tag.students).load_only(User.name),
                selectinload(Course._students).load_only(User.name)
            )
        )

    async def check_user_in_course(self, user_id: int, course_id: int) -> bool:
        return await self._session.scalar(
            select(
                exists(
                    select(1).select_from(users_courses).where(users_courses.c.user_id ==
                                                               user_id, users_courses.c.course_id == course_id)
                )
            )
        )
