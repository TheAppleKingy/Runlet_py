from typing import Optional

from pydantic import BaseModel, Field
from .problem import (
    ProblemG1,
    ProblemG2,
    ProblemG5,
    ProblemWithRateInfoDTO
)


class OrderedModuleDTO(BaseModel):
    order: int


class ModuleG1(OrderedModuleDTO):
    id: int
    name: str
    problems: list[ProblemG1]


class ModuleG2(OrderedModuleDTO):
    id: int
    name: str
    problems: list[ProblemG2]


class ModuleG3(OrderedModuleDTO):
    id: int
    name: str
    problems: list[ProblemG5] = Field(default_factory=list)


class ModuleG4(BaseModel):
    name: str
    order: int
    problems: list[ProblemWithRateInfoDTO] = Field(default_factory=list)


class ModuleCreateUpdateDTO(BaseModel):
    id: Optional[int] = None
    name: str
    order: int
