from typing import Optional

from pydantic import BaseModel, Field
from .module import ModuleCreateUpdateDTO
from .tag import TagCreateUpdateDTO


class GenLinkDTO(BaseModel):
    tags_ids: list[int] = []


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
    problems_ids: list[int] = []
    module_id: int


class DeleteModulesDTO(BaseModel):
    modules_ids: list[int]


class ManageModulesDTO(BaseModel):
    to_delete: list[int] = Field(default_factory=list)
    to_create_update: list[ModuleCreateUpdateDTO] = Field(default_factory=list)


class ManageTagsDTO(BaseModel):
    to_delete: list[int] = Field(default_factory=list)
    to_create_update: list[TagCreateUpdateDTO] = Field(default_factory=list)
