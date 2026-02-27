from typing import Optional

from runlet.domain.entities import (
    Course,
    DefaultTagType,
    Tag
)
from runlet.domain.services import (
    CourseStudentsManagerService,
    CourseTagManagerService
)
from runlet.application.interfaces.repositories import (
    UserRepositoryInterface,
    CourseRepositoryInterface,
)
from runlet.application.interfaces.uow import UoWInterface
from runlet.application.interfaces.services import (
    EmailMessageTextTemplate,
    EmailServiceInterface,
    AuthenticationServiceInterface
)
from runlet.application.interactors.exceptions import (
    UndefinedCourseError,
    InvalidInvitingLinkError,
    CoursePrivacyError,
    ImpossibleOperationError
)
from runlet.application.dtos.course import CourseCreateDTO
from .base import (
    _CourseRepoRelatedInteractor,
    _CourseUserReposRelatedInteractor
)


class ShowMain(_CourseRepoRelatedInteractor):
    async def __call__(
        self,
        user_id: Optional[int] = None,
        page: int = 1,
        size: int = 10
    ) -> tuple[list, list, tuple[list[Course], int, int, int]]:
        as_student = []
        as_teacher = []
        async with self._uow:
            paginated = await self._course_repo.get_all_paginated(page=page, size=size)
            if user_id:
                as_student = await self._course_repo.get_student_courses(user_id)
                as_teacher = await self._course_repo.get_teacher_courses(user_id)
        return as_teacher, as_student, paginated


class ShowMyProfile:
    def __init__(
        self,
        uow: UoWInterface,
        user_repo: UserRepositoryInterface
    ):
        self._uow = uow
        self._user_repo = user_repo

    async def __call__(self, user_id: int):
        async with self._uow:
            user = await self._user_repo.get_by_id(user_id)
        return user


class ShowCourse(_CourseRepoRelatedInteractor):
    async def __call__(self, course_id: int):
        async with self._uow:
            course = await self._course_repo.get_by_id(course_id)
            if not course:
                raise UndefinedCourseError("Course does not exist", status=404)
        return course


class CreateCourse:
    def __init__(
        self,
        uow: UoWInterface,
    ):
        self._uow = uow

    async def __call__(self, user_id: int, dto: CourseCreateDTO):
        async with self._uow as uow:
            course = Course(dto.name, user_id, dto.description,
                            dto.is_private, dto.notify_request_sub)
            uow.save(course)
            await uow.flush()
            default_tags = [Tag(type_.value, course.id) for type_ in DefaultTagType]
            uow.save(*default_tags)
            manager = CourseTagManagerService(course)
            manager.add_tags(default_tags)


class RequestSubscribeOnCourse(_CourseUserReposRelatedInteractor):
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
        user_repo: UserRepositoryInterface,
        email_service: EmailServiceInterface
    ):
        super().__init__(uow, course_repo, user_repo)
        self._email_service = email_service

    async def __call__(self, course_id: int, user_id: int):
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._tags, Tag.students], [Course._students])
            if not course:
                raise UndefinedCourseError("Course does not exist")
            if not course.is_private:
                raise CoursePrivacyError("Course is not private")
            user = await self._user_repo.get_by_id(user_id)  # type: ignore
            manager = CourseStudentsManagerService(course)
            manager.request_subscribe([user])  # type: ignore
        topic, msg = EmailMessageTextTemplate.notify_student_requested_subscribe(course.name)  # type: ignore
        await self._email_service.send_mail(user.email, topic, msg)  # type: ignore
        if course.notify_request_sub:  # type: ignore
            async with self._uow:
                admin = await self._user_repo.get_by_id(course.teacher_id)  # type: ignore
                topic, msg = EmailMessageTextTemplate.notify_teacher_requested_subscribe(
                    user.email, course.name)  # type: ignore
                await self._email_service.send_mail(admin.email, topic, msg)  # type: ignore


class SubscribeOnCourse(_CourseUserReposRelatedInteractor):
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
        user_repo: UserRepositoryInterface,
        email_service: EmailServiceInterface
    ):
        super().__init__(uow, course_repo, user_repo)
        self._email_service = email_service

    async def __call__(self, user_id: int, course_id: int):
        async with self._uow:
            # only authorized users be able to subscribe on course therefore, don't need to check whether user exists or not.
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._students], [Course._tags, Tag.students])
            if not course:
                raise UndefinedCourseError("Course does not exist", status=404)
            if course.is_private:
                raise CoursePrivacyError("Course is private")
            user = await self._user_repo.get_by_id(user_id)
            manager = CourseStudentsManagerService(course)
            manager.add_students([user])  # type: ignore
        topic, msg = EmailMessageTextTemplate.notify_student_subscribed(course.name)  # type: ignore
        await self._email_service.send_mail(user.email, topic, msg)  # type: ignore


class SubscribeOnCourseByLink(_CourseUserReposRelatedInteractor):
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
        user_repo: UserRepositoryInterface,
        auth_service: AuthenticationServiceInterface,
        email_service: EmailServiceInterface
    ):
        super().__init__(uow, course_repo, user_repo)
        self._token_service = auth_service
        self._email_service = email_service

    async def __call__(self, token: str, user_id: int):
        try:
            payload = self._token_service.decode(token)
        except Exception:
            raise InvalidInvitingLinkError("Inviting URL is invalid", status=404)
        tags_ids = payload.get("tags_ids", [])
        course_id = payload.get("course_id")
        if not course_id:
            raise InvalidInvitingLinkError("Inviting URL is invalid", status=404)
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, [Course._tags, Tag.students], [Course._students])
            if not course:
                raise UndefinedCourseError("Course does not exist", status=404)
            if await self._course_repo.check_user_in_course(user_id, course.id):
                raise InvalidInvitingLinkError("Already subscribed on course")
            student = await self._user_repo.get_by_id(user_id)
            manager = CourseStudentsManagerService(course)
            if tags_ids:
                for tag_id in tags_ids:
                    manager.add_students_by_tag(tag_id, [student])  # type: ignore
            else:
                manager.add_students([student])  # type: ignore
        topic, msg = EmailMessageTextTemplate.notify_student_subscribed(course.name)  # type: ignore
        await self._email_service.send_mail(student.email, topic, msg)  # type: ignore


class ShowFavourites(_CourseRepoRelatedInteractor):
    async def __call__(self, user_id: int) -> list[Course]:  # type: ignore[return]
        async with self._uow:
            return await self._course_repo.get_favourites_for(user_id)


class AddToFavourites(_CourseRepoRelatedInteractor):
    async def __call__(self, user_id: int, course_id: int):
        async with self._uow:
            course = await self._course_repo.get_by_id(course_id)
            if user_id == course.teacher_id:  # type: ignore[union-attr]
                raise ImpossibleOperationError("Cannot add course to favorites because you are the teacher")
            await self._course_repo.add_to_favourites(user_id, course_id)
