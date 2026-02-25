from dataclasses import dataclass, field
from typing import Optional

from .exceptions import HasNoDirectAccessError
from ..value_objects import TestCases, Examples


@dataclass
class Problem:
    name: str
    module_id: int
    description: Optional[str] = None
    auto_pass: bool = False
    show_test_cases: bool = False
    test_cases: TestCases = field(default_factory=TestCases)
    examples: Examples = field(default_factory=Examples)
    id: int = field(default=None, init=False)  # type: ignore


@dataclass
class Module:
    id: int = field(default=None, init=False)  # type: ignore
    name: str
    course_id: int
    order: int = 1
    _problems: list[Problem] = field(default_factory=list, init=False)

    @property
    def problems(self):
        return self._problems

    @problems.setter
    def problems(self, _):
        raise HasNoDirectAccessError("Cannot to set problems in module directly")

    def add_problems(self, problems: list[Problem]):
        self._problems += problems

    def delete_problems(self, ids: list[int]):
        self._problems = [problem for problem in self.problems if problem.id not in ids]

    def get_problem_by_id(self, problem_id: int):
        for p in self.problems:
            if p.id == problem_id:
                return p
        return None
