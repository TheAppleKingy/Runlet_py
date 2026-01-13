from src.application.interfaces.repositories import CourseRepositoryInterface
from src.application.interfaces.uow import UoWInterface
__all__ = [
    "ShowStudentCourses",
    "ShowStudentCourse",
]


class ShowStudentCourses:
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface
    ):
        self._uow = uow
        self._course_repo = course_repo

    async def execute(self, user_id: int):
        async with self._uow:
            courses = await self._course_repo.get_user_courses(user_id)
        return courses


class ShowStudentCourse:
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface
    ):
        self._uow = uow
        self._course_repo = course_repo

    async def execute(self, course_id: int):
        async with self._uow:
            course = await self._course_repo.get_by_id_for_students(course_id)
        return course
