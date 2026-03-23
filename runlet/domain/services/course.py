from runlet.domain.entities import (
    Course,
    User,
    Problem,
    Module,
    Tag,
    DefaultTagType
)
from runlet.domain.entities.exceptions import (
    RolesError,
    UndefinedModuleError,
    UndefinedTagError,
    RepeatableNamesError,
    NamesAlreadyExistError,
    ImpossibleOperationError,
    IncorrectModulesOrdersError
)
from runlet.domain.interfaces.types import Named


class BaseCourseManagerService:
    def __init__(self, course: Course):
        self._course = course


class BaseCourseNamedAttrsManagerService(BaseCourseManagerService):
    def _validate_repeatable_names(self, entities: list[Named]):
        if len(set(ent.name for ent in entities)) != len(entities):
            raise RepeatableNamesError(f"Names of {entities[0].__class__.__name__.lower()} cannot match")

    def _validate_already_exists(self, current: list[Named], incoming: list[Named]):
        intersec = set(ent.name for ent in current) & set(ent.name for ent in incoming)
        if intersec:
            raise NamesAlreadyExistError(
                f"Names of {incoming[0].__class__.__name__.lower()} already exists in course {self._course.name}")


class CourseStudentsManagerService(BaseCourseManagerService):
    def _validate_teacher_is_student(self, students: list[User]):
        if self._course._teacher_id in [s.id for s in students]:
            raise RolesError("User is the teacher of this course")

    def add_students(self, students: list[User]) -> list[int]:
        self._validate_teacher_is_student(students)
        waiting_tag = self._course.get_tag(DefaultTagType.WAITING_FOR_SUBSCRIBE.value)
        from_waiting = []
        for s in students:
            if s not in self._course._students:
                self._course._students.append(s)
            if s in waiting_tag.students:
                waiting_tag.students.remove(s)
            from_waiting.append(s.id)
        return from_waiting

    def add_students_to_tag(self, tag_id: int, students: list[User]):
        target_tag = self._course.get_tag_by_id(tag_id)
        if not target_tag:
            raise UndefinedTagError("Unable to add students to tag: tag not related with course")
        if target_tag.name in DefaultTagType.names():
            raise ImpossibleOperationError(f"Unable to add student to default tag '{target_tag.name}'")
        self.add_students(students)
        for s in students:
            if s not in target_tag.students:
                target_tag.students.append(s)

    def request_subscribe(self, students: list[User]):
        target = self._course.get_tag(DefaultTagType.WAITING_FOR_SUBSCRIBE.value)
        self._validate_teacher_is_student(students)
        for s in students:
            if s in self._course.students:
                raise ImpossibleOperationError("Unable to request subscribe on course: already subscribed")
            if s not in target.students:
                target.students.append(s)

    def _delete_students_common(self, ids: list[int]) -> list[int]:
        to_delete = [s.id for s in self._course._students if s.id in ids]
        self._course._students = [s for s in self._course._students if s.id not in to_delete]
        return to_delete

    def delete_students(self, ids: list[int]) -> list[int]:
        deleted = self._delete_students_common(ids)
        for tag in self._course.tags:
            tag.students = [s for s in tag.students if s.id not in deleted]
        return deleted

    def delete_students_from_tag(self, tag_id: int, students_ids: list[int]):
        tag = self._course.get_tag_by_id(tag_id)
        if not tag:
            raise UndefinedTagError("Tag does not exist")
        tag.students = [s for s in tag.students if s.id not in students_ids]


class CourseModulesManagerService(BaseCourseNamedAttrsManagerService):
    def _validate_orders(self, current: list[Module], incoming: list[Module]):
        orders = sorted([module.order for module in current + incoming])
        print(orders, [module.order for module in current], [module.order for module in incoming])
        for i in range(1, len(orders) + 1):
            if i != orders[i-1]:
                raise IncorrectModulesOrdersError("Retrieved modules have incorrect orders")

    def _validate_incoming_modules(self, current: list[Module], incoming: list[Module]):
        self._validate_repeatable_names(incoming)
        self._validate_already_exists(current, incoming)
        self._validate_orders(current, incoming)

    def add_modules(self, modules: list[Module]):
        self._validate_incoming_modules(self._course.modules, modules)
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

    def delete_tags(self, ids: list[int]):
        for type_ in DefaultTagType:
            default_tag = self._course.get_tag(type_.value)
            if default_tag.id in ids:
                raise ImpossibleOperationError(f"Unable to delete default tag '{type_.value}'")
        self._course._tags = [tag for tag in self._course.tags if tag.id not in ids]


class CourseProblemManagerService(BaseCourseNamedAttrsManagerService):
    def _validate_incoming_problems(self, module: Module, problems: list[Problem]):
        self._validate_repeatable_names(problems)
        self._validate_already_exists(module.problems, problems)

    def add_problems(self, module: Module, problems: list[Problem]):
        self._validate_incoming_problems(module, problems)
        module.add_problems(problems)

    def delete_problems(self, module_id: int, problems_ids: list[int]):
        module = self._course.get_module_by_id(module_id)
        if not module:
            raise UndefinedModuleError("Module does not exist")
        module.delete_problems(problems_ids)
