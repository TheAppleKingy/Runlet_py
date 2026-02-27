from typing import Optional

from runlet.domain.entities import (
    Attempt,
    Problem
)
from runlet.application.dtos.problem import (
    ProblemInfoForStudentDTO
)
from runlet.application.dtos.test_cases import (
    TestCaseForStudentDTO
)
from runlet.application.dtos.student import (
    CurrentAttemptInfo
)


def show_problem_info_for_student_to_solve(problem: Problem, attempt: Optional[Attempt]):
    res = ProblemInfoForStudentDTO(
        problem_id=problem.id,
        problem_name=problem.name,
        problem_description=problem.description,
    )
    if attempt:
        res.code = attempt.code
        res.test_cases = sorted(
            [
                TestCaseForStudentDTO(
                    test_num=num,
                    input=case.input if problem.show_test_cases else None,
                    current_output=case.output if problem.show_test_cases else None,
                    ok=problem.test_cases.get_case(num).output == case.output,  # type: ignore[union-attr]
                    expected_output=problem.test_cases.get_case(
                        num).output if problem.show_test_cases else None  # type: ignore[union-attr]
                ) for num, case in attempt.test_cases
            ], key=lambda tc: tc.test_num)
    return res


def show_current_attempts_info(attempts: list[Attempt]) -> list[CurrentAttemptInfo]:
    return list(reversed(sorted([CurrentAttemptInfo(
        problem_id=attempt.problem_id,
        problem_name=attempt.problem.name,
        tests_passed=attempt.tests_passed,
        confirmed_passed=attempt.confirmed_passed,
        seen=attempt.seen,
        updated_at=attempt.updated_at
    ) for attempt in attempts], key=lambda a: a.updated_at)))
