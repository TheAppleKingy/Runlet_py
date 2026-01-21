from typing import Optional

from src.domain.entities import Course, DefautTagType, Tag
from src.domain.services import CourseStudentsManagerService, CourseTagManagerService
from src.application.interfaces.repositories import (
    UserRepositoryInterface,
    CourseRepositoryInterface,
    ProblemRepositoryInterface
)
from src.application.interfaces.uow import UoWInterface
from src.application.interfaces.services import (
    EmailMessageTextTemplate,
    EmailServiceInterface,
    AuthenticationServiceInterface
)
from src.application.use_cases.exceptions import (
    UndefinedCourseError,
    InvalidInvitingLinkError,
    CoursePrivacyError,
)
from src.application.dtos.course import CreateCourseDTO

__all__ = [
    "ShowCourse",
    "ShowMain",
    "CreateCourse",
    "RequestSubscribeOnCourse",
    "SubscribeOnCourse",
    "SubscribeOnCourseByLink"
]


class ShowMain:
    def __init__(self, uow: UoWInterface, course_repo: CourseRepositoryInterface):
        self._uow = uow
        self._course_repo = course_repo

    async def execute(self, user_id: Optional[int], page: int = 1, size: int = 10):
        as_student = []
        as_teacher = []
        async with self._uow:
            paginated = await self._course_repo.get_all_paginated(page=page, size=size)
            if user_id:
                as_student = await self._course_repo.get_student_courses(user_id)
                as_teacher = await self._course_repo.get_teacher_courses(user_id)
        return as_teacher, as_student, paginated


class ShowCourse:
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface
    ):
        self._uow = uow
        self._course_repo = course_repo

    async def execute(self, course_id: int):
        async with self._uow:
            course = await self._course_repo.get_by_id(course_id)
        return course


class CreateCourse:
    def __init__(
        self,
        uow: UoWInterface,
    ):
        self._uow = uow

    async def execute(self, user_id: int, dto: CreateCourseDTO):
        async with self._uow as uow:
            course = Course(dto.name, user_id, dto.description,
                            dto.is_private, dto.notify_request_sub)
            uow.save(course)
            await uow.flush()
            default_tags = [Tag(DefautTagType.WAITING_FOR_SUBSCRIBE.value, course.id)]
            uow.save(*default_tags)
            manager = CourseTagManagerService(course)
            manager.add_tags(default_tags)


class RequestSubscribeOnCourse:
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
        user_repo: UserRepositoryInterface,
        email_service: EmailServiceInterface
    ):
        self._uow = uow
        self._course_repo = course_repo
        self._user_repo = user_repo
        self._email_service = email_service

    async def execute(self, course_id: int, user_id: int):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._tags], [Course._students])
            if not course:
                raise UndefinedCourseError("Course does not exist")
            if not course.is_private:
                raise CoursePrivacyError("Course is not private")
            user = await self._user_repo.get_by_id(user_id)  # type: ignore
            manager = CourseStudentsManagerService(course)
            manager.add_students_by_tag(
                DefautTagType.WAITING_FOR_SUBSCRIBE.value, [user])  # type: ignore
        topic, msg = EmailMessageTextTemplate.notify_student_requested_subscribe(
            course.name)  # type: ignore
        await self._email_service.send_mail(user.email, topic, msg)  # type: ignore
        if course.notify_request_sub:  # type: ignore
            async with self._uow:
                admin = await self._user_repo.get_by_id(course.teacher_id)  # type: ignore
                topic, msg = EmailMessageTextTemplate.notify_teacher_requested_subscribe(
                    user.email, course.name)  # type: ignore
                await self._email_service.send_mail(admin.email, topic, msg)  # type: ignore


class SubscribeOnCourse:
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
        user_repo: UserRepositoryInterface,
        email_service: EmailServiceInterface
    ):
        self._uow = uow
        self._course_repo = course_repo
        self._user_repo = user_repo
        self._email_service = email_service

    async def execute(self, user_id: int, course_id: int):
        async with self._uow:
            # only authorized users be able to subscribe on course therefore, don't need to check whether user exists or not.
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._students])
            if not course:
                raise UndefinedCourseError("Course does not exist")
            if course.is_private:
                raise CoursePrivacyError("Course is private")
            user = await self._user_repo.get_by_id(user_id)
            manager = CourseStudentsManagerService(course)
            manager.add_students([user])  # type: ignore
        topic, msg = EmailMessageTextTemplate.notify_student_subscribed(course.name)  # type: ignore
        await self._email_service.send_mail(user.email, topic, msg)  # type: ignore


class SubscribeOnCourseByLink:
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
        user_repo: UserRepositoryInterface,
        auth_service: AuthenticationServiceInterface,
        email_service: EmailServiceInterface
    ):
        self._uow = uow
        self._course_repo = course_repo
        self._user_repo = user_repo
        self._token_service = auth_service
        self._email_service = email_service

    async def execute(self, token: str, user_id: int):
        try:
            payload = self._token_service.decode(token)
        except Exception:
            raise InvalidInvitingLinkError("Inviting URL is invalid", 404)
        tags_names = payload.get("tags_names", [])
        course_id = payload.get("course_id")
        if not course_id:
            raise InvalidInvitingLinkError("Inviting URL is invalid", 404)
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._tags, Tag.students])
            if not course:
                raise InvalidInvitingLinkError("Inviting URL is invalid", 404)
            if await self._course_repo.check_user_in_course(user_id, course.id):
                raise InvalidInvitingLinkError("Already subscribed on course")
            student = await self._user_repo.get_by_id(user_id)
            manager = CourseStudentsManagerService(course)
            if tags_names:
                for tag_name in tags_names:
                    manager.add_students_by_tag(tag_name, [student])  # type: ignore
            else:
                manager.add_students([student])  # type: ignore
        topic, msg = EmailMessageTextTemplate.notify_student_subscribed(course.name)  # type: ignore
        await self._email_service.send_mail(student.email, topic, msg)  # type: ignore
