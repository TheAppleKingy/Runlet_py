from runlet.domain.entities import (
    Attempt,
    Module,
    Course,
    User,
    DefaultTagType
)

from runlet.application.dtos.problem import (
    ProblemWithRateInfoDTO,
    ProblemInfoForTeacherDTO
)
from runlet.application.dtos.problem import (
    ProblemG5
)
from runlet.application.dtos.module import (
    ModuleG3,
    ModuleG4
)
from runlet.application.dtos.course import (
    CourseG3,
    CourseG4
)
from runlet.application.dtos.user import (
    UserWithSeenDTO,
    UserG4
)
from runlet.application.dtos.tag import (
    TagG2
)
from runlet.application.dtos.test_cases import TestCaseForTeacherDTO


def student_problems_info(attempts: list[Attempt], modules: list[Module]):
    module_map = {
        module.id: ModuleG4(name=module.name, order=module.order) for module in modules
    }
    for attempt in attempts:
        presented = module_map[attempt.problem.module_id]
        presented.problems.append(
            ProblemWithRateInfoDTO(
                id=attempt.problem_id,
                name=attempt.problem.name,
                tests_passed=attempt.tests_passed,
                confirmed_passed=attempt.confirmed_passed
            )
        )
    return sorted(list(module_map.values()), key=lambda m: m.order)


def show_tags_students_with_seen_info(
    course: Course,
    students_seens: list[tuple[User, bool | None]]
):
    students_dtos = [
        UserWithSeenDTO(id=s.id, name=s.name, seen=False if seen_info is False else True) for s, seen_info in students_seens
    ]
    students_dto_map = {dto.id: dto for dto in students_dtos}
    tags_dtos = [
        TagG2(
            name=t.name,
            students=[students_dto_map[s.id] for s in t.students]
        ) for t in course.tags if t.name not in DefaultTagType.names()
    ]
    return CourseG4(id=course.id, name=course.name, tags=tags_dtos, students=students_dtos)


def show_student_problem_to_rate(attempt: Attempt):
    return ProblemInfoForTeacherDTO(
        problem_id=attempt.problem.id,
        problem_description=attempt.problem.description,
        problem_name=attempt.problem.name,
        code=attempt.code,
        test_cases=sorted(
            [
                TestCaseForTeacherDTO(
                    test_num=num,
                    input=case.input,
                    current_output=case.output,
                    ok=case.output == attempt.problem.test_cases.get_case(num).output,  # type: ignore[union-attr]
                    expected_output=attempt.problem.test_cases.get_case(num).output,  # type: ignore[union-attr]
                ) for num, case in attempt.test_cases
            ],
            key=lambda tc: tc.test_num
        ),
        examples=attempt.problem.examples  # type: ignore[arg-type]
    )


def show_course_modules_problems_with_seen_info(course: Course, unseen_problems_ids: list[int]):
    modules_dtos: list[ModuleG3] = []
    for module in course.modules:
        module_dto = ModuleG3(id=module.id, name=module.name, order=module.order)
        for problem in module.problems:
            module_dto.problems.append(ProblemG5(
                id=problem.id,
                name=problem.name,
                seen_attempt=problem.id not in unseen_problems_ids
            ))
        modules_dtos.append(module_dto)
    res = CourseG3(id=course.id, name=course.name, modules=modules_dtos)
    return res


def show_problems_students_with_attempt_info(students_attempts: list[tuple[User, Attempt]]):
    return [
        UserG4(
            id=user.id,
            name=user.name,
            seen=attempt.seen,
            tests_passed=attempt.tests_passed,
            confirmed_passed=attempt.confirmed_passed
        ) for user, attempt in students_attempts
    ]
