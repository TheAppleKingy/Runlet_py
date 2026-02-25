from typing import Optional

from pydantic import BaseModel
from .user import UserG1


class TagG1(BaseModel):
    id: int
    name: str
    students: list[UserG1]

    class Config:
        from_attributes = True


class TagG2(BaseModel):
    name: str
    students: list[UserG1]


class TagG3(BaseModel):
    id: int
    name: str


class TagCreateUpdateDTO(BaseModel):
    id: Optional[int] = None
    name: str
