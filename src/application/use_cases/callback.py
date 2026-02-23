from src.domain.entities import (
    Attempt,
)
from src.domain.value_objects import (
    TestCases
)
from src.application.dtos.callback import ResultDTO
from src.application.interfaces.repositories import (
    AttemptRepositoryInterface,
    ProblemRepositoryInterface
)
from src.application.interfaces.uow import UoWInterface
from .exceptions import (
    UndefinedProblemError,
)


class HandleTestResultUseCase:
    def __init__(
        self,
        uow: UoWInterface,
        problem_repo: ProblemRepositoryInterface,
        attempt_repo: AttemptRepositoryInterface
    ):
        self._uow = uow
        self._problem_repo = problem_repo
        self._attempt_repo = attempt_repo

    async def execute(self, dto: ResultDTO):
        async with self._uow:
            problem = await self._problem_repo.get_by_id(dto.problem_id)
            if not problem:
                raise UndefinedProblemError(
                    f"Got result of testing code for unexistant problem with id '{dto.problem_id}'")
            attempt = await self._attempt_repo.get_student_attempt(dto.course_id, dto.student_id, dto.problem_id)
            if not attempt:
                attempt = Attempt(dto.student_id, dto.problem_id, dto.code)
            test_cases = TestCases.from_dict(
                {case.test_num: {"input": case.input, "output": case.output} for case in dto.test_cases}
            )
            attempt.stop(test_cases)
