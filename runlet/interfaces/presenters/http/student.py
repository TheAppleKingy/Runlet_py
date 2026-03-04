from typing import Optional

from runlet.domain.entities import (
    Attempt,
    Problem
)
from runlet.application.dtos.problem import (
    ProblemInfoForStudentDTO
)
from runlet.application.dtos.test_cases import (
    TestCaseForStudentDTO,
)


def show_problem_info_for_student_to_solve(problem: Problem, attempt: Optional[Attempt]):
    res = ProblemInfoForStudentDTO(
        problem_id=problem.id,
        problem_name=problem.name,
        problem_description=problem.description,
        examples=problem.examples
    )
    if attempt:
        res.code = attempt.code
        res.test_cases = sorted(  # type: ignore[assignment]
            [
                TestCaseForStudentDTO(
                    test_num=num,
                    input=case.input if problem.show_test_cases else None,
                    current_output=case.output if problem.show_test_cases else None,
                    ok=problem.test_cases.get_case(num).output == case.output,  # type: ignore[union-attr]
                    expected_output=problem.test_cases.get_case(
                        num).output if problem.show_test_cases else None  # type: ignore[union-attr]
                ) for num, case in attempt.test_cases
            ], key=lambda tc: tc.test_num),
    return res
