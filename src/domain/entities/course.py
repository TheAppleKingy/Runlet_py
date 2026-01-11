from dataclasses import dataclass, field

from .user import User
from .problem import Problem
from .tag import Tag
from .exceptions import RolesError, UndefinedTagError


@dataclass
class Course:
    name: str
    _teacher_id: int
    tags: list[Tag] = field(default_factory=list, init=False)
    id: int = field(default=None, init=False)  # type: ignore
    description: str = ""
    _students: list[User] = field(default_factory=list, init=False)
    problems: list[Problem] = field(default_factory=list, init=False)
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
        return tuple(self._students)

    def _validate_teacher_is_student(self, students: list[User]):
        if self._teacher_id in [s.id for s in students]:
            raise RolesError(f"User {self._teacher_id} is the teacher of this course")

    @students.setter
    def students(self, students: list[User]):
        self._validate_teacher_is_student(students)
        self._students = students

    def add_students(self, students: list[User]):
        self._validate_teacher_is_student(students)
        for s in students:
            if s not in self._students:
                self._students.append(s)

    def add_students_by_tag(self, tag_id: int, students: list[User]):  # to test
        self.add_students(students)
        target_tag = None
        for tag in self.tags:
            if tag.id == tag_id:
                target_tag = tag
                break
        if not target_tag:
            raise UndefinedTagError(
                f"Unable to bind students to tag {tag_id}: tag not related with course {self.name}")
        for s in students:
            if s not in target_tag.students:
                target_tag.students.append(s)

    def _delete_students_common(self, ids: list[int]) -> list[int]:
        to_delete = [s.id for s in self._students if s.id in ids]
        self._students = [s for s in self._students if s.id not in to_delete]
        return to_delete

    def delete_students(self, ids: list[int]):
        deleted = self.delete_students(ids)
        for tag in self.tags:
            tag.students = [s for s in tag.students if s.id not in deleted]
