# mypy: disable-error-code="arg-type"
from typing import Optional, Sequence, Any

from sqlalchemy import (
    select,
    exists,
    func,
    insert,
    desc,
    delete
)
from sqlalchemy.orm import selectinload

from runlet.application.interfaces.repositories import CourseRepositoryInterface
from runlet.domain.entities import (
    Course,
    Module,
    Problem
)
from runlet.infrastructure.db.tables import (
    users_courses,
    favourites,
    courses
)
from .base import BaseAlchemyRepository


class AlchemyCourseRepository(BaseAlchemyRepository, CourseRepositoryInterface):
    async def get_by_id(self, course_id: int) -> Optional[Course]:
        return await self._session.scalar(select(Course).where(Course.id == course_id))

    async def get_all_paginated(self, page: int, size: int) -> tuple[list[Course], int]:
        stmt = select(Course)
        res = await self._session.scalars(stmt.offset((page - 1) * size).limit(size).order_by(Course.created_at))
        count = await self._session.scalar(select(func.count()).select_from(stmt)) or 0
        return res.all(), (count + size - 1) // size  # type: ignore[return-value]

    async def get_student_courses_paginated(self, student_id: int, page: int, size: int) -> tuple[list[Course], int]:
        stmt = select(Course).join(
            users_courses, Course.id == users_courses.c.course_id,
        ).where(
            users_courses.c.student_id == student_id
        )
        res = await self._session.scalars(stmt.limit(size).order_by(desc(users_courses.c.created_at)).offset((page - 1) * size))
        count = await self._session.scalar(select(func.count()).select_from(stmt)) or 0
        return res.unique().all(), (count + size - 1) // size  # type: ignore

    async def get_teacher_courses_paginated(self, teacher_id: int, page: int, size: int) -> tuple[list[Course], int]:
        stmt = select(Course).where(Course._teacher_id == teacher_id)
        res = await self._session.scalars(stmt.limit(size).order_by(desc(Course.created_at)).offset((page - 1) * size))
        count = await self._session.scalar(select(func.count()).select_from(stmt)) or 0
        return res.all(), (count + size - 1) // size  # type: ignore

    async def check_user_in_course(self, user_id: int, course_id: int) -> bool:
        return await self._session.scalar(  # type: ignore
            select(
                exists(
                    select(1).select_from(users_courses).where(users_courses.c.student_id ==
                                                               user_id, users_courses.c.course_id == course_id)
                )
            )
        )

    async def check_module_related(self, module_id: int, course_id: int) -> bool:
        return await self._session.scalar(  # type: ignore
            select(
                exists(
                    select(1).where(Module.id == module_id, Module.course_id == course_id)
                )
            )
        )

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

    async def get_favourites_for(self, user_id: int) -> list[Course]:
        sub = (
            select(favourites.c.course_id)
            .where(favourites.c.user_id == user_id)
            .subquery()
        )
        res = await self._session.scalars(select(Course).where(courses.c.id.in_(sub)))
        return res.unique().all()  # type: ignore[return-value]

    async def add_to_favourites(self, user_id: int, course_id: int) -> None:
        exists = await self._session.scalar(select(favourites).where(
            favourites.c.user_id == user_id,
            favourites.c.course_id == course_id
        ))
        if not exists:
            await self._session.execute(insert(favourites).values(
                user_id=user_id,
                course_id=course_id
            ))

    async def get_course_by_problem(self, problem_id: int) -> Optional[Course]:
        stmt = (
            select(Course)
            .where(
                exists(
                    select(1).select_from(Module)
                    .join(Problem, Problem.module_id == Module.id)
                    .where(Problem.id == problem_id, Module.course_id == Course.id)
                )
            )
        )
        return await self._session.scalar(stmt)

    async def delete_favourites(self, user_id: int, course_id: int) -> None:
        await self._session.execute(delete(favourites).where(favourites.c.user_id == user_id, favourites.c.course_id == course_id))

    async def delete_course(self, course_id: int) -> None:
        await self._session.execute(delete(Course).where(Course.id == course_id))
