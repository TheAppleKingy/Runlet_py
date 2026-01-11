from typing import Optional, Protocol

from src.domain.entities import Problem


class ProblemRepositoryInterface(Protocol):
    async def get_by_id(self, problem_id: int) -> Optional[Problem]: ...
    async def get_course_problems(self, course_id: int) -> list[Problem]: ...
