from typing import Any, Sequence, Generic, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.interfaces.types import DomainEnt
from .exceptions import NoRelationsError


class LoadRelationsMixin(Generic[DomainEnt]):
    _model: type[DomainEnt]
    _session: AsyncSession

    def __class_getitem__(cls, item: type[DomainEnt]):
        new_cls = type(
            f"{cls.__name__}[{item.__name__}]",
            (cls,),
            {"_model": item}
        )
        return new_cls

    async def get_by_id_with_rels(self, entity_id: int, *rels_chains: Sequence[Any]) -> Optional[DomainEnt]:
        options = []
        for list_models in rels_chains:
            depth = len(list_models)
            if depth <= 0:
                raise NoRelationsError("Provided empty list of relations")
            root_rel = selectinload(list_models[0])
            for i in range(1, depth):
                root_rel = getattr(root_rel, "selectinload")(list_models[i])
            options.append(root_rel)
        return await self._session.scalar(select(self._model).where(self._model.id == entity_id).options(*options))
