
from pydantic import BaseModel, Field

from src.application.dtos.user import UserG1
from src.application.dtos.tag import TagG1


class UserWithSeenDTO(UserG1):
    seen: bool


class TagsStudentsWithSeenDTO(BaseModel):
    name: str
    students: list[UserWithSeenDTO] = Field(default_factory=list)


class ProblemWithRateInfoDTO(BaseModel):
    id: int
    name: str
    tests_passed: bool
    confirmed_passed: bool


class ModuleWithRateInfoDTO(BaseModel):
    name: str
    order: int
    problems: list[ProblemWithRateInfoDTO] = Field(default_factory=list)


class TagsToUpdateDTO(BaseModel):
    students: list[UserG1] = []
    tags: list[TagG1] = []


class CourseWithStudentsSeensDTO(BaseModel):
    id: int
    name: str
    tags: list[TagsStudentsWithSeenDTO] = Field(default_factory=list)
    students: list[UserWithSeenDTO] = Field(default_factory=list)
