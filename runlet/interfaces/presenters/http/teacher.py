from typing import Optional

from runlet.domain.entities import (
    Attempt,
    Module,
    Course,
    User,
    DefaultTagType,
    Tag
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
)
from runlet.application.dtos.user import (
    UserWithSeenDTO,
    UserG4
)
from runlet.application.dtos.tag import (
    TagG2,
    TagG3
)
from runlet.application.dtos.test_cases import TestCaseForTeacherDTO
from runlet.application.dtos.teacher import (
    PaginatedCourseTagsStudentsWithSeensDTO,
    PaginatedProblemStudentsInfoDTO,
    PaginatedTagStudentsDTO,
    PaginatedTagsStudentsDTO,
    PaginatedSearchStudentsWithSeensDTO
)


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
                confirmed_passed=attempt.confirmed_passed,
                seen_attempt=attempt.seen
            )
        )
    return sorted(list(module_map.values()), key=lambda m: m.order)


def show_tags_students_with_seen_info(
    course: Course,
    students_attempts: list[tuple[User, Optional[Attempt]]],
    tag: Optional[Tag],
    page: int,
    pages: int
):
    students_dtos = [
        UserWithSeenDTO(
            id=s.id,
            name=s.name,
            seen=False if attempt and attempt.seen is False else True
        ) for s, attempt in students_attempts
    ]
    tags_dtos = [
        TagG2(
            id=t.id,
            name=t.name
        ) for t in course.tags if t.name not in DefaultTagType.names()
    ]
    if tag:
        for tag_dto in tags_dtos:
            if tag.id == tag_dto.id:
                tag_dto.students = students_dtos
                break
    else:
        tags_dtos.append(TagG2(id=None, name="all", students=students_dtos))
    return PaginatedCourseTagsStudentsWithSeensDTO(
        course_id=course.id,
        course_name=course.name,
        tags=tags_dtos,
        page=page,
        pages=pages
    )


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


def show_problems_students_with_attempt_info(students_attempts: list[tuple[User, Attempt]], page: int, pages: int):
    return PaginatedProblemStudentsInfoDTO(
        students=[
            UserG4(
                id=user.id,
                name=user.name,
                seen=attempt.seen,
                tests_passed=attempt.tests_passed,
                confirmed_passed=attempt.confirmed_passed
            ) for user, attempt in students_attempts
        ],
        page=page,
        pages=pages
    )


def show_tags_paginated_students_to_update(
    course_students: list[User],
    course_students_page: int,
    course_students_pages: int,
    tag: Tag,
    tag_students: list[User],
    tag_students_page: int,
    tag_students_pages: int,
    tags: list[Tag]
):
    return PaginatedTagsStudentsDTO(
        tags_students=[
            PaginatedTagStudentsDTO(
                name="all",
                students=course_students,  # type: ignore[arg-type]
                page=course_students_page,
                pages=course_students_pages
            ),
            PaginatedTagStudentsDTO(
                id=tag.id,
                name=tag.name,
                students=tag_students,  # type: ignore[arg-type]
                page=tag_students_page,
                pages=tag_students_pages
            )
        ],
        tags=[TagG3(id=t.id, name=t.name) for t in tags]
    )


def show_paginated_searched_students_with_seens(
    students: list[User],
    attempts: list[Attempt],
    page: int,
    pages: int
):
    attempts_map = {a.user_id: a for a in attempts}
    return PaginatedSearchStudentsWithSeensDTO(
        students=[
            UserWithSeenDTO(id=s.id, name=s.name, seen=attempts_map[s.id].seen if attempts_map.get(s.id) else True) for s in students
        ],
        page=page,
        pages=pages
    )
