from dataclasses import dataclass, field
from typing import Sequence
from ..exceptions.entities import DuplicateTestCaseInput, ValidationTestCaseError


@dataclass
class TestCase:
    input: str = field(default="")
    output: str = field(default="")

    def __post_init__(self):
        if self.input is None or not isinstance(self.input, str):
            raise ValidationTestCaseError("Data for test case is not valid")
        if self.output is None or not isinstance(self.output, str):
            raise ValidationTestCaseError("Data for test case is not valid")

    def to_dict(self):
        return {
            "input": self.input,
            "output": self.output
        }

    def from_dict(self, io_dict: dict[str, str]):
        i = io_dict.get("input")
        o = io_dict.get("output")
        if i is None or o is None or not (isinstance(i, str) and isinstance(o, str)):
            raise ValidationTestCaseError("Data for test case is not valid")
        self.input = io_dict["input"]
        self.output = io_dict["output"]


TestCasesDataType = dict[int, TestCase]
"""Represents format of data of test cases. { test_num -> { input: input_data, output: output_data } }"""


@dataclass
class TestCases:
    _data: TestCasesDataType = field(default_factory=dict[int, TestCase])
    with_update: bool = field(default=False)

    def __post_init__(self):
        if self._data:
            self._data = self._get_validated_test_cases(self._data)

    def __iter__(self):
        return iter(self._data.items())

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, cases_data: TestCasesDataType):
        self._data = self._get_validated_test_cases(cases_data)

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
        deduplicated_io = self._validate_io_duplicates(cases_data)
        self._validate_input_duplicates([v for v in deduplicated_io.values()])
        return deduplicated_io

    def get_case(self, num: int) -> TestCase:
        return self._data.get(num)

    def as_dict(self):
        return {num: case.to_dict() for num, case in self._data.items()}

    def update_test_cases(self, cases_data: TestCasesDataType):
        if set(case.input for case in self._data.values()) & set(case.input for case in cases_data.values()):
            raise DuplicateTestCaseInput("Inputs cannot match")
        self._data.update(cases_data)

    def delete_test_cases(self, nums: Sequence[int]):
        for num in nums:
            self._data.pop(num, None)

    @property
    def count(self):
        return len(self._data)
