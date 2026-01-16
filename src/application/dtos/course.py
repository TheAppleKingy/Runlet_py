from pydantic import BaseModel, Field


class CourseForUnauthorizedDTO(BaseModel):
    id: int
    name: str
    description: str


class PaginatedCoursesDTO(BaseModel):
    courses: list[CourseForUnauthorizedDTO]
    page: int
    size: int
    total: int


class CreateCourseDTO(BaseModel):
    name: str = Field(max_length=100)
    description: str = Field(max_length=512, default="")
    is_private: bool = False
    notify_request_sub: bool = False
