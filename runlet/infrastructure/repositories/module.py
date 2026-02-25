from sqlalchemy import select

from runlet.application.interfaces.repositories import ModuleRepositoryInterface
from runlet.domain.entities import Module
from runlet.infrastructure.db.tables import modules
from .base import BaseAlchemyRepository


class AlchemyModuleRepository(BaseAlchemyRepository, ModuleRepositoryInterface):
    async def get_by_ids(self, modules_ids: list[int]) -> list[Module]:
        res = await self._session.scalars(select(Module).where(modules.c.id.in_(modules_ids)))
        return res.all()  # type: ignore
