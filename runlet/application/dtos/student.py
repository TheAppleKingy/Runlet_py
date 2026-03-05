from pydantic import BaseModel, Field

from runlet.domain.interfaces.types import CodeName


class SendProblemSolutionDTO(BaseModel):
    code: str
    lang: CodeName


class RunDataDTO(BaseModel):
    test_num: int
    input: str


class TestSolutionDTO(BaseModel):
    student_id: int
    problem_id: int
    course_id: int
    lang: CodeName
    code: str
    run_data: list[RunDataDTO] = Field(min_length=1)
