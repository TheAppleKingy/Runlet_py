from .test_case import TestCases
from .exceptions import (
    MismatchTestNumsError,
    MismatchTestsCountError,
    MismatchTestOutputsError,
)


class Attempt:
    def __init__(
        self,
        user_id: int,
        problem_id: int,
        amount: int = 0,
        passed: bool = False,
        test_cases: TestCases = None,
    ):
        self.user_id = user_id
        self.problem_id = problem_id
        self.amount = amount
        self.passed = passed
        self.test_cases = test_cases if test_cases is not None else TestCases()

    def mark_as_passed(self, expected_cases: TestCases):
        if expected_cases.count != self.test_cases.count:
            raise MismatchTestsCountError("Count of provided results mismatch with spcified cases")
        mismatching_outputs = []
        mismatchng_nums = []
        for num, case in self.test_cases:
            matching_result = expected_cases.get_case(num)
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
