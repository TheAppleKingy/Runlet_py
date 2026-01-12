from dataclasses import dataclass, field

from .user import User
from .problem import Module
from .tag import Tag
from .exceptions import RolesError, HasNoDirectAccessError


@dataclass
class Course:
    name: str
    _teacher_id: int
    _tags: list[Tag] = field(default_factory=list, init=False)
    id: int = field(default=None, init=False)  # type: ignore
    description: str = ""
    _students: list[User] = field(default_factory=list, init=False)
    _modules: list[Module] = field(default_factory=list, init=False)
    is_private: bool = False

    @property
    def teacher_id(self):
        return self._teacher_id

    @teacher_id.setter
    def teacher_id(self, id_: int):
        if any(s.id == id_ for s in self._students):
            raise RolesError("Teacher cannot be student at the same time")
        self._teacher_id = id_

    @property
    def students(self):
        return self._students

    @students.setter
    def students(self, _):
        raise HasNoDirectAccessError(
            "Unable to set list of students for course directly")

    @property
    def modules(self):
        return self._modules

    @modules.setter
    def modules(self, _):
        raise HasNoDirectAccessError("Unable to set list of modules for course directly")

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, _):
        raise HasNoDirectAccessError("Unable to set list of tags for course directly")

    def get_modules_names(self):
        return [module.name for module in self.modules]

    def get_tags_names(self):
        return [tag.name for tag in self.tags]

    def get_module(self, module_name: str):
        for module in self.modules:
            if module.name == module_name:
                return module
        return None
