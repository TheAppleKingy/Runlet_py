from typing import Optional

from pydantic import BaseModel
from .course import CourseForUnauthorizedDTO, PaginatedCoursesDTO


class MyProfileDTO(BaseModel):
    id: int
    name: str


class MainDTO(BaseModel):
    as_teacher: list[CourseForUnauthorizedDTO]
    as_student: list[CourseForUnauthorizedDTO]
    paginated: PaginatedCoursesDTO
