from dataclasses import dataclass, field

from .user import User
from .problem import Problem
from ..exceptions.entities import RolesError


@dataclass
class Course:
    id: int = field(default=None)
    name: str = field(default="")
    description: str = field(default="")
    _teacher_id: int = field(default=None)
    _students: list[User] = field(default_factory=list, init=False)
    problems: list[Problem] = field(default_factory=list, init=False)

    @property
    def teacher_id(self):
        return self._teacher_id

    @teacher_id.setter
    def teacher_id(self, id_: int):
        if id_ in {s.id for s in self._students}:
            raise RolesError("Teacher cannot be student at the same time")
        self._teacher_id = id_

    @property
    def students(self):
        return tuple(self._students)

    def _validate_teacher_is_student(self, students: list[User]):
        if self._teacher_id in {s.id for s in students}:
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

    def delete_students(self, students: list[User]):
        self._students = [s for s in self._students if s not in students]
