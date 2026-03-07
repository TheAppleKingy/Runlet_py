from typing import Optional

from pydantic import BaseModel, Field
from .module import ModuleCreateUpdateDTO
from .user import (
    UserG1,
    UserWithSeenDTO,
    UserG4
)
from .tag import (
    TagCreateUpdateDTO,
    TagG1,
    TagG2,
    TagG3
)


class GenLinkDTO(BaseModel):
    tags_ids: list[int] = Field(default_factory=list)


class LinkDTO(BaseModel):
    link: str


class DeleteTagsDTO(BaseModel):
    tags_ids: list[int]


class UpdateTagStudentsDTO(BaseModel):
    tag_id: Optional[int] = None
    to_add: list[int] = Field(default_factory=list)
    to_delete: list[int] = Field(default_factory=list)


class DeleteStudentsDTO(BaseModel):
    students_ids: list[int]


class DeleteProblemsDTO(BaseModel):
    problems_ids: list[int]
    module_id: int


class DeleteModulesDTO(BaseModel):
    modules_ids: list[int]


class ManageModulesDTO(BaseModel):
    to_delete: list[int] = Field(default_factory=list)
    to_create_update: list[ModuleCreateUpdateDTO] = Field(default_factory=list)


class ManageTagsDTO(BaseModel):
    to_delete: list[int] = Field(default_factory=list)
    to_create_update: list[TagCreateUpdateDTO] = Field(default_factory=list)


class RateStudentDTO(BaseModel):
    ok: bool


class TagsToUpdateDTO(BaseModel):
    students: list[UserG1] = Field(default_factory=list)
    tags: list[TagG1] = Field(default_factory=list)


class PaginatedCourseTagsStudentsWithSeensDTO(BaseModel):
    course_id: int
    course_name: str
    tags: list[TagG2] = Field(default_factory=list)
    page: int
    pages: int


class PaginatedProblemStudentsInfoDTO(BaseModel):
    students: list[UserG4] = Field(default_factory=list)
    page: int
    pages: int


class PaginatedTagStudentsDTO(BaseModel):
    id: Optional[int] = None
    name: str
    students: list[UserG1] = Field(default_factory=list)
    page: int
    pages: int


class PaginatedTagsStudentsDTO(BaseModel):
    tags_students: list[PaginatedTagStudentsDTO] = Field(default_factory=list)
    tags: list[TagG3] = Field(default_factory=list)


class PaginatedSearchStudentsWithSeensDTO(BaseModel):
    students: list[UserWithSeenDTO] = Field(default_factory=list)
    page: int
    pages: int


class PaginatedSearchStudentsDTO(BaseModel):
    students: list[UserG1] = Field(default_factory=list)
    page: int
    pages: int
