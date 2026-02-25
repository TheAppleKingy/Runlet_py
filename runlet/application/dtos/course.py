from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .module import (
    ModuleG1,
    ModuleG2,
    ModuleG3,
    OrderedModuleDTO
)
from .tag import (
    TagG2
)
from .user import (
    UserWithSeenDTO
)


class CourseG1(BaseModel):
    id: int
    name: str


class CourseG2(BaseModel):
    id: int
    name: str
    description: str


class _ContainsOrderedModulesDTO(BaseModel):
    modules: list[OrderedModuleDTO] = Field(default_factory=list)

    @field_validator("modules", mode="after")
    @classmethod
    def validate_modules(cls, modules: list[OrderedModuleDTO]):
        return sorted(modules, key=lambda m: m.order)


class CourseG3(_ContainsOrderedModulesDTO):
    id: int
    name: str
    modules: list[ModuleG3] = Field(default_factory=list)  # type: ignore[assignment]


class CourseG4(BaseModel):
    id: int
    name: str
    tags: list[TagG2] = Field(default_factory=list)
    students: list[UserWithSeenDTO] = Field(default_factory=list)


class CourseG5(BaseModel):
    courses: list[CourseG1]
    page: int
    size: int
    total: int


class CourseG6(_ContainsOrderedModulesDTO):
    id: int
    name: str
    modules: list[ModuleG2]  # type: ignore[assignment]


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
