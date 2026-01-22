from src.domain.entities import Course, Problem, Module, Tag, DefautTagType
from src.domain.value_objects import TestCases, TestCase
from src.domain.services.course import (
    CourseTagManagerService,
    CourseStudentsManagerService,
    CourseModulesManagerService,
    CourseProblemManagerService
)
from src.application.interfaces.uow import UoWInterface
from src.application.interfaces.services import AuthenticationServiceInterface
from src.application.interfaces.repositories import CourseRepositoryInterface, UserRepositoryInterface
from src.application.use_cases.exceptions import (
    UndefinedCourseError,
    ImpossibleOperationError,
    undefinedStudentError
)
from src.application.dtos.teacher import (
    AddTagsDTO,
    GenLinkDTO,
    AddProblemDTO,
    DeleteProblemsDTO,
    AddStudentsDTO,
    DeleteStudentsDTO,
)
from src.application.dtos.course import (
    CourseC1
)
from src.logger import logger


__all__ = [
    "ShowTeacherCourseToManageStudents",
    "ShowTeacherCourseToManageProblems",
    "UpdateCourseData",
    "DeleteModules",
    "AddProblem",
    "DeleteProblems",
    "AddTags",
    "DeleteTags",
    "AddStudents",
    "DeleteStudents",
    "GenerateInviteLink"
]


class ShowTeacherCourseToManageStudents:
    def __init__(self, uow: UoWInterface, course_repo: CourseRepositoryInterface):
        self._uow = uow
        self._course_repo = course_repo

    async def execute(self, course_id: int):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._students], [Course._tags, Tag.students])
        return course


class ShowTeacherCourseToManageProblems:
    def __init__(self, uow: UoWInterface, course_repo: CourseRepositoryInterface):
        self._uow = uow
        self._course_repo = course_repo

    async def execute(self, course_id: int):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._modules, Module._problems])
        return course


class UpdateCourseData:
    def __init__(self, uow: UoWInterface, course_repo: CourseRepositoryInterface):
        self._uow = uow
        self._course_repo = course_repo

    async def execute(self, course_id: int, dto: CourseC1):
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


class AddProblem:
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface
    ):
        self._uow = uow
        self._course_repo = course_repo

    async def execute(self, course_id: int, dto: AddProblemDTO):
        async with self._uow as uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._modules, Module._problems])
            module = course.get_module(dto.module_name)  # type: ignore
            if not module:
                module = Module(dto.module_name, course_id)
                module_manager = CourseModulesManagerService(course)  # type: ignore
                module_manager.add_modules([module])
                uow.save(module)
                await uow.flush()
            problem_manager = CourseProblemManagerService(course)  # type: ignore
            new_problem = Problem(
                dto.problem_data.name,
                dto.problem_data.description,
                module.id,
                dto.problem_data.auto_pass,
                dto.problem_data.show_test_cases,
                TestCases(
                    {
                        data.test_num: TestCase.from_dict(
                            {
                                "input": data.input,
                                "output": data.output
                            }
                        ) for data in dto.problem_data.test_cases
                    }
                )
            )
            problem_manager.add_problems(module.name, [new_problem])
            uow.save(new_problem)


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


class AddTags:
    def __init__(
            self,
            uow: UoWInterface,
            course_repo: CourseRepositoryInterface,
            user_repo: UserRepositoryInterface
    ):
        self._uow = uow
        self._course_repo = course_repo
        self._user_repo = user_repo

    async def execute(self, course_id: int, dto: AddTagsDTO):
        async with self._uow as uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._tags, Tag.students], [Course._students])
            tag_manager = CourseTagManagerService(course)  # type: ignore
            tags = [Tag(data.name, course_id) for data in dto.tags_data]
            tag_manager.add_tags(tags)
            uow.save(*tags)
            student_manager = CourseStudentsManagerService(course)  # type: ignore
            for data in dto.tags_data:
                students = await self._user_repo.get_by_ids(data.students_ids)
                if not students:
                    raise UndefinedCourseError("Students do not exist")
                student_manager.add_students_by_tag(data.name, students)


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
            if tag_name in [type_.value for type_ in DefautTagType]:
                raise ImpossibleOperationError("Unable to create link for default tag")
            tag = course.get_tag(tag_name)  # type: ignore
            if tag and (tag_name not in target_tags):
                target_tags.append(tag.name)
        payload.update({"tags_names": target_tags})
        return self._confirm_subscription_url + f"/{self._token_service.encode(payload, self._exp_time)}"
