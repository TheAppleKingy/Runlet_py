from typing import Optional

from runlet.domain.entities import (
    Course,
    Problem,
    Module,
    Tag,
    DefaultTagType,
    Attempt,
    User
)
from runlet.domain.value_objects import (
    TestCases,
    TestCase,
    Examples
)
from runlet.domain.services.course import (
    CourseTagManagerService,
    CourseStudentsManagerService,
    CourseModulesManagerService,
    CourseProblemManagerService
)
from runlet.application.interfaces.uow import UoWInterface
from runlet.application.interfaces.services import AuthenticationServiceInterface
from runlet.application.interfaces.repositories import (
    CourseRepositoryInterface,
    ModuleRepositoryInterface,
    AttemptRepositoryInterface,
    TagRepositoryInterface,
    UserRepositoryInterface
)
from runlet.application.interactors.exceptions import (
    UndefinedCourseError,
    ImpossibleOperationError,
    undefinedStudentError,
    UndefinedModuleError,
    UndefinedProblemError,
    UndefinedTagError,
    UndefinedAttemptError
)
from runlet.application.dtos.teacher import (
    GenLinkDTO,
    DeleteProblemsDTO,
    UpdateTagStudentsDTO,
    ManageModulesDTO,
    ManageTagsDTO
)
from runlet.application.dtos.course import (
    CourseUpdateDTO
)

from runlet.application.dtos.problem import (
    CreateUpdateProblemDTO,
    TestCaseDTO
)

from .base import (
    _CourseRepoRelatedInteractor,
    _CourseUserReposRelatedInteractor,
    _CourseAttemptReposRelatedInteractor,
    _CourseAttemptUserRepoRelatedInteractor,
    _AttemptUserRepoRelatedInteractor
)


class ShowTeacherCourseTagsToRateStudents(_CourseAttemptUserRepoRelatedInteractor):
    async def __call__(
        self,
        course_id: int,
        tag_id: Optional[int],
        page: int = 1,
        size: int = 12
    ) -> tuple[Course, list[tuple[User, Optional[Attempt]]], int, Optional[Tag]]:
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._tags])
            tag: Optional[Tag] = None
            if tag_id:
                tag = course.get_tag_by_id(tag_id)
                if not tag:
                    raise UndefinedTagError("Tag does not exist or not related to course")
                students, pages = await self._user_repo.get_paginated_by_tag(course_id, tag_id, page=page, size=size)
            else:
                students, pages = await self._user_repo.get_paginated_by_course(course_id, page=page, size=size)
            attempts = await self._attempt_repo.get_attempts_of_students([s.id for s in students])
            attempts_map = {a.user_id: a for a in attempts}
        return course, [(s, attempts_map.get(s.id)) for s in students], pages, tag  # type: ignore[return-value]


class ShowTeacherCourseModulesToRateStudents(_CourseAttemptReposRelatedInteractor):
    async def __call__(self, course_id: int) -> tuple[Course, list[int]]:  # type: ignore[return]
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(
                course_id,
                [Course._modules, Module._problems]
            )
            unseen_problems_ids = await self._attempt_repo.get_problems_ids_with_unseen_attempts(
                course.id  # type: ignore[union-attr]
            )
            return course, unseen_problems_ids  # type: ignore[return-value]


class ShowCourseModulesProblemsToUpdate(_CourseRepoRelatedInteractor):
    async def __call__(self, course_id: int):
        async with self._uow:
            return await self._course_repo.get_by_id_with_rels(course_id, [Course._modules, Module._problems])


class ShowTeacherCourseData(_CourseRepoRelatedInteractor):
    async def __call__(self, course_id: int):
        async with self._uow:
            return await self._course_repo.get_by_id(course_id)


class UpdateCourseData(_CourseRepoRelatedInteractor):
    async def __call__(self, course_id: int, dto: CourseUpdateDTO):
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


class ManageModules(_CourseRepoRelatedInteractor):
    async def __call__(self, course_id: int, dto: ManageModulesDTO):
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


class CreateUpdateProblem(_CourseRepoRelatedInteractor):
    def _map_test_cases(self, cases_dto: list[TestCaseDTO]) -> TestCases:
        prepared = {case_data.test_num: TestCase(case_data.input, case_data.output) for case_data in cases_dto}
        return TestCases(prepared)

    async def __call__(self, course_id: int, dto: CreateUpdateProblemDTO):
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


class DeleteProblems(_CourseRepoRelatedInteractor):
    async def __call__(self, course_id: int, data: list[DeleteProblemsDTO]):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(
                course_id,
                [Course._modules, Module._problems]
            )
            manager = CourseProblemManagerService(course)  # type: ignore
            for delete_data in data:
                manager.delete_problems(delete_data.module_id, delete_data.problems_ids)


class ManageTags(_CourseRepoRelatedInteractor):
    async def __call__(self, course_id: int, dto: ManageTagsDTO) -> list[Tag]:
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


class DeleteTags(_CourseRepoRelatedInteractor):
    async def __call__(self, course_id: int, tags_ids: list[int]):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._tags])
            manager = CourseTagManagerService(course)  # type: ignore
            manager.delete_tags(tags_ids)


class ManageStudents(_CourseUserReposRelatedInteractor):
    async def __call__(self, course_id: int, data: list[UpdateTagStudentsDTO]):
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


class GenerateInviteLink(_CourseRepoRelatedInteractor):
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
        confirm_subscription_url: str,
        link_exp_time: int,
        token_service: AuthenticationServiceInterface
    ):
        super().__init__(uow, course_repo)
        self._confirm_subscription_url = confirm_subscription_url
        self._token_service = token_service
        self._exp_time = link_exp_time

    async def __call__(self, course_id: int, dto: GenLinkDTO):
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


class ShowStudentProblems(_CourseAttemptReposRelatedInteractor):
    def __init__(
        self,
        uow: UoWInterface,
        attempt_repo: AttemptRepositoryInterface,
        module_repo: ModuleRepositoryInterface,
        course_repo: CourseRepositoryInterface
    ):
        super().__init__(uow, course_repo, attempt_repo)
        self._module_repo = module_repo

    async def __call__(self, course_id: int, student_id: int) -> tuple[list[Attempt], list[Module]]:
        async with self._uow:
            if not await self._course_repo.check_user_in_course(student_id, course_id):
                raise undefinedStudentError("Student is not subscribed on course")
            attempts = await self._attempt_repo.get_student_attempts(course_id, student_id)
            modules_ids = [attempt.problem.module_id for attempt in attempts]
            modules = await self._module_repo.get_by_ids(modules_ids)
        return attempts, modules


class ShowProblemStudents(_CourseAttemptReposRelatedInteractor):
    async def __call__(
        self,
        course_id: int,
        module_id: int,
        problem_id: int,
        page: int = 1,
        size: int = 7
    ) -> tuple[list[tuple[User, Attempt]], int]:
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._modules, Module._problems])
            module = course.get_module_by_id(module_id)
            if not module:
                raise UndefinedModuleError("Module does not exist or not related to course")
            problem = module.get_problem_by_id(problem_id)
            if not problem:
                raise UndefinedProblemError("Problem does not exist or not related to module")
            return await self._attempt_repo.get_problem_paginated_students_with_attempts(problem_id, page=page, size=size)


class ShowTagsToUpdate(_CourseUserReposRelatedInteractor):
    async def __call__(
        self,
        course_id: int,
        tag_id: int,
        course_students_page: int = 1,
        course_students_size: int = 7,
        tag_students_page: int = 1,
        tag_students_size: int = 7
    ) -> tuple[list[User], int, list[User], int, Tag]:
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._tags])
            course_students, course_students_pages = await self._user_repo.get_paginated_by_course(  # TODO: cache
                course_id,
                page=course_students_page,
                size=course_students_size
            )
            tag = course.get_tag_by_id(tag_id)
            if not tag:
                raise UndefinedTagError("Tag does not exist or not related to course")
            tag_students, tag_students_pages = await self._user_repo.get_paginated_by_tag(
                course_id,
                tag_id,
                page=tag_students_page,
                size=tag_students_size
            )
        return course_students, course_students_pages, tag_students, tag_students_pages, tag


class ShowProblemDataToUpdate(_CourseRepoRelatedInteractor):
    async def __call__(self, course_id: int, module_id: int, problem_id: int) -> Problem:  # type: ignore[return]
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._modules, Module._problems])
            module = course.get_module_by_id(module_id)  # type: ignore[union-attr]
            if not module:
                raise UndefinedModuleError("Module does not exist or not related to course", status=404)
            problem = module.get_problem_by_id(problem_id)
            if not problem:
                raise UndefinedProblemError("Problem does not exist or not related to module", status=404)
            return problem


class SearchStudents:
    def __init__(
        self,
        uow: UoWInterface,
        user_repo: UserRepositoryInterface
    ):
        self._uow = uow
        self._user_repo = user_repo

    async def __call__(
        self,
        course_id: int,
        namelike: str,
        tag_id: Optional[int],
        page: int = 1,
        size: int = 10
    ) -> tuple[list[User], int]:  # type: ignore[return]
        async with self._uow:
            return await self._user_repo.find_by_name(course_id, namelike, tag_id=tag_id, page=page, size=size)


class SearchStudentsWithSeens(_AttemptUserRepoRelatedInteractor):
    async def __call__(self, course_id, namelike, tag_id, page=1, size=10):
        async with self._uow:
            students, pages = await self._user_repo.find_by_name(course_id, namelike, tag_id=tag_id, page=page, size=size)
            attempts = await self._attempt_repo.get_attempts_of_students([s.id for s in students])
        return students, attempts, pages


class ShowStudentProblemInfoToRate(_CourseAttemptReposRelatedInteractor):
    async def __call__(  # type: ignore[return]
        self,
        course_id: int,
        module_id: int,
        problem_id: int,
        student_id: int,
        *args
    ) -> Attempt:
        async with self._uow:
            if not await self._course_repo.check_user_in_course(student_id, course_id):
                raise undefinedStudentError("User does not exist or not subscribed on course", status=404)
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._modules, Module._problems])
            module = course.get_module_by_id(module_id)  # type: ignore[union-attr]
            if not module:
                raise UndefinedModuleError("Module does not exist or not related to course", status=404)
            attempt = await self._attempt_repo.get_student_attempt(course_id, student_id, problem_id)
            if not attempt:
                raise UndefinedAttemptError("Problem does not exist or student did not try to solve", status=404)
            attempt.watch()
            return attempt


class RateStudent(ShowStudentProblemInfoToRate):
    async def __call__(
        self,
        course_id: int,
        module_id: int,
        problem_id: int,
        student_id: int,
        ok: bool
    ):
        attempt = await super().__call__(course_id, module_id, problem_id, student_id)
        async with self._uow:
            attempt.teacher_confirm(ok)
