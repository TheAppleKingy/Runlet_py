from pydantic import BaseModel


class TestCaseDTO(BaseModel):
    input: str
    output: str


class ProblemForTeacherDTO(BaseModel):
    id: int
    name: str
    description: str
    test_cases: dict[int, TestCaseDTO] = {}


class ModuleForTeacherDTO(BaseModel):
    id: int
    name: str
    problems: list[ProblemForTeacherDTO] = []


class CourseToUpdateDTO(BaseModel):
    id: int
    name: str
    modules: list[ModuleForTeacherDTO] = []
