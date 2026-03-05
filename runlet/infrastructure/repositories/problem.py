from typing import Optional

from sqlalchemy import select

from runlet.application.interfaces.repositories import ProblemRepositoryInterface
from runlet.domain.entities import Problem
from .base import BaseAlchemyRepository
from runlet.infrastructure.db.tables import problems


class AlchemyProblemRepository(BaseAlchemyRepository, ProblemRepositoryInterface):
    async def get_by_id(self, problem_id: int) -> Optional[Problem]:
        return await self._session.scalar(select(Problem).where(Problem.id == problem_id))  # type: ignore[arg-type]

    async def get_by_ids(self, problems_ids: list[int]) -> list[Problem]:
        res = await self._session.scalars(select(Problem).where(problems.c.id.in_(problems_ids)))
        return res.all()  # type: ignore[return-value]
