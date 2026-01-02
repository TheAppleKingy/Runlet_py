from dataclasses import dataclass, field

from .test_case import TestCase


@dataclass
class Problem:
    id: int = field(default=None)
    name: str = field(default="")
    description: str = field(default="")
    course_id: int = field(default=None)
    test_cases: list[TestCase] = field(default_factory=list, init=False)
