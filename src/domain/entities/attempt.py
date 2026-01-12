from dataclasses import dataclass, field

from .problem import Problem

from ..value_objects import TestCases
from .exceptions import (
    MismatchTestNumsError,
    MismatchTestsCountError,
    MismatchTestOutputsError,
)


@dataclass
class Attempt:
    user_id: int
    problem_id: int
    problem: Problem = field(default=None, init=False)
    amount: int = field(default=0, init=False)
    passed: bool = field(default=False, init=False)
    test_cases: TestCases = field(default_factory=TestCases)

    def mark_as_passed(self):
        """
        Mark attempt as passed comparing test cases got in last attempt with excpected values of cases outputs 

        :param expected_cases: set of test cases that with correct outputs(problem.test_cases)
        :type expected_cases: TestCases
        """
        if self.problem.test_cases.count != self.test_cases.count:
            raise MismatchTestsCountError("Count of provided results mismatch with specified cases")
        mismatching_outputs = []
        mismatchng_nums = []
        for num, case in self.test_cases:
            matching_result = self.problem.test_cases.get_case(num)
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
