from typing import Optional, Protocol

from src.domain.entities import Module


class ModuleRepositoryInterface(Protocol):
    async def get_by_id(self, module_id: int) -> Optional[Module]: ...
    async def get_by_ids(self, modules_ids: list[int]) -> list[Module]: ...
