from src.domain.entities import Course, DefautTagType
from src.domain.services import CourseStudentsManagerService
from src.application.interfaces.repositories import UserRepositoryInterface, CourseRepositoryInterface, ProblemRepositoryInterface
from src.application.interfaces.uow import UoWInterface
from src.application.interfaces.services import EmailMessageTextTemplate, EmailServiceInterface, AuthenticationServiceInterface
from src.application.use_cases.exceptions import UndefinedCourseError, InvalidInvitingLingError


__all__ = [
    "ShowCourse",
    "RequestSubscribeOnCourse",
    "SubscribeOnCourse",
    "SubscribeOnCourseByLink"
]


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


class RequestSubscribeOnCourse:
    def __init__(
        self,
        uow: UoWInterface,
        problem_repo: ProblemRepositoryInterface,
        course_repo: CourseRepositoryInterface,
        user_repo: UserRepositoryInterface,
        email_service: EmailServiceInterface
    ):
        self._uow = uow
        self._problem_repo = problem_repo
        self._course_repo = course_repo
        self._user_repo = user_repo
        self._email_service = email_service

    async def execute(self, course_id: int, user_id: int):
        async with self._uow as uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, Course._tags, Course._students)
            if not course:
                raise UndefinedCourseError("Course does not exist")
            user = await self._user_repo.get_by_id(user_id)
            manager = CourseStudentsManagerService(course)
            manager.add_students_by_tag(DefautTagType.WAITING_FOR_SUBSCRIBE.value, [user])
        topic, msg = EmailMessageTextTemplate.notify_student_requested_subscribe(course.name)
        await self._email_service.send_mail(user.email, topic, msg)
        if course.notify_request_sub:
            async with self._uow:
                admin = await self._user_repo.get_by_id(course.teacher_id)
                topic, msg = EmailMessageTextTemplate.notify_teacher_requested_subscribe(
                    user.email, course.name)
                await self._email_service.send_mail(admin.email, topic, msg)


class SubscribeOnCourse:
    def __init__(
        self,
        uow: UoWInterface,
        problem_repo: ProblemRepositoryInterface,
        course_repo: CourseRepositoryInterface,
        user_repo: UserRepositoryInterface,
        email_service: EmailServiceInterface
    ):
        self._uow = uow
        self._problem_repo = problem_repo
        self._course_repo = course_repo
        self._user_repo = user_repo
        self._email_service = email_service

    async def execute(self, user_id: int, course_id: int):
        async with self._uow:
            # only authorized users be able to subscribe on course therefore, don't need to check whether user exists or not.
            user = await self._user_repo.get_by_id(user_id)
            course = await self._course_repo.get_by_id_with_rels(course_id, Course._students)
            if not course:
                raise UndefinedCourseError("Course does not exist")
            manager = CourseStudentsManagerService(course)
            manager.add_students([user])
        topic, msg = EmailMessageTextTemplate.notify_student_subscribed(course.name)
        await self._email_service.send_mail(user.email, topic, msg)


class SubscribeOnCourseByLink:
    def __init__(
        self,
        uow: UoWInterface,
        problem_repo: ProblemRepositoryInterface,
        course_repo: CourseRepositoryInterface,
        user_repo: UserRepositoryInterface,
        auth_service: AuthenticationServiceInterface,
        email_service: EmailServiceInterface
    ):
        self._uow = uow
        self._problem_repo = problem_repo
        self._course_repo = course_repo
        self._user_repo = user_repo
        self._token_service = auth_service
        self._email_service = email_service

    async def execute(self, token: str, user_id: int):
        payload = self._token_service.decode(token)
        tag_name = payload.get("tag_name")
        course_id = payload.get("course_id")
        if not course_id:
            raise InvalidInvitingLingError("Inviting URL is invalid", 404)
        async with self._uow:
            course = await self._course_repo.get_by_id_to_add_students_by_tag(course_id)
            if not course:
                raise InvalidInvitingLingError("Inviting URL is invalid", 404)
            if await self._course_repo.check_user_in_course(user_id, course.id):
                raise InvalidInvitingLingError("Already subscribed on course")
            student = await self._user_repo.get_by_id(user_id)
            manager = CourseStudentsManagerService(course)
            if tag_name:
                manager.add_students_by_tag(tag_name, [student])
            else:
                manager.add_students([student])
        topic, msg = EmailMessageTextTemplate.notify_student_subscribed(course.name)
        await self._email_service.send_mail(student.email, topic, msg)
