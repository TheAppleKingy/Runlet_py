from typing import Protocol, Optional

from src.domain.entities import Course


class CourseRepositoryInterface(Protocol):
    async def get_by_id(self, course_id: int) -> Optional[Course]: ...
    async def get_user_courses(self, user_id: int) -> list[Course]: ...
