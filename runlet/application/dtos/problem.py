from typing import Optional
from pydantic import BaseModel, Field, field_validator
from runlet.domain.value_objects import Examples, TestCases

from .test_cases import (
    TestCaseForStudentDTO,
    TestCaseForTeacherDTO,
    TestCaseDTO,
    ExampleCaseDTO
)


class ProblemG1(BaseModel):
    id: int
    name: str
    confirmed_passed: Optional[bool] = None
    tests_passed: Optional[bool] = None


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


class CreateUpdateProblemDTO(BaseModel):
    id: Optional[int] = None
    name: str = Field(max_length=100)
    module_id: int
    description: Optional[str] = Field(max_length=1024, default=None)
    auto_pass: bool
    show_test_cases: bool
    test_cases: list[TestCaseDTO] = Field(default_factory=list)
    examples: list[ExampleCaseDTO] = Field(default_factory=list)


class ProblemG5(BaseModel):
    id: int
    name: str
    seen_attempt: bool


class ProblemInfoForStudentDTO(_ContainsExample):
    problem_id: int
    problem_name: str
    problem_description: Optional[str] = None
    code: Optional[str] = None
    pending: bool = False
    test_cases: list[TestCaseForStudentDTO] = Field(default_factory=list)
    langs: dict[str, str]
    confirmed_passed: Optional[bool]


class ProblemInfoForTeacherDTO(_ContainsExample):
    problem_id: int
    problem_name: str
    confirmed_passed: Optional[bool]
    problem_description: Optional[str] = None
    code: Optional[str] = None
    test_cases: list[TestCaseForTeacherDTO] = Field(default_factory=list)


class ProblemWithRateInfoDTO(BaseModel):
    id: int
    name: str
    tests_passed: bool
    confirmed_passed: Optional[bool]
    seen_attempt: bool
