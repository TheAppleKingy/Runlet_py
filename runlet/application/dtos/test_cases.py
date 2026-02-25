from typing import Optional

from pydantic import BaseModel


class TestCaseDTO(BaseModel):
    test_num: int
    input: str
    output: str


class ExampleCaseDTO(BaseModel):
    input: str
    output: str


class TestCaseForTeacherDTO(BaseModel):
    test_num: int
    input: str
    current_output: str
    expected_output: str
    ok: bool


class TestCaseForStudentDTO(BaseModel):
    test_num: int
    input: Optional[str] = None
    current_output: Optional[str] = None
    expected_output: Optional[str] = None
    ok: bool
