from typing import Optional

from pydantic import BaseModel
from .problem import ProblemG1, ProblemG2


class ModuleG1(BaseModel):
    name: str
    problems: list[ProblemG1]


class ModuleG2(BaseModel):
    id: int
    name: str
    problems: list[ProblemG2]


class ModuleUpdateDTO(BaseModel):
    id: int
    name: Optional[str] = None
    order: Optional[int] = None


class ModuleCreateDTO(BaseModel):
    name: str
    order: int


class ModuleCreateUpdateDTO(BaseModel):
    id: Optional[int] = None
    name: str
    order: int
