from typing import Protocol, Optional


class TestCaseData(Protocol):
    input: str
    output: str


class ProblemData(Protocol):
    id: Optional[int]
    name: Optional[str]
    description: Optional[str]
    auto_pass: Optional[bool]
    test_cases: dict[int, TestCaseData]
    show_test_cases: Optional[bool]


class ModuleData(Protocol):
    id: Optional[int]
    name: Optional[str]
    order: Optional[int]
    problems: list[ProblemData]
