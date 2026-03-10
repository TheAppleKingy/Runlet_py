from pydantic import BaseModel, Field

from .course import CourseG1


class PaginatedCoursesDTO(BaseModel):
    courses: list[CourseG1] = Field(default_factory=list)
    page: int
    pages: int


class MainDTO(BaseModel):
    as_teacher: PaginatedCoursesDTO
    as_student: PaginatedCoursesDTO
    all_courses: PaginatedCoursesDTO
