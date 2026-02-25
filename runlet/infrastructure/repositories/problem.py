from typing import Optional

from sqlalchemy import select

from runlet.application.interfaces.repositories import ProblemRepositoryInterface
from runlet.domain.entities import Problem
from .base import BaseAlchemyRepository


class AlchemyProblemRepository(BaseAlchemyRepository, ProblemRepositoryInterface):
    async def get_by_id(self, problem_id: int) -> Optional[Problem]:
        return await self._session.scalar(select(Problem).where(Problem.id == problem_id))  # type: ignore[arg-type]
