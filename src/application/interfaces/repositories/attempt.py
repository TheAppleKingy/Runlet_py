from typing import Protocol, Optional, Any, Sequence

from src.domain.entities import User, Attempt


class AttemptRepositoryInterface(Protocol):
    async def get_student_attempts(self, course_id: int, student_id: int) -> list[Attempt]: ...
    async def get_problem_students(self, problem_id: int) -> list[User]: ...
