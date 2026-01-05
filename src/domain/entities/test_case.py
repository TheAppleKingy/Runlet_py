from typing import Sequence, Optional
from .exceptions import DuplicateTestCaseInput, ValidationTestCaseError


class TestCase:
    def __init__(self, input_: str = "", output: str = ""):
        self._validate_io(input_)
        self._validate_io(output)
        self.input = input_
        self.output = output

    def _validate_io(self, data: str):
        if data is None or not isinstance(data, str):
            raise ValidationTestCaseError("Data for test case is not valid")

    def to_dict(self):
        return {
            "input": self.input,
            "output": self.output
        }

    def from_dict(self, io_dict: dict[str, str]):
        self._validate_io(io_dict.get("input"))
        self._validate_io(io_dict.get("output"))
        self.input = io_dict["input"]
        self.output = io_dict["output"]
        return self


TestCasesDataType = dict[int, TestCase]
"""Represents format of data of test cases. { test_num -> { input: input_data, output: output_data } }"""


class TestCases:
    def __init__(self, with_update: bool = False):
        self._data: TestCasesDataType = {}
        self.with_update = with_update

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
        deduplicated_io = self._validate_io_duplicates(cases_data)
        self._validate_input_duplicates([v for v in deduplicated_io.values()])
        return deduplicated_io

    def get_case(self, num: int) -> Optional[TestCase]:
        return self._data.get(num)

    def as_dict(self):
        return {num: case.to_dict() for num, case in self._data.items()}

    def from_dict(self, test_cases_data: dict[int, dict[str, str]]):
        to_update = {num: TestCase().from_dict(case_data)
                     for num, case_data in test_cases_data.items()}
        self.update_test_cases(to_update)
        return self

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
