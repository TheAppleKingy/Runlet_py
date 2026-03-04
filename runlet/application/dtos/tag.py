from typing import Optional

from pydantic import BaseModel, Field
from .user import (
    UserG1,
    UserWithSeenDTO
)


class TagG1(BaseModel):
    id: int
    name: str
    students: list[UserG1] = Field(default_factory=list)

    class Config:
        from_attributes = True


class TagG2(BaseModel):
    id: Optional[int] = None
    name: str
    students: list[UserWithSeenDTO] = Field(default_factory=list)


class TagG3(BaseModel):
    id: int
    name: str


class TagCreateUpdateDTO(BaseModel):
    id: Optional[int] = None
    name: str
