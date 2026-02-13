from typing import Optional

from pydantic import BaseModel, Field


class GenLinkDTO(BaseModel):
    tags_names: list[str] = []


class LinkDTO(BaseModel):
    link: str


class TagsCreateUpdate(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class DeleteTagsDTO(BaseModel):
    tags_ids: list[int]


class AddStudentsDTO(BaseModel):
    tag_name: Optional[str] = None
    student_ids: list[int]


class DeleteStudentsDTO(BaseModel):
    students_ids: list[int]


class DeleteProblemsDTO(BaseModel):
    problems_ids: list[int] = []
    module_name: str


class DeleteModulesDTO(BaseModel):
    modules_ids: list[int]
