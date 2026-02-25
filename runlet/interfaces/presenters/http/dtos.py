from typing import Optional

from pydantic import BaseModel, Field

from runlet.application.dtos.user import UserG1
from runlet.application.dtos.tag import TagG1


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


class TestCaseForStudentDTO(BaseModel):
    test_num: int
    input: Optional[str] = None
    output: Optional[str] = None
    ok: bool


class ProblemInfoForStudentDTO(BaseModel):
    problem_id: int
    problem_name: str
    problem_description: Optional[str] = None
    code: Optional[str] = None
    test_cases: list[TestCaseForStudentDTO] = Field(default_factory=list)
