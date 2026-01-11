from dataclasses import dataclass, field

from ..value_objects import TestCases


@dataclass
class Problem:
    name: str
    description: str
    course_id: int
    test_cases: TestCases = field(default_factory=TestCases)
    id: int = field(default=None, init=False)  # type: ignore
