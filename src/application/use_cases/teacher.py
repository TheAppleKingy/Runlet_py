from typing import Optional
from abc import ABC

from src.domain.entities import (
    Course,
    Problem,
    Module,
    Tag,
    DefaultTagType,
    Attempt,
    User
)
from src.domain.value_objects import (
    TestCases,
    TestCase,
    Examples
)
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
    GenLinkDTO,
    DeleteProblemsDTO,
    UpdateTagStudentsDTO,
    ManageModulesDTO,
    ManageTagsDTO
)
from src.application.dtos.course import (
    CourseUpdateDTO
)

from src.application.dtos.problem import (
    CreateUpdateProblemDTO,
    TestCaseDTO
)


class _CourseRepoRelatedUseCase(ABC):
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
    ):
        self._uow = uow
        self._course_repo = course_repo


class ShowTeacherCourseTagsToRateStudents(_CourseRepoRelatedUseCase):
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
        user_repo: UserRepositoryInterface
    ):
        super().__init__(uow, course_repo)
        self._user_repo = user_repo

    async def execute(self, course_id: int) -> tuple[Course, list[tuple[User, Optional[bool]]]]:
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._students], [Course._tags, Tag.students])
            students_seens = await self._user_repo.get_by_id_with_attempts_seen_info(course_id)
        return course, students_seens


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


class ManageModules(_CourseRepoRelatedUseCase):
    async def execute(self, course_id: int, dto: ManageModulesDTO):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._modules])
            module_manager = CourseModulesManagerService(course)  # type: ignore[arg-type]
            to_add = []
            module_manager.delete_modules(dto.to_delete)
            for module_data in dto.to_create_update:
                if module_data.id:
                    module = course.get_module_by_id(module_data.id)  # type: ignore[union-attr]
                    if not module:
                        raise UndefinedModuleError(
                            f"Module '{module_data.name}' does not exist")
                    module.name = module_data.name
                    module.order = module_data.order
                else:
                    to_add.append(Module(module_data.name, course.id, module_data.order))  # type: ignore[union-attr]
            module_manager.add_modules(to_add)


class _ProblemCreateUpdateUseCase(ABC):
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface
    ):
        self._uow = uow
        self._course_repo = course_repo

    def _map_test_cases(self, cases_dto: list[TestCaseDTO]) -> TestCases:
        prepared = {case_data.test_num: TestCase(case_data.input, case_data.output) for case_data in cases_dto}
        return TestCases(prepared)


class CreateUpdateProblem(_ProblemCreateUpdateUseCase):
    async def execute(self, course_id: int, dto: CreateUpdateProblemDTO):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._modules, Module._problems])
            module = course.get_module_by_id(dto.module_id)  # type: ignore
            if not module:
                raise UndefinedModuleError("Module does not exist or not related to course")
            if dto.id:
                problem = module.get_problem_by_id(dto.id)
                if not problem:
                    raise UndefinedProblemError(f"Problem '{dto.name}' does not exist")
                problem.name = dto.name
                problem.description = dto.description
                problem.auto_pass = dto.auto_pass
                problem.show_test_cases = dto.show_test_cases
                problem.test_cases = self._map_test_cases(dto.test_cases)
                problem.examples = Examples([TestCase(case.input, case.output) for case in dto.examples])
            else:
                created = Problem(
                    dto.name,
                    module.id,
                    dto.description,
                    dto.auto_pass,
                    dto.show_test_cases,
                    self._map_test_cases(dto.test_cases),
                    Examples([TestCase(case.input, case.output) for case in dto.examples])
                )
                problem_manager = CourseProblemManagerService(course)  # type: ignore[arg-type]
                problem_manager.add_problems(module, [created])


class DeleteProblems:
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface
    ):
        self._uow = uow
        self._course_repo = course_repo

    async def execute(self, course_id: int, data: list[DeleteProblemsDTO]):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(
                course_id,
                [Course._modules, Module._problems]
            )
            manager = CourseProblemManagerService(course)  # type: ignore
            for delete_data in data:
                manager.delete_problems(delete_data.module_id, delete_data.problems_ids)


class ManageTags:
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
    ):
        self._uow = uow
        self._course_repo = course_repo

    async def execute(self, course_id: int, dto: ManageTagsDTO) -> list[Tag]:
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._tags])
            to_add = []
            tag_manager = CourseTagManagerService(course)  # type: ignore[arg-type]
            tag_manager.delete_tags(dto.to_delete)
            for tag_data in dto.to_create_update:
                if tag_data.id:
                    tag = course.get_tag_by_id(tag_data.id)  # type: ignore
                    if not tag:
                        raise UndefinedTagError(f"Tag '{tag_data.name}' does not exist")
                    tag.name = tag_data.name
                else:
                    to_add.append(Tag(tag_data.name, course.id))  # type: ignore[union-attr]
            tag_manager.add_tags(to_add)
        return to_add  # returns created with id


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


class ManageStudents:
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
        user_repo: UserRepositoryInterface
    ):
        self._uow = uow
        self._course_repo = course_repo
        self._user_repo = user_repo

    async def execute(self, course_id: int, data: list[UpdateTagStudentsDTO]):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._tags, Tag.students], [Course._students])
            manager = CourseStudentsManagerService(course)  # type: ignore
            for add_data in data:
                if add_data.to_delete:
                    if add_data.tag_id:
                        manager.delete_students_from_tag(add_data.tag_id, add_data.to_delete)
                    else:
                        manager.delete_students(add_data.to_delete)
                if add_data.to_add:
                    students = await self._user_repo.get_by_ids(add_data.to_add)
                    if not students:
                        raise undefinedStudentError("Students does not exist for adding to tag")
                    if add_data.tag_id:
                        manager.add_students_by_tag(add_data.tag_id, students)
                    else:
                        manager.add_students(students)


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
        target_ids = []
        for tag_id in dto.tags_ids:
            tag = course.get_tag_by_id(tag_id)  # type: ignore
            if not tag:
                raise UndefinedTagError("Tag does not exist")
            if tag.name in DefaultTagType.names():
                raise ImpossibleOperationError("Unable to create link for default tag")
            if tag.id not in target_ids:
                target_ids.append(tag.id)
        payload.update({"tags_ids": target_ids})
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
    ):
        self._uow = uow
        self._attempt_repo = attempt_repo

    async def execute(self, problem_id: int):
        async with self._uow:
            students = await self._attempt_repo.get_problem_students(problem_id)
        return students


class ShowTagsToUpdate(_CourseRepoRelatedUseCase):
    async def execute(self, course_id: int):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._students], [Course._tags, Tag.students])
        return course.students, course.tags  # type: ignore[union-attr]


class ShowProblemDataToUpdate(_CourseRepoRelatedUseCase):
    async def execute(self, course_id: int, module_id: int, problem_id: int) -> Problem:  # type: ignore[return]
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._modules, Module._problems])
            module = course.get_module_by_id(module_id)  # type: ignore[union-attr]
            if not module:
                raise UndefinedModuleError("Module does not exist", status=404)
            problem = module.get_problem_by_id(problem_id)
            if not problem:
                raise UndefinedProblemError("Problem does not exist", status=404)
            return problem


class SearchStudents(_CourseRepoRelatedUseCase):
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
        user_repo: UserRepositoryInterface
    ):
        super().__init__(uow, course_repo)
        self._user_repo = user_repo

    async def execute(
        self,
        course_id: int,
        namelike: str,
        tag_id: Optional[int] = None
    ) -> list[User]:  # type: ignore[return]
        async with self._uow:
            res = await self._user_repo.find_by_name(course_id, namelike, tag_id=tag_id)
        return res
