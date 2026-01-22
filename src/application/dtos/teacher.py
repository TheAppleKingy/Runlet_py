from typing import Optional

from pydantic import BaseModel, Field
from .tag import TagC1
from .problem import ProblemC1


class GenLinkDTO(BaseModel):
    tags_names: list[str] = []


class LinkDTO(BaseModel):
    link: str


class AddTagsDTO(BaseModel):
    tags_data: list[TagC1]


class DeleteTagsDTO(BaseModel):
    tags_ids: list[int]


class AddStudentsDTO(BaseModel):
    tag_name: Optional[str] = None
    student_ids: list[int]


class DeleteStudentsDTO(BaseModel):
    students_ids: list[int]


class AddProblemDTO(BaseModel):
    module_name: str
    problem_data: ProblemC1


class DeleteProblemsDTO(BaseModel):
    problems_ids: list[int] = []
    module_name: str


class DeleteModulesDTO(BaseModel):
    modules_ids: list[int]
