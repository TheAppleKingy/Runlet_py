from pydantic import BaseModel, Field


class TestCaseDTO(BaseModel):
    test_num: int
    input: str
    output: str


class ProblemG1(BaseModel):
    id: int
    name: str


class ProblemG2(BaseModel):
    id: int
    name: str
    description: str


class ProblemC1(BaseModel):
    name: str = Field(max_length=100)
    description: str = Field(max_length=1024)
    auto_pass: bool = False
    test_cases: list[TestCaseDTO]
    show_test_cases: bool = False
