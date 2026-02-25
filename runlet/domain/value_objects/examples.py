from dataclasses import dataclass, field

from .test_case import TestCase


@dataclass
class Examples:
    _data: list[TestCase] = field(default_factory=list)

    def cases(self):
        return self._data

    def as_dicts(self):
        return [case.to_dict() for case in self._data]

    @classmethod
    def from_raw(cls, cases_dicts: list[dict[str, str]]):
        return cls([TestCase.from_dict(case) for case in cases_dicts])
