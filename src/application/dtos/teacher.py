from typing import Optional

from pydantic import BaseModel, Field


class TestCaseDTO(BaseModel):
    input: str
    output: str


class ProblemForTeacherDTO(BaseModel):
    id: int
    name: str
    description: str
    test_cases: dict[int, TestCaseDTO]


class StudentForTeacherDTO(BaseModel):
    id: int
    name: str


class ModuleForTeacherDTO(BaseModel):
    id: int
    name: str
    problems: list[ProblemForTeacherDTO]


class TagForTeacherDTO(BaseModel):
    id: int
    name: str
    course_id: int
    students: list[StudentForTeacherDTO]


class CourseToUpdateDTO(BaseModel):
    id: int
    name: str
    modules: list[ModuleForTeacherDTO] = []


class UpdateCourseDTO(BaseModel):
    name: Optional[str] = Field(max_length=100)
    description: Optional[str] = Field(max_length=512)
    is_private: Optional[bool] = None
    notify_request_sub: Optional[bool] = None


class CreateProblemDTO(BaseModel):
    name: str = Field(max_length=100)
    description: str = Field(max_length=1024)
    auto_pass: bool = False
    test_cases: dict[int, TestCaseDTO] = {}
    show_test_cases: bool = False


class CreateModuleDTO(BaseModel):
    name: str = Field(max_length=100)
    problems: list[CreateProblemDTO] = []


class CreateCourseTagDTO(BaseModel):
    name: str = Field(max_length=100)
    students_ids: list[int] = []


class CreateCourseTagsDTO(BaseModel):
    tags_data: list[CreateCourseTagDTO]


class CourseForTeacherDTO(BaseModel):
    id: int
    name: str
    modules: list[ModuleForTeacherDTO]
    tags: list[TagForTeacherDTO]
    is_private: bool
    notify_request_sub: bool


class TeacherCourseToManageDTO(BaseModel):
    id: int
    name: str
    modules: list[ModuleForTeacherDTO]
    tags: list[TagForTeacherDTO]


class DeleteStudentsFromCourseDTO(BaseModel):
    name: str
    students_ids: list[int] = []


class GenerateInviteLinkDTO(BaseModel):
    tag_name: Optional[str] = None


class GenInviteLinkDTO(BaseModel):
    link: str
