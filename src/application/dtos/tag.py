from pydantic import BaseModel, Field
from .user import UserG3, UserG1


class TagG1(BaseModel):
    id: int
    name: str
    students: list[UserG1]


class TagG2(BaseModel):
    name: str
    students: list[UserG1]


class TagC1(BaseModel):
    name: str = Field(max_length=100)
    students_ids: list[int] = []
