from pydantic import BaseModel, Field
from .problem import ProblemG1, ProblemG2


class ModuleG1(BaseModel):
    name: str
    problems: list[ProblemG1]


class ModuleG2(BaseModel):
    id: int
    name: str
    problems: list[ProblemG2]
