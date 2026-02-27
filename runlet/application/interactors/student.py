from typing import Optional

from runlet.domain.entities import (
    Course,
    Module,
    Problem,
    Attempt
)
from runlet.application.interfaces.repositories import (
    CourseRepositoryInterface,
    AttemptRepositoryInterface
)
from runlet.application.interfaces.message_publisher import MessagePublisherInterface
from runlet.application.interfaces.uow import UoWInterface
from .exceptions import (
    UndefinedModuleError,
    UndefinedProblemError
)
from runlet.application.dtos.student import (
    SendProblemSolutionDTO,
    RunDataDTO,
    TestSolutionDTO
)
from .base import (
    _CourseRepoRelatedInteractor,
    _CourseAttemptReposRelatedInteractor
)

from runlet.application.interfaces.message_tasks import SendCodeSolution


class ShowStudentCourses(_CourseRepoRelatedInteractor):
    async def __call__(self, user_id: int):
        async with self._uow:
            return await self._course_repo.get_student_courses(user_id)


class ShowStudentCourse(_CourseRepoRelatedInteractor):
    async def __call__(self, course_id: int):
        async with self._uow:
            return await self._course_repo.get_by_id_with_rels(course_id, [Course._modules, Module._problems])


class ShowProblemToSolve(_CourseAttemptReposRelatedInteractor):
    async def __call__(  # type: ignore[return]
        self,
        user_id: int,
        course_id: int,
        module_id: int,
        problem_id: int
    ) -> tuple[Problem, Optional[Attempt]]:
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._modules, Module._problems])
            module = course.get_module_by_id(module_id)  # type: ignore[union-attr]
            if not module:
                raise UndefinedModuleError("Module does not exists or not related with this course", status=404)
            problem = module.get_problem_by_id(problem_id)
            if not problem:
                raise UndefinedProblemError("Problem does not exist or not related to module", status=404)
            attempt = await self._attempt_repo.get_student_attempt(course_id, user_id, problem_id)
            return problem, attempt


class SendProblemSolution(_CourseAttemptReposRelatedInteractor):
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
        attempt_repo: AttemptRepositoryInterface,
        publisher: MessagePublisherInterface
    ):
        super().__init__(uow, course_repo, attempt_repo)
        self._publisher = publisher

    async def __call__(
        self,
        course_id: int,
        module_id: int,
        problem_id: int,
        student_id: int,
        dto: SendProblemSolutionDTO
    ):
        async with self._uow as uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._modules, Module._problems])
            module = course.get_module_by_id(module_id)  # type: ignore[union-attr]
            if not module:
                raise UndefinedModuleError("Module does not exist or not related to course")
            problem = module.get_problem_by_id(problem_id)
            if not problem:
                raise UndefinedProblemError("Problem does not exist or not related to module")
            attempt = await self._attempt_repo.get_student_attempt(course_id, student_id, problem_id)
            if not attempt:
                attempt = Attempt(student_id, problem.id, dto.code)
                uow.save(attempt)  # type: ignore[union-attr]
            attempt.start()
            message_dto = TestSolutionDTO(
                student_id=student_id,
                problem_id=problem_id,
                course_id=course_id,
                lang=dto.lang,
                code=dto.code,
                run_data=[RunDataDTO(test_num=num, input=case.input) for num, case in problem.test_cases]
            )
            await self._publisher.publish(SendCodeSolution(message_dto.model_dump_json()))


class ShowCurrentAttempts(_CourseAttemptReposRelatedInteractor):
    async def __call__(self, student_id: int, course_id: int) -> list[Attempt]:  # type: ignore[return]
        async with self._uow:
            return await self._attempt_repo.get_student_attempts(course_id, student_id)
