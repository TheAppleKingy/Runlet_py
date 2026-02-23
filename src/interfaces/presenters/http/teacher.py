from src.domain.entities import (
    Attempt,
    Module,
    Course,
    User,
)

from .dtos import (
    ProblemWithRateInfoDTO,
    ModuleWithRateInfoDTO,
    CourseWithStudentsSeensDTO,
    UserWithSeenDTO,
    TagsStudentsWithSeenDTO,
    TestCaseForStudentDTO,
    ProblemInfoForStudentDTO
)


def student_problems_info(attempts: list[Attempt], modules: list[Module]):
    module_map = {module.id: ModuleWithRateInfoDTO(name=module.name, order=module.order) for module in modules}
    for attempt in attempts:
        presented = module_map[attempt.problem.module_id]
        presented.problems.append(ProblemWithRateInfoDTO(id=attempt.problem_id,
                                  name=attempt.problem.name, tests_passed=attempt.tests_passed, confirmed_passed=attempt.confirmed_passed))
    return sorted(list(module_map.values()), key=lambda m: m.order)


def show_tags_students_with_seen_info(course: Course, students_seens: list[tuple[User, bool | None]]):
    students_dtos = [UserWithSeenDTO(id=s.id, name=s.name, seen=bool(seen_info)) for s, seen_info in students_seens]
    students_dto_map = {dto.id: dto for dto in students_dtos}
    tags_dtos = [
        TagsStudentsWithSeenDTO(
            name=t.name,
            students=[students_dto_map[s.id] for s in t.students]
        ) for t in course.tags
    ]
    return CourseWithStudentsSeensDTO(id=course.id, name=course.name, tags=tags_dtos, students=students_dtos)


def show_student_problem_to_rate(attempt: Attempt):
    return ProblemInfoForStudentDTO(
        problem_id=attempt.problem.id,
        problem_description=attempt.problem.description,
        problem_name=attempt.problem.name,
        code=attempt.code,
        test_cases=sorted(
            [
                TestCaseForStudentDTO(
                    test_num=num,
                    input=case.input,
                    output=case.output,
                    ok=case.output == attempt.problem.test_cases.get_case(num).output  # type: ignore[union-attr]
                ) for num, case in attempt.test_cases
            ],
            key=lambda tc: tc.test_num
        )
    )
