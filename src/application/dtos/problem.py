from typing import Optional
from pydantic import BaseModel, Field, field_validator
from src.domain.value_objects import Examples, TestCases


class TestCaseDTO(BaseModel):
    test_num: int
    input: str
    output: str


class ExampleCaseDTO(BaseModel):
    input: str
    output: str


class ProblemG1(BaseModel):
    id: int
    name: str


class _ContainsExample(BaseModel):
    examples: list[ExampleCaseDTO] = Field(default_factory=list)

    @field_validator("examples", mode="before")
    @classmethod
    def validate_examples(cls, value: Examples):
        return value.as_dicts()


class _ContainsTestCases(BaseModel):
    test_cases: list[TestCaseDTO] = Field(default_factory=list)

    @field_validator("test_cases", mode="before")
    @classmethod
    def validate_test_cases(cls, value: TestCases):
        return [{"test_num": case[0], **case[1].to_dict()} for case in value]


class ProblemG2(_ContainsExample):
    id: int
    name: str
    description: str


class ProblemG3(_ContainsExample, _ContainsTestCases):
    id: int
    name: str
    module_id: int
    description: Optional[str] = None
    auto_pass: bool
    show_test_cases: bool


class ProblemG4(_ContainsExample):
    id: int
    name: str
    description: str


class CreateUpdateProblemDTO(BaseModel):
    id: Optional[int] = None
    name: str = Field(max_length=100)
    module_id: int
    description: Optional[str] = Field(max_length=1024, default=None)
    auto_pass: bool
    show_test_cases: bool
    test_cases: list[TestCaseDTO] = Field(default_factory=list)
    examples: list[ExampleCaseDTO] = Field(default_factory=list)
