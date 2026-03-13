from typing import Optional

from runlet.domain.entities import (
    Attempt,
    Problem,
    Course
)
from runlet.application.dtos.problem import (
    ProblemInfoForStudentDTO,
    ProblemG1
)
from runlet.application.dtos.test_cases import (
    TestCaseForStudentDTO,
)
from runlet.application.dtos.course import (
    CourseG7
)
from runlet.application.dtos.module import (
    ModuleG1
)


def show_problem_info_for_student_to_solve(problem: Problem, attempt: Optional[Attempt], langs: dict[str, str]):
    res = ProblemInfoForStudentDTO(
        problem_id=problem.id,
        problem_name=problem.name,
        problem_description=problem.description,
        examples=problem.examples,  # type: ignore[arg-type]
        langs=langs
    )
    if attempt:
        res.pending = attempt.pending
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


def show_student_course_problems_with_attempts_info(course: Course, attempts: list[Attempt]):
    res = CourseG7(id=course.id, name=course.name, description=course.description)
    attempts_map: dict[int, Attempt] = {a.problem_id: a for a in attempts}
    for m in course.modules:
        dto = ModuleG1(id=m.id, order=m.order, name=m.name)
        for p in m.problems:
            attempt = attempts_map.get(p.id)
            dto.problems.append(
                ProblemG1(
                    id=p.id,
                    name=p.name,
                    tests_passed=attempt.tests_passed if attempt else None,
                    confirmed_passed=attempt.confirmed_passed if attempt else None
                )
            )
        res.modules.append(dto)
    return res
