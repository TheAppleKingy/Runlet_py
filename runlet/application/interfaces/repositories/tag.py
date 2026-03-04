from typing import Protocol, Optional

from runlet.domain.entities import Tag


class TagRepositoryInterface(Protocol):
    async def get_by_id_with_students(self, course_id: int, tag_id: int) -> Optional[Tag]: ...
