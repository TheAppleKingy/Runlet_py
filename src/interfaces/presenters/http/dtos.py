from pydantic import BaseModel

from src.application.dtos.user import UserG1
from src.application.dtos.tag import TagG1


class ProblemWithRateInfoDTO(BaseModel):
    id: int
    name: str
    tests_passed: bool


class ModuleWithRateInfoDTO(BaseModel):
    name: str
    order: int
    problems: list[ProblemWithRateInfoDTO] = []


class TagsToUpdateDTO(BaseModel):
    students: list[UserG1] = []
    tags: list[TagG1] = []
