from runlet.domain.entities import (
    Attempt,
    Course
)
from runlet.application.dtos.user import (
    CurrentAttemptInfoDTO,
    CurrentAttemptsInfoDTO
)

from runlet.application.dtos.main import (
    MainDTO,
    PaginatedCoursesDTO
)


def show_current_attempts_info(data: list[tuple[Attempt, Course]], page: int, pages: int) -> CurrentAttemptsInfoDTO:
    attempts_info = [
        CurrentAttemptInfoDTO(
            problem_id=a.problem_id,
            module_id=a.problem.module_id,
            course_id=c.id,
            problem_name=a.problem.name,
            course_name=c.name,
            tests_passed=a.tests_passed,
            confirmed_passed=a.confirmed_passed,
            seen=a.seen,
            pending=a.pending
        ) for a, c in data
    ]
    return CurrentAttemptsInfoDTO(attempts_info=attempts_info, page=page, pages=pages)


def show_main(
        all_courses: list[Course],
        all_page: int,
        all_pages: int,
        as_teacher: list[Course],
        as_teacher_page: int,
        as_teacher_pages: int,
        as_student: list[Course],
        as_student_page: int,
        as_student_pages: int
) -> MainDTO:
    return MainDTO(
        as_teacher=PaginatedCoursesDTO(
            courses=as_teacher,
            page=as_teacher_page,
            pages=as_teacher_pages
        ),
        as_student=PaginatedCoursesDTO(
            courses=as_student,
            page=as_student_page,
            pages=as_student_pages
        ),
        all_courses=PaginatedCoursesDTO(
            courses=all_courses,
            page=all_page,
            pages=all_pages
        )
    )
