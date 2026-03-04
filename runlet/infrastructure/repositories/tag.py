from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from runlet.application.interfaces.repositories import TagRepositoryInterface
from runlet.domain.entities import Tag
from .base import BaseAlchemyRepository


class AlchemyTagRepository(BaseAlchemyRepository, TagRepositoryInterface):
    async def get_by_id_with_students(self, course_id: int, tag_id: int) -> Optional[Tag]:
        return await self._session.scalar(
            select(Tag).where(Tag.course_id == course_id, Tag.id == tag_id).options(selectinload(Tag.students))
        )
