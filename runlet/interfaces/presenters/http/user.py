from runlet.domain.entities import (
    Attempt
)
from runlet.application.dtos.student import (
    CurrentAttemptInfo
)


def show_current_attempts_info(attempts: list[Attempt]) -> list[CurrentAttemptInfo]:
    return list(reversed(sorted([CurrentAttemptInfo(
        problem_id=attempt.problem_id,
        problem_name=attempt.problem.name,
        tests_passed=attempt.tests_passed,
        confirmed_passed=attempt.confirmed_passed,
        seen=attempt.seen,
        updated_at=attempt.updated_at
    ) for attempt in attempts], key=lambda a: a.updated_at)))
