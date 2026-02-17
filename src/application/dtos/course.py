from typing import Optional

from pydantic import BaseModel, Field, field_serializer

from src.domain.entities import DefaultTagType
from .module import ModuleG1, ModuleG2
from .tag import TagG2
from .user import UserG1


class CourseG1(BaseModel):
    id: int
    name: str


class CourseG2(BaseModel):
    id: int
    name: str
    description: str


class CourseG3(BaseModel):
    id: int
    name: str
    modules: list[ModuleG1]


class CourseG4(BaseModel):
    id: int
    name: str
    students: list[UserG1]
    tags: list[TagG2]

    @field_serializer("tags")
    def serialize_tags(self, tags: list[TagG2]):
        return [tag_data for tag_data in tags if tag_data.name not in DefaultTagType.names()]


class CourseG5(BaseModel):
    courses: list[CourseG1]
    page: int
    size: int
    total: int


class CourseG6(BaseModel):
    id: int
    name: str
    modules: list[ModuleG2]


class CourseG7(BaseModel):
    id: int
    name: str
    description: str
    modules: list[ModuleG1]


class CourseG8(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_private: bool
    notify_request_sub: bool


class CourseCreateDTO(BaseModel):
    name: str = Field(max_length=100)
    description: Optional[str] = Field(max_length=512, default=None)
    is_private: bool = False
    notify_request_sub: bool = False


class CourseUpdateDTO(BaseModel):
    name: Optional[str] = Field(max_length=100, default=None)
    description: Optional[str] = Field(max_length=512, default=None)
    is_private: Optional[bool] = None
    notify_request_sub: Optional[bool] = None
