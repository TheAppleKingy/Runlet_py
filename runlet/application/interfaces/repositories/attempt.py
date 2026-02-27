from typing import Protocol, Optional

from runlet.domain.entities import User, Attempt


class AttemptRepositoryInterface(Protocol):
    async def get_student_attempts(self, course_id: int, student_id: int) -> list[Attempt]: ...
    async def get_problem_students_with_attempts(self, problem_id: int) -> list[tuple[User, Attempt]]: ...
    async def get_student_attempt(self, course_id: int, student_id: int, problem_id: int) -> Optional[Attempt]: ...

    async def get_problems_ids_with_unseen_attempts(self, course_id: int) -> list[int]:
        """
        Returns ids of problems within course with provided course_id that have unseen attempts
        """
