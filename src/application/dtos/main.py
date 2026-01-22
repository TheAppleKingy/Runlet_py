from pydantic import BaseModel

from .course import CourseG1, CourseG5


class MainDTO(BaseModel):
    as_teacher: list[CourseG1]
    as_student: list[CourseG1]
    paginated: CourseG5
