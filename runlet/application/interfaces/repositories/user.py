from typing import Protocol, Optional

from runlet.domain.entities import User


class UserRepositoryInterface(Protocol):
    async def get_by_id(self, user_id: int) -> Optional[User]: ...
    async def get_by_ids(self, user_ids: list[int]) -> list[User]: ...
    async def get_by_email(self, email: str) -> Optional[User]: ...
    async def count_by_email(self, email: str) -> int: ...

    async def find_by_name(
        self,
        course_id: int,
        namelike: str,
        tag_id: Optional[int],
        page: int = 1,
        size: int = 10
    ) -> tuple[list[User], int]: ...

    async def get_paginated_by_tag(
        self,
        course_id: int,
        tag_id: int,
        page: int = 1,
        size: int = 7
    ) -> tuple[list[User], int]: ...

    async def get_paginated_by_course(self, course_id: int, page: int = 1, size: int = 7) -> tuple[list[User], int]: ...

    async def get_by_id_with_attempts_seen_info(
        self,
        course_id: int,
    ) -> list[tuple[User, Optional[bool]]]: ...
