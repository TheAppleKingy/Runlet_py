from dataclasses import dataclass, field

from .exceptions import HasNoDirectAccessError
from ..value_objects import TestCases


@dataclass
class Problem:
    name: str
    description: str
    module_id: int
    auto_pass: bool = False
    show_test_cases: bool = False
    test_cases: TestCases = field(default_factory=TestCases)
    id: int = field(default=None, init=False)  # type: ignore


@dataclass
class Module:
    id: int = field(default=None, init=False)  # type: ignore
    name: str
    course_id: int
    _problems: list[Problem] = field(default_factory=list, init=False)

    @property
    def problems(self):
        return self._problems

    @problems.setter
    def problems(self, _):
        raise HasNoDirectAccessError("Cannot to set problems in module directly")

    def add_problems(self, problems: list[Problem]):
        to_append = [problem for problem in problems if problem not in self.problems]
        self._problems += to_append

    def delete_problems(self, ids: list[int]):
        self._problems = [problem for problem in self.problems if problem.id not in ids]
