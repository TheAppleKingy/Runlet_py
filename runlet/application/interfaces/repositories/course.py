from typing import Protocol, Optional, Any, Sequence

from runlet.domain.entities import Course


class CourseRepositoryInterface(Protocol):
    async def get_by_id(self, course_id: int) -> Optional[Course]: ...

    async def get_all_paginated(
        self,
        page: int,
        size: int
    ) -> tuple[list[Course], int]: ...

    async def get_student_courses_paginated(
        self,
        student_id: int,
        page: int,
        size: int
    ) -> tuple[list[Course], int]: ...

    async def get_teacher_courses_paginated(
        self,
        teacher_id: int,
        page: int,
        size: int
    ) -> tuple[list[Course], int]: ...

    async def get_by_id_with_rels(
        self,
        course_id: int,
        *rels_chains: Sequence[Any]
    ) -> Optional[Course]: ...

    async def check_user_in_course(self, user_id: int, course_id: int) -> bool: ...
    async def check_module_related(self, module_id: int, course_id: int) -> bool: ...
    async def get_favourites_for(self, user_id: int) -> list[Course]: ...
    async def add_to_favourites(self, user_id: int, course_id: int) -> None: ...
    async def delete_favourites(self, user_id: int, course_id: int) -> None: ...
    async def get_course_by_problem(self, problem_id: int) -> Optional[Course]: ...
    async def delete_course(self, course_id: int) -> None: ...
