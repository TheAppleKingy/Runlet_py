from dataclasses import dataclass, field
from datetime import datetime, timezone

from .problem import Problem

from ..value_objects import TestCases
from .exceptions import (
    AttemptAlreadyInProcessError,
    AlreadyPassedError,
    NotStartedAttemptError
)


@dataclass
class Attempt:
    user_id: int
    problem_id: int
    code: str = ""
    problem: Problem = field(default=None, init=False)  # type: ignore
    amount: int = field(default_factory=lambda: 0, init=False)
    tests_passed: bool = field(default=False, init=False)
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc), init=False)
    test_cases: TestCases = field(default_factory=TestCases)
    confirmed_passed: bool = field(default=False, init=False)
    seen: bool = field(default=False, init=False)
    pending: bool = field(default=False, init=False)

    def stop(self, result_test_cases: TestCases):
        """
        Compares test cases got in last attempt with excpected values of cases outputs.
        Updates data of  attempt instance

        :param result_test_cases: result of last code running
        :type result_test_cases: TestCases
        """
        if not self.pending:
            raise NotStartedAttemptError("Unable to stop not started attempt")
        self.test_cases = result_test_cases
        count_matches = self.problem.test_cases.count == self.test_cases.count
        mismatching_outputs = []
        mismatchng_nums = []
        for num, case in self.test_cases:
            matching_result = self.problem.test_cases.get_case(num)
            if not matching_result:
                mismatchng_nums.append(num)
                continue
            if matching_result.output != case.output:
                mismatching_outputs.append(num)
        if (mismatching_outputs or mismatchng_nums) or not count_matches:
            self.tests_passed = False
        else:
            self.tests_passed = True
            if self.problem.auto_pass:
                self.confirmed_passed = True
        self.pending = False
        self.updated_at = datetime.now(timezone.utc)

    def start(self):
        if self.pending:
            raise AttemptAlreadyInProcessError("Code is already testing now. Try later")
        if self.confirmed_passed:
            raise AlreadyPassedError("Attempt already confirmed by teacher")
        self.updated_at = datetime.now(timezone.utc)
        self.pending = True
        self.amount += 1
        self.seen = False

    def teacher_confirm(self, ok: bool):
        if self.pending:
            raise AttemptAlreadyInProcessError("Code is still testing now. Try later")
        self.confirmed_passed = ok
        self.updated_at = datetime.now(timezone.utc)
        self.seen = True

    def watch(self):
        if self.pending:
            raise AttemptAlreadyInProcessError("Code is still testing now. Try later")
        self.seen = True
        self.updated_at = datetime.now(timezone.utc)
