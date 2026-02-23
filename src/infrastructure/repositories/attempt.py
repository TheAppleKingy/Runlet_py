from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.application.interfaces.repositories import AttemptRepositoryInterface
from src.domain.entities import Attempt, Module, Problem, User
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

    async def get_problem_students(self, problem_id: int) -> list[User]:
        res = await self._session.scalars(
            select(User)
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
