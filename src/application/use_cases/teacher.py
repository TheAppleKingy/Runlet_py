from src.domain.entities import Course, Problem, Module, Tag
from src.domain.value_objects import TestCases, TestCase
from src.domain.services.course import CourseTagManagerService, CourseStudentsManagerService
from src.application.interfaces.uow import UoWInterface
from src.application.interfaces.services import AuthenticationServiceInterface
from src.application.interfaces.repositories import CourseRepositoryInterface, UserRepositoryInterface
from src.application.use_cases.exceptions import UndefinedCourseError
from src.application.dtos.teacher import (
    CreateModuleDTO,
    UpdateCourseDTO,
    CreateCourseTagsDTO,
    DeleteStudentsFromCourseDTO,
    GenerateInviteLinkDTO
)
from src.logger import logger


__all__ = [
    "AddProblemsModules",
    "UpdateCourseData",
    "AddCourseTags",
    "ShowTeacherCourseToManageStudents",
    "ShowTeacherCourseToManageProblems",
    "GenerateInviteLink"
]


class ShowTeacherCourseToManageStudents:
    def __init__(self, uow: UoWInterface, course_repo: CourseRepositoryInterface):
        self._uow = uow
        self._course_repo = course_repo

    async def execute(self, course_id: int):
        async with self._uow:
            # or split to load modules and problems/students, tags and students differentely?
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._tags, Tag.students])
        return course


class ShowTeacherCourseToManageProblems:
    def __init__(self, uow: UoWInterface, course_repo: CourseRepositoryInterface):
        self._uow = uow
        self._course_repo = course_repo

    async def execute(self, course_id: int):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._modules, Module._problems])
        return course


class AddProblemsModules:
    def __init__(
        self,
        uow: UoWInterface,
    ):
        self._uow = uow

    async def execute(self, course_id: int, dto: CreateModuleDTO):
        async with self._uow as uow:
            module = Module(dto.name, course_id)
            uow.save(module)
            await uow.flush()
            if dto.problems:
                problems = [
                    Problem(
                        data.name,
                        data.description,
                        module.id,
                        data.auto_pass,
                        data.show_test_cases,
                        TestCases(
                            {
                                num: TestCase.from_dict(model.model_dump()) for num, model in data.test_cases.items()
                            }
                        )
                    ) for data in dto.problems
                ]
                uow.save(*problems)


class UpdateCourseData:
    def __init__(self, uow: UoWInterface, course_repo: CourseRepositoryInterface):
        self._uow = uow
        self._course_repo = course_repo

    async def execute(self, course_id: int, dto: UpdateCourseDTO):
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


class AddCourseTags:
    def __init__(self, uow: UoWInterface, course_repo: CourseRepositoryInterface, user_repo: UserRepositoryInterface):
        self._uow = uow
        self._course_repo = course_repo
        self._user_repo = user_repo

    async def execute(self, course_id: int, dto: CreateCourseTagsDTO):
        async with self._uow as uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._tags, Tag.students])
            if not course:
                raise UndefinedCourseError("Course does not exist")
            tag_manager = CourseTagManagerService(course)
            tags = [Tag(data.name, course_id) for data in dto.tags_data]
            tag_manager.add_tags(tags)
            uow.save(*tags)
            student_manager = CourseStudentsManagerService(course)
            for data in dto.tags_data:
                students = await self._user_repo.get_by_ids(data.students_ids)
                if students:
                    student_manager.add_students_by_tag(data.name, students)


class DeleteStudentsFromCourse:
    def __init__(self, uow: UoWInterface, course_repo: CourseRepositoryInterface, user_repo: UserRepositoryInterface):
        self._uow = uow
        self._course_repo = course_repo
        self._user_repo = user_repo

    async def execute(self, course_id: int, dto: DeleteStudentsFromCourseDTO):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._tags, Tag.students])
            if not course:
                raise UndefinedCourseError("Course does not exist")
            manager = CourseStudentsManagerService(course)
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

    async def execute(self, course_id: int, dto: GenerateInviteLinkDTO):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._tags])
        payload = {"course_id": course.id}  # type: ignore
        if dto.tag_name:
            tag = course.get_tag(dto.tag_name)  # type: ignore
            if tag:
                payload.update({"tag_name": tag.name})
        return self._confirm_subscription_url + f"/{self._token_service.encode(payload, self._exp_time)}"
