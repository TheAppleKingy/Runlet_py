# mypy: disable-error-code="arg-type"
from typing import Optional

from sqlalchemy import select, exists
from sqlalchemy.orm import selectinload

from runlet.application.interfaces.repositories import AttemptRepositoryInterface
from runlet.domain.entities import (
    Attempt,
    Module,
    Problem,
    User,
    Course
)
from .base import BaseAlchemyRepository


class AlchemyAttemptRepository(BaseAlchemyRepository, AttemptRepositoryInterface):
    async def get_student_attempts(self, course_id: int, student_id: int) -> list[Attempt]:
        stmt = (
            select(Attempt)
            .join(Problem, Problem.id == Attempt.problem_id)
            .join(Module, Module.id == Problem.module_id)
            .where(Attempt.user_id == student_id, Module.course_id == course_id)
        )
        res = await self._session.scalars(stmt.options(selectinload(Attempt.problem)))
        return res.unique().all()  # type: ignore

    async def get_problem_students_with_attempts(self, problem_id: int) -> list[tuple[User, Attempt]]:
        res = await self._session.execute(
            select(User, Attempt)
            .join(Attempt, Attempt.user_id == User.id).where(Attempt.problem_id == problem_id)
        )
        return res.unique().all()  # type: ignore

    async def get_student_attempt(self, course_id: int, student_id: int, problem_id: int) -> Optional[Attempt]:
        stmt = (
            select(Attempt)
            .join(Problem, Problem.id == Attempt.problem_id)
            .join(Module, Module.id == Problem.module_id)
            .where(Attempt.user_id == student_id, Module.course_id == course_id, Attempt.problem_id == problem_id)
        )
        return await self._session.scalar(stmt.options(selectinload(Attempt.problem)))

    async def get_problems_ids_with_unseen_attempts(self, course_id: int) -> list[int]:
        stmt = (
            select(Problem.id)  # type: ignore[call-overload]
            .join(Module, Module.id == Problem.module_id)
            .join(Course, Course.id == Module.course_id)
            .where(Course.id == course_id)
            .where(
                exists().where(Attempt.problem_id == Problem.id, Attempt.seen == False)  # noqa: E712
            )
        )
        res = await self._session.scalars(stmt)
        return res.unique().all()  # type: ignore[return-value]
