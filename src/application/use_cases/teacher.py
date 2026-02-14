from abc import ABC

from src.domain.entities import Course, Problem, Module, Tag, DefautTagType, Attempt
from src.domain.value_objects import TestCases, TestCase
from src.domain.services.course import (
    CourseTagManagerService,
    CourseStudentsManagerService,
    CourseModulesManagerService,
    CourseProblemManagerService
)
from src.application.interfaces.uow import UoWInterface
from src.application.interfaces.services import AuthenticationServiceInterface
from src.application.interfaces.repositories import (
    CourseRepositoryInterface,
    UserRepositoryInterface,
    ModuleRepositoryInterface,
    ProblemRepositoryInterface,
    AttemptRepositoryInterface
)
from src.application.use_cases.exceptions import (
    UndefinedCourseError,
    ImpossibleOperationError,
    undefinedStudentError,
    UndefinedModuleError,
    UndefinedProblemError,
    UndefinedTagError
)
from src.application.dtos.teacher import (
    TagsCreateUpdate,
    GenLinkDTO,
    DeleteProblemsDTO,
    AddStudentsDTO,
    DeleteStudentsDTO,
)
from src.application.dtos.course import (
    CourseUpdateDTO
)
from src.application.dtos.module import (
    ModuleCreateDTO,
    ModuleUpdateDTO
)
from src.application.dtos.problem import ProblemCreateDTO, ProblemUpdateDTO, TestCaseDTO
from src.logger import logger


__all__ = [
    "ShowTeacherCourseTagsToRateStudents",
    "ShowTeacherCourseModulesToRateStudents",
    "UpdateCourseData",
    "CreateModules",
    "UpdateModules",
    "DeleteModules",
    "CreateProblem",
    "UpdateProblem",
    "DeleteProblems",
    "UpdateTags",
    "DeleteTags",
    "AddStudents",
    "DeleteStudents",
    "GenerateInviteLink",
    "ShowTeacherCourseData",
    "ShowStudentProblems",
    "ShowProblemStudents"
]


class _CourseRepoRelatedUseCase(ABC):
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
    ):
        self._uow = uow
        self._course_repo = course_repo


class ShowTeacherCourseTagsToRateStudents(_CourseRepoRelatedUseCase):
    async def execute(self, course_id: int):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._students], [Course._tags, Tag.students])
        return course


class ShowTeacherCourseModulesToRateStudents(_CourseRepoRelatedUseCase):
    async def execute(self, course_id: int):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._modules, Module._problems])
        return course


class ShowTeacherCourseData(_CourseRepoRelatedUseCase):
    async def execute(self, course_id: int):
        async with self._uow:
            return await self._course_repo.get_by_id(course_id)


class UpdateCourseData(_CourseRepoRelatedUseCase):
    async def execute(self, course_id: int, dto: CourseUpdateDTO):
        async with self._uow:
            course = await self._course_repo.get_by_id(course_id)
            if not course:
                raise UndefinedCourseError("Course does not exist")
            if dto.name:
                course.name = dto.name
            if dto.is_private is not None:
                course.is_private = dto.is_private
            if dto.description:
                course.description = dto.description
            if dto.notify_request_sub is not None:
                course.notify_request_sub = dto.notify_request_sub


class UpdateModules(_CourseRepoRelatedUseCase):
    async def execute(self, course_id: int, data: list[ModuleUpdateDTO]):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._modules])
            for module_data in data:
                module = course.get_module_by_id(module_data.id)
                if not module:
                    raise UndefinedModuleError(
                        f"Module with name '{module_data.name}' does not exist but retrieved to update")
                if module_data.name:
                    module.name = module_data.name
                if module_data.order:
                    module.order = module_data.order


class CreateModules(_CourseRepoRelatedUseCase):
    async def execute(self, course_id: int, data: list[ModuleCreateDTO]):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._modules])
            to_add = []
            for module_data in data:
                to_add.append(Module(module_data.name, course.id, module_data.order))
            module_manager = CourseModulesManagerService(course)
            module_manager.add_modules(to_add)


class DeleteModules:
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface
    ):
        self._uow = uow
        self._course_repo = course_repo

    async def execute(self, course_id: int, modules_ids: list[int]):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._modules])
            manager = CourseModulesManagerService(course)  # type: ignore
            manager.delete_modules(modules_ids)


class _ProblemCreateUpdateUseCase(ABC):
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface
    ):
        self._uow = uow
        self._course_repo = course_repo

    def _map_test_cases(self, cases_dto: dict[int, TestCaseDTO]) -> TestCases:
        prepared = {k: TestCase(case_data.input, case_data.output) for k, case_data in cases_dto.items()}
        return TestCases(prepared)


class UpdateProblem(_ProblemCreateUpdateUseCase):
    async def execute(self, course_id: int, module_id: int, problem_id: int, data: ProblemUpdateDTO):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._modules, Module._problems])
            module = course.get_module_by_id(module_id)
            if not module:
                raise UndefinedModuleError("Module does not exist", status=404)
            problem = module.get_problem_by_id(problem_id)
            if not problem:
                raise UndefinedProblemError(f"Problem does not exist", status=404)
            if data.name:
                problem.name = data.name
            if data.description:
                problem.description = data.description
            if data.auto_pass is not None:
                problem.auto_pass = data.auto_pass
            if data.show_test_cases is not None:
                problem.show_test_cases = data.show_test_cases
            if data.test_cases:
                problem.test_cases = self._map_test_cases(data.test_cases)


class CreateProblem(_ProblemCreateUpdateUseCase):
    async def execute(self, course_id: int, module_id: int, data: ProblemCreateDTO):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._modules, Module._problems])
            module = course.get_module_by_id(module_id)
            if not module:
                raise UndefinedModuleError("Module does not exist", status=404)
            created = Problem(
                data.name,
                module.id,
                data.description,
                data.auto_pass,
                data.show_test_cases,
                self._map_test_cases(data.test_cases)
            )
            problem_manager = CourseProblemManagerService(course)
            problem_manager.add_problems(module, [created])


class DeleteProblems:
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface
    ):
        self._uow = uow
        self._course_repo = course_repo

    async def execute(self, course_id: int, dto: DeleteProblemsDTO):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(
                course_id,
                [Course._modules, Module._problems]
            )
            manager = CourseProblemManagerService(course)  # type: ignore
            manager.delete_problems(dto.module_name, dto.problems_ids)


class UpdateTags:
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
        user_repo: UserRepositoryInterface
    ):
        self._uow = uow
        self._course_repo = course_repo
        self._user_repo = user_repo
    # TODO

    async def execute(self, course_id: int, data: list[TagsCreateUpdate]):
        async with self._uow as uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._tags, Tag.students], [Course._students])
            for tag_data in data:
                if tag_data.id:
                    tag = course.get_tag_by_id(tag_data.id)
                    if not tag:
                        raise UndefinedTagError("pass")


class DeleteTags:
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
    ):
        self._uow = uow
        self._course_repo = course_repo

    async def execute(self, course_id: int, tags_ids: list[int]):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._tags])
            manager = CourseTagManagerService(course)  # type: ignore
            manager.delete_tags(tags_ids)


class AddStudents:
    def __init__(
            self,
            uow: UoWInterface,
            course_repo: CourseRepositoryInterface,
            user_repo: UserRepositoryInterface
    ):
        self._uow = uow
        self._course_repo = course_repo
        self._user_repo = user_repo

    async def execute(self, course_id: int, dto: AddStudentsDTO):
        async with self._uow:
            students = await self._user_repo.get_by_ids(dto.student_ids)
            if not students:
                raise undefinedStudentError("Students does not exist")
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._tags, Tag.students], [Course._students])
            manager = CourseStudentsManagerService(course)  # type: ignore
            if dto.tag_name:
                manager.add_students_by_tag(dto.tag_name, students)
            else:
                manager.add_students(students)


class DeleteStudents:
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
        user_repo: UserRepositoryInterface
    ):
        self._uow = uow
        self._course_repo = course_repo
        self._user_repo = user_repo

    async def execute(self, course_id: int, dto: DeleteStudentsDTO):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._tags, Tag.students], [Course._students])
            manager = CourseStudentsManagerService(course)  # type: ignore
            manager.delete_students(dto.students_ids)


class GenerateInviteLink:
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
        confirm_subscription_url: str,
        link_exp_time: int,
        token_service: AuthenticationServiceInterface
    ):
        self._uow = uow
        self._course_repo = course_repo
        self._confirm_subscription_url = confirm_subscription_url
        self._token_service = token_service
        self._exp_time = link_exp_time

    async def execute(self, course_id: int, dto: GenLinkDTO):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._tags])
        payload = {"course_id": course.id}  # type: ignore
        target_tags = []
        for tag_name in dto.tags_names:
            if tag_name in DefautTagType.names():
                raise ImpossibleOperationError("Unable to create link for default tag")
            tag = course.get_tag(tag_name)  # type: ignore
            if tag and (tag_name not in target_tags):
                target_tags.append(tag.name)
        payload.update({"tags_names": target_tags})
        return self._confirm_subscription_url + f"/{self._token_service.encode(payload, self._exp_time)}"


class ShowStudentProblems:
    def __init__(
        self,
        uow: UoWInterface,
        attempt_repo: AttemptRepositoryInterface,
        module_repo: ModuleRepositoryInterface
    ):
        self._uow = uow
        self._attempt_repo = attempt_repo
        self._module_repo = module_repo

    async def execute(self, course_id: int, student_id: int) -> tuple[list[Attempt], list[Module]]:
        async with self._uow:
            attempts = await self._attempt_repo.get_student_attempts(course_id, student_id)
            modules_ids = [attempt.problem.module_id for attempt in attempts]
            modules = await self._module_repo.get_by_ids(modules_ids)
        return attempts, modules


class ShowProblemStudents:
    def __init__(
        self,
        uow: UoWInterface,
        attempt_repo: AttemptRepositoryInterface,
        module_repo: ModuleRepositoryInterface
    ):
        self._uow = uow
        self._attempt_repo = attempt_repo
        self._module_repo = module_repo

    async def execute(self, problem_id: int):
        async with self._uow:
            students = await self._attempt_repo.get_problem_students(problem_id)
        return students
