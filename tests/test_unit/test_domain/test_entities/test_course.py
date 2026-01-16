import pytest

from src.domain.entities import Course, User, Problem, Tag, Module
from src.domain.services import CourseTagManagerService, CourseModulesManagerService, CourseProblemManagerService, CourseStudentsManagerService
from src.domain.entities.exceptions import RolesError, UndefinedTagError, RepeatableNamesError, NamesAlreadyExistError, UndefinedModuleError


@pytest.fixture
def user_factory():
    def _make_user(id_, email=None, name=""):
        res = User(
            email=email or f"user{id_}@example.com",
            password="secret",
            name=name or f"user{id_}",
        )
        res.id = id_
        return res
    return _make_user


@pytest.fixture
def base_course(user_factory):
    teacher = user_factory(1)
    course = Course(name="Python 101", _teacher_id=teacher.id, description="course")
    return course


@pytest.fixture
def module_factory():
    def _make_module(name, course_id, mid=None):
        m = Module(name=name, course_id=course_id)
        m.id = mid
        return m
    return _make_module


@pytest.fixture
def problem_factory():
    def _make_problem(name, module_id, pid=None):
        p = Problem(name=name, description="desc", module_id=module_id)
        p.id = pid
        return p
    return _make_problem


@pytest.fixture
def tag_factory():
    def _make_tag(name, course_id, tid=None):
        t = Tag(name=name, course_id=course_id)
        t.id = tid
        return t
    return _make_tag


# ----- CourseStudentsManagerService -----

def test_add_students_basic(base_course, user_factory):
    s1 = user_factory(2)
    s2 = user_factory(3)
    mgr = CourseStudentsManagerService(base_course)

    mgr.add_students([s1, s2])

    assert base_course.students == [s1, s2]


def test_add_students_ignores_duplicates(base_course, user_factory):
    s1 = user_factory(2)
    mgr = CourseStudentsManagerService(base_course)

    mgr.add_students([s1])
    mgr.add_students([s1])

    assert base_course.students == [s1]


def test_add_students_teacher_cannot_be_student(base_course, user_factory):
    teacher_id = base_course.teacher_id
    teacher_like_student = user_factory(teacher_id)
    mgr = CourseStudentsManagerService(base_course)

    with pytest.raises(RolesError):
        mgr.add_students([teacher_like_student])


def test_add_students_by_tag_happy_path(base_course, user_factory, tag_factory):
    s1 = user_factory(2)
    s2 = user_factory(3)
    tag = tag_factory("group A", base_course.id, tid=10)
    base_course._tags.append(tag)
    mgr = CourseStudentsManagerService(base_course)

    mgr.add_students_by_tag(tag_name="group A", students=[s1, s2])

    assert base_course.students == [s1, s2]
    assert tag.students == [s1, s2]


def test_add_students_by_tag_undefined_tag(base_course, user_factory):
    s1 = user_factory(2)
    mgr = CourseStudentsManagerService(base_course)

    with pytest.raises(UndefinedTagError):
        mgr.add_students_by_tag(tag_name="999", students=[s1])


def test_delete_students_removes_from_course_and_tags(
    base_course, user_factory, tag_factory
):
    s1 = user_factory(2)
    s1.id = 2
    s2 = user_factory(3)
    s2.id = 3
    base_course._students = [s1, s2]

    tag = tag_factory("group A", base_course.id, tid=10)
    tag.students = [s1, s2]
    base_course._tags.append(tag)

    mgr = CourseStudentsManagerService(base_course)

    mgr.delete_students([2])  # удалить только s1

    assert base_course.students == [s2]
    assert tag.students == [s2]


# ----- CourseModulesManagerService -----

def test_add_modules_ok(base_course, module_factory):
    m1 = module_factory("Module 1", base_course.id)
    m2 = module_factory("Module 2", base_course.id)
    mgr = CourseModulesManagerService(base_course)

    mgr.add_modules([m1, m2])

    assert base_course.modules == [m1, m2]


def test_add_modules_duplicate_names_in_batch(base_course, module_factory):
    m1 = module_factory("Module 1", base_course.id)
    m2 = module_factory("Module 1", base_course.id)
    mgr = CourseModulesManagerService(base_course)

    with pytest.raises(RepeatableNamesError):
        mgr.add_modules([m1, m2])


def test_add_modules_names_already_exist_in_course(base_course, module_factory):
    existing = module_factory("Module 1", base_course.id)
    base_course._modules.append(existing)
    new = module_factory("Module 1", base_course.id)
    mgr = CourseModulesManagerService(base_course)

    with pytest.raises(NamesAlreadyExistError):
        mgr.add_modules([new])


def test_delete_modules_by_ids(base_course, module_factory):
    m1 = module_factory("Module 1", base_course.id, mid=1)
    m2 = module_factory("Module 2", base_course.id, mid=2)
    base_course._modules = [m1, m2]
    mgr = CourseModulesManagerService(base_course)

    mgr.delete_modules([1])

    assert base_course.modules == [m2]


# ----- CourseTagManagerService -----

def test_add_tags_ok(base_course, tag_factory):
    t1 = tag_factory("A", base_course.id)
    t2 = tag_factory("B", base_course.id)
    mgr = CourseTagManagerService(base_course)

    mgr.add_tags([t1, t2])

    assert base_course.tags == [t1, t2]


def test_add_tags_duplicate_names_in_batch(base_course, tag_factory):
    t1 = tag_factory("A", base_course.id)
    t2 = tag_factory("A", base_course.id)
    mgr = CourseTagManagerService(base_course)

    with pytest.raises(RepeatableNamesError):
        mgr.add_tags([t1, t2])


def test_add_tags_names_already_exist_in_course(base_course, tag_factory):
    t_existing = tag_factory("A", base_course.id)
    base_course._tags.append(t_existing)
    t_new = tag_factory("A", base_course.id)
    mgr = CourseTagManagerService(base_course)

    with pytest.raises(NamesAlreadyExistError):
        mgr.add_tags([t_new])


def test_delete_tags_by_ids(base_course, tag_factory):
    t1 = tag_factory("A", base_course.id)
    t1.id = 1
    t2 = tag_factory("B", base_course.id)
    t2.id = 2
    base_course._tags = [t1, t2]
    mgr = CourseTagManagerService(base_course)

    mgr.delete_tags([1])

    assert base_course.tags == [t2]


# ----- CourseProblemManagerService + Module -----

def test_module_add_and_delete_problems(module_factory, problem_factory, base_course):
    module = module_factory("M1", base_course.id, mid=1)
    base_course._modules.append(module)
    p1 = problem_factory("P1", module_id=1, pid=1)
    p2 = problem_factory("P2", module_id=1, pid=2)

    module.add_problems([p1, p2])
    assert module.problems == [p1, p2]

    module.delete_problems([1])
    assert module.problems == [p2]


def test_course_problem_manager_add_ok(
    base_course, module_factory, problem_factory
):
    module = module_factory("M1", base_course.id, mid=1)
    base_course._modules.append(module)
    p1 = problem_factory("P1", module_id=1)
    p2 = problem_factory("P2", module_id=1)

    mgr = CourseProblemManagerService(base_course)
    mgr.add_problems("M1", [p1, p2])

    assert module.problems == [p1, p2]


def test_course_problem_manager_undefined_module_on_add(
    base_course, problem_factory
):
    p1 = problem_factory("P1", module_id=999)
    mgr = CourseProblemManagerService(base_course)

    with pytest.raises(UndefinedModuleError):
        mgr.add_problems("NO_SUCH", [p1])


def test_course_problem_manager_repeatable_problem_names(
    base_course, module_factory, problem_factory
):
    module = module_factory("M1", base_course.id, mid=1)
    base_course._modules.append(module)
    p1 = problem_factory("P1", module_id=1)
    p2 = problem_factory("P1", module_id=1)
    mgr = CourseProblemManagerService(base_course)

    with pytest.raises(RepeatableNamesError):
        mgr.add_problems("M1", [p1, p2])


def test_course_problem_manager_names_already_exist_in_module(
    base_course, module_factory, problem_factory
):
    module = module_factory("M1", base_course.id, mid=1)
    base_course._modules.append(module)
    existing = problem_factory("P1", module_id=1)
    module.add_problems([existing])

    new = problem_factory("P1", module_id=1)
    mgr = CourseProblemManagerService(base_course)

    with pytest.raises(NamesAlreadyExistError):
        mgr.add_problems("M1", [new])


def test_course_problem_manager_delete_ok(
    base_course, module_factory, problem_factory
):
    module = module_factory("M1", base_course.id, mid=1)
    base_course._modules.append(module)
    p1 = problem_factory("P1", module_id=1, pid=1)
    p2 = problem_factory("P2", module_id=1, pid=2)
    module.add_problems([p1, p2])

    mgr = CourseProblemManagerService(base_course)
    mgr.delete_problems("M1", [1])

    assert module.problems == [p2]


def test_course_problem_manager_undefined_module_on_delete(base_course):
    mgr = CourseProblemManagerService(base_course)

    with pytest.raises(UndefinedModuleError):
        mgr.delete_problems("NO_SUCH", [1])
