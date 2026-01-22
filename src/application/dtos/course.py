from pydantic import BaseModel, Field

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


class CourseC1(BaseModel):
    name: str = Field(max_length=100)
    description: str = Field(max_length=512, default="")
    is_private: bool = False
    notify_request_sub: bool = False
