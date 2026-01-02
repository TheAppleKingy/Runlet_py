from dataclasses import dataclass, field

from .test_case import TestCases
from .exceptions import (
    MismatchTestNumsError,
    MismatchTestsCountError,
    MismatchTestOutputsError,
)


@dataclass
class Attempt:
    student_id: int
    problem_id: int
    amount: int = field(default=0, init=False)
    passed: bool = field(default=False, init=False)
    _test_cases_data: dict[int, dict[str, str]] = field(default_factory=dict, init=False)
    _test_cases: TestCases = field(default_factory=TestCases, init=False)
    _result_cases_data: dict[int, dict[str, str]] = field(default_factory=dict, init=False)
    _result_cases: TestCases = field(default_factory=TestCases, init=False)

    @property
    def test_cases(self):
        return self._test_cases

    @test_cases.setter
    def test_cases(self, test_cases: TestCases):
        self._test_cases = test_cases
        self._test_cases_data = test_cases.as_dict()

    @property
    def result_cases(self):
        return self._result_cases

    @result_cases.setter
    def result_cases(self, result_cases: TestCases):
        if result_cases.count != self._test_cases.count:
            raise MismatchTestsCountError("Count of provided results mismatch with spcified cases")
        for num, _ in result_cases:
            matching_case = self.test_cases.get_case(num)
            if not matching_case:
                raise MismatchTestNumsError(
                    f"Provided result test num {num} does not exist in defined set of test cases")
        self._result_cases = result_cases
        self._result_cases_data = result_cases.as_dict()

    def mark_as_passed(self):
        if self._result_cases.count != self._test_cases.count:
            raise MismatchTestsCountError("Count of provided results mismatch with spcified cases")
        mismatching_outputs = []
        mismatchng_nums = []
        for num, case in self._test_cases:
            matching_result = self._result_cases.get_case(num)
            if not matching_result:
                mismatchng_nums.append(num)
                continue
            if matching_result.output != case.output:
                mismatching_outputs.append(num)
        if mismatching_outputs:
            raise MismatchTestOutputsError(f"Result of tests {mismatching_outputs} are incorrect")
        if mismatchng_nums:
            raise MismatchTestNumsError(
                f"Provided results dont contain tests {mismatchng_nums}")
        self.passed = True
