from typing import Protocol

from runlet.domain.entities import Module


class ModuleRepositoryInterface(Protocol):
    async def get_by_ids(self, modules_ids: list[int]) -> list[Module]: ...
