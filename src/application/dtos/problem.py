from typing import Optional
from pydantic import BaseModel, Field


class TestCaseDTO(BaseModel):
    input: str
    output: str


class ProblemG1(BaseModel):
    id: int
    name: str


class ProblemG2(BaseModel):
    id: int
    name: str
    description: str


class ProblemCreateDTO(BaseModel):
    name: str = Field(max_length=100)
    description: Optional[str] = Field(max_length=1024, default=None)
    auto_pass: bool = False
    test_cases: dict[int, TestCaseDTO] = {}
    show_test_cases: bool = False


class ProblemUpdateDTO(BaseModel):
    name: Optional[str] = Field(max_length=100, default=None)
    description: Optional[str] = Field(max_length=1024, default=None)
    auto_pass: Optional[bool] = None
    test_cases: dict[int, TestCaseDTO] = {}
    show_test_cases: Optional[bool] = None


class CreateUpdateProblemDTO(BaseModel):
    id: Optional[int] = None
    name: str = Field(max_length=100)
    module_id: int
    description: Optional[str] = Field(max_length=1024, default=None)
    auto_pass: bool
    test_cases: dict[int, TestCaseDTO] = {}
    show_test_cases: bool
