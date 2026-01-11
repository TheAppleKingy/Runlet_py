from src.application.interfaces.repositories import CourseRepositoryInterface, ProblemRepositoryInterface, UserRepositoryInterface
from src.application.interfaces.uow import ReadOnlyUoWInterface, ReadWriteUoWInterface
from src.application.interfaces.services import AuthenticationServiceInterface
from src.domain.entities import Tag, User, Course
from .exceptions import SubscribeUnexsistantCourseError, InvalidInvitingLingError

__all__ = [
    "ShowStudentCourses",
    "ShowStudentCourseProblems",
    "SubscribeOnCourse",
]


class ShowStudentCourses:
    def __init__(
        self,
        uow: ReadOnlyUoWInterface,
        course_repo: CourseRepositoryInterface
    ):
        self._uow = uow
        self._course_repo = course_repo

    async def execute(self, user_id: int):
        async with self._uow:
            courses = await self._course_repo.get_user_courses(user_id)
        return courses


class ShowStudentCourseProblems:
    def __init__(
        self,
        uow: ReadOnlyUoWInterface,
        problem_repo: ProblemRepositoryInterface
    ):
        self._uow = uow
        self._problem_repo = problem_repo

    async def execute(self, course_id: int):
        async with self._uow:
            problems = await self._problem_repo.get_course_problems(course_id)
        return problems


class SubscribeOnCourse:
    def __init__(
        self,
        uow: ReadWriteUoWInterface,
        problem_repo: ProblemRepositoryInterface,
        course_repo: CourseRepositoryInterface,
        user_repo: UserRepositoryInterface
    ):
        self._uow = uow
        self._problem_repo = problem_repo
        self._course_repo = course_repo
        self._user_repo = user_repo

    async def execute(self, user_id: int, course_id: int):
        async with self._uow:
            # only authorized users be able to subscribe on course therefore, don't need to check whether user exists or not.
            user = await self._user_repo.get_by_id(user_id)
            course = await self._course_repo.get_by_id_with_rels(course_id, Course._students)
            if not course:
                raise SubscribeUnexsistantCourseError(
                    "Course you trying to subscribe does not exist")
            course.add_students([user])


class SubscribeOnCourseByLink:
    def __init__(
        self,
        uow: ReadWriteUoWInterface,
        problem_repo: ProblemRepositoryInterface,
        course_repo: CourseRepositoryInterface,
        user_repo: UserRepositoryInterface,
        auth_service: AuthenticationServiceInterface
    ):
        self._uow = uow
        self._problem_repo = problem_repo
        self._course_repo = course_repo
        self._user_repo = user_repo
        self._token_service = auth_service

    async def execute(self, token: str, user_id: int):
        payload = self._token_service.decode(token)
        tag_id = payload.get("tag_id")
        course_id = payload.get("course_id")
        if not course_id:
            raise InvalidInvitingLingError("Inviting URL is invalid")
        async with self._uow:
            course = await self._course_repo.get_by_id_with_rels(course_id, Tag, User)
            if not course:
                raise InvalidInvitingLingError("Inviting URL is invalid")
            student = await self._user_repo.get_by_id(user_id)
            if tag_id:
                course.add_students_by_tag(tag_id, [student])
            else:
                course.add_students([student])
