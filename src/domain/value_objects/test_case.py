from typing import Sequence, Optional
from dataclasses import dataclass, field

from .exceptions import DuplicateTestCaseInput, ValidationTestCaseError


@dataclass
class TestCase:
    input: str
    output: str = ""

    def __post_init__(self):
        self._validate_io(self.input)
        self._validate_io(self.output)

    def _validate_io(self, data: str):
        if not isinstance(data, str):
            raise ValidationTestCaseError("Data for test case is not valid")

    def to_dict(self):
        return {
            "input": self.input,
            "output": self.output
        }

    @classmethod
    def from_dict(cls, io_dict: dict[str, str]):
        return cls(**io_dict)


TestCasesDataType = dict[int, TestCase]
"""Represents format of data of test cases. { test_num -> { input: input_data, output: output_data } }"""


@dataclass
class TestCases:
    _data: TestCasesDataType = field(default_factory=dict)

    def __post_init__(self):
        self._data = self._get_validated_test_cases(self._data)

    def __iter__(self):
        return iter(self._data.items())

    def _validate_input_duplicates(self, cases: Sequence[TestCase]):
        """
        Ensures test cases inputs duplications
        """
        if len(set(case.input for case in cases)) != len(cases):
            raise DuplicateTestCaseInput("Inputs cannot match")

    def _validate_io_duplicates(self, cases_data: TestCasesDataType):
        case_map: dict[str, str] = {}
        res: TestCasesDataType = {}
        for num, case in cases_data.items():
            if case_map.get(case.input) == case.output:
                continue
            res[num] = case
            case_map[case.input] = case.output
        return res

    def _get_validated_test_cases(self, cases_data: TestCasesDataType):
        if not all((isinstance(num, int) and num > 0) for num in cases_data):
            raise ValidationTestCaseError("Number of test should be natural int")
        deduplicated_io = self._validate_io_duplicates(cases_data)
        self._validate_input_duplicates([v for v in deduplicated_io.values()])
        return deduplicated_io

    def get_case(self, num: int) -> Optional[TestCase]:
        return self._data.get(num)

    def as_dict(self):
        return {num: case.to_dict() for num, case in self._data.items()}

    @classmethod
    def from_dict(cls, test_cases_data: dict[int, dict[str, str]]):
        data = {num: TestCase.from_dict(case_data)
                for num, case_data in test_cases_data.items()}
        return cls(_data=data)

    def update_test_cases(self, cases_data: TestCasesDataType):
        res = self._data.copy()
        res.update(cases_data)
        deduplicated_io = self._get_validated_test_cases(res)
        self._data = deduplicated_io

    def delete_test_cases(self, nums: Sequence[int]):
        for num in nums:
            self._data.pop(num, None)

    @property
    def count(self):
        return len(self._data)
