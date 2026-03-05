from typing import Optional, Protocol

from runlet.domain.entities import Problem


class ProblemRepositoryInterface(Protocol):
    async def get_by_id(self, problem_id: int) -> Optional[Problem]: ...
    async def get_by_ids(self, problems_ids: list[int]) -> list[Problem]: ...
