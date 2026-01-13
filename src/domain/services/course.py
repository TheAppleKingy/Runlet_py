from typing import TypeVar

from src.domain.entities import Course, User, Problem, Module, Tag
from src.domain.entities.exceptions import (
    RolesError,
    UndefinedModuleError,
    UndefinedTagError,
    RepeatableNamesError,
    NamesAlreadyExistError
)
from src.logger import logger


class HasNameType:
    name: str


T = TypeVar("HasNameType", bound=HasNameType)


class BaseCourseManagerService:
    def __init__(self, course: Course):
        self._course = course


class BaseCourseNamedAttrsManagerService(BaseCourseManagerService):
    def _validate_repeatable_names(self, entities: list[T]):
        if len(set(ent.name for ent in entities)) != len(entities):
            raise RepeatableNamesError(f"Names cannot match")

    def _validate_already_exists(self, current: list[T], incoming: list[T]):
        intersec = set(ent.name for ent in current) & set(ent.name for ent in incoming)
        if intersec:
            raise NamesAlreadyExistError(
                f"Names of {intersec} already exists in course {self._course.name}")


class CourseStudentsManagerService(BaseCourseManagerService):
    def _validate_teacher_is_student(self, students: list[User]):
        if self._course._teacher_id in [s.id for s in students]:
            raise RolesError(f"User {self._course._teacher_id} is the teacher of this course")

    def add_students(self, students: list[User]):
        self._validate_teacher_is_student(students)
        for s in students:
            if s not in self._course._students:
                self._course._students.append(s)

    def _find_tag_to_add_students(self, target_name: str):
        for tag in self._course.tags:
            if tag.name == target_name:
                return tag
        return None

    def add_students_by_tag(self, tag_name: str, students: list[User]):
        target_tag = self._find_tag_to_add_students(tag_name)
        if not target_tag:
            raise UndefinedTagError(
                f"Unable to bind students to tag {tag_name}: tag not related with course {self._course.name}")
        self.add_students(students)
        for s in students:
            if s not in target_tag.students:
                target_tag.students.append(s)

    def _delete_students_common(self, ids: list[int]) -> list[int]:
        to_delete = [s.id for s in self._course._students if s.id in ids]
        self._course._students = [s for s in self._course._students if s.id not in to_delete]
        return to_delete

    def delete_students(self, ids: list[int]):
        deleted = self._delete_students_common(ids)
        for tag in self._course.tags:
            tag.students = [s for s in tag.students if s.id not in deleted]


class CourseModulesManagerService(BaseCourseNamedAttrsManagerService):
    def _validate_incoming_modules(self, modules: list[Module]):
        self._validate_repeatable_names(modules)
        self._validate_already_exists(self._course.modules, modules)

    def add_modules(self, modules: list[Module]):
        self._validate_incoming_modules(modules)
        self._course._modules += modules

    def delete_modules(self, ids: list[int]):
        self._course._modules = [module for module in self._course.modules if module.id not in ids]


class CourseTagManagerService(BaseCourseNamedAttrsManagerService):
    def _validate_incoming_tags(self, tags: list[Tag]):
        self._validate_repeatable_names(tags)
        self._validate_already_exists(self._course.tags, tags)

    def add_tags(self, tags: list[Tag]):
        self._validate_incoming_tags(tags)
        self._course._tags += tags

    def delete_tags(self, ids: int):
        self._course._tags = [tag for tag in self._course.tags if tag.id not in ids]


class CourseProblemManagerService(BaseCourseNamedAttrsManagerService):
    def _validate_incoming_problems(self, module: Module, problems: list[Problem]):
        self._validate_repeatable_names(problems)
        self._validate_already_exists(module.problems, problems)

    def add_problems(self, module_name: str, problems: list[Problem]):
        module = self._course.get_module(module_name)
        if not module:
            raise UndefinedModuleError(
                f"Module with name {module_name} does not exist in course {self._course.name}")
        self._validate_incoming_problems(module, problems)
        module.add_problems(problems)

    def delete_problems(self, module_name: str, problems_ids: list[int]):
        module = self._course.get_module(module_name)
        if not module:
            raise UndefinedModuleError(
                f"Module with name {module_name} does not exist in course {self._course.name}")
        module.delete_problems(problems_ids)
