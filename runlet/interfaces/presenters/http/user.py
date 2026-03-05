from runlet.domain.entities import (
    Attempt,
    Course
)
from runlet.application.dtos.user import (
    CurrentAttemptInfoDTO,
    CurrentAttemptsInfoDTO
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
