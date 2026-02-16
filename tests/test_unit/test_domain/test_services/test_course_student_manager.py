import pytest

from src.domain.entities import Course, User, Tag, DefautTagType
from src.domain.services.course import CourseStudentsManagerService
from src.domain.entities.exceptions import RolesError, ImpossibleOperationError, UndefinedTagError


@pytest.fixture
def course():
    return Course(name="Test Course", _teacher_id=42)


@pytest.fixture
def user():
    return User(email="user@example.com", password="pass")


@pytest.fixture
def waiting_tag():
    tag = Tag(name=DefautTagType.WAITING_FOR_SUBSCRIBE.value, course_id=1)
    tag.id = 1
    return tag


@pytest.fixture
def custom_tag():
    tag = Tag(name="custom", course_id=1)
    tag.id = 2
    return tag


@pytest.fixture
def manager(course):
    return CourseStudentsManagerService(course)


@pytest.fixture
def manager_with_tags(course, waiting_tag, custom_tag):
    course._tags = [waiting_tag, custom_tag]
    course._students = []
    return CourseStudentsManagerService(course)


class TestAddStudents:
    def test_adds_student(self, manager_with_tags, user):
        manager_with_tags.add_students([user])
        assert user in manager_with_tags._course._students

    def test_skips_duplicate_student(self, manager_with_tags, user):
        manager_with_tags._course._students.append(user)
        manager_with_tags.add_students([user])
        assert len(manager_with_tags._course._students) == 1

    def test_removes_from_waiting_tag(self, manager, user, waiting_tag):
        manager._course._tags = [waiting_tag]
        waiting_tag.students.append(user)
        manager._course.get_tag = lambda name: waiting_tag if name == DefautTagType.WAITING_FOR_SUBSCRIBE.value else None

        manager.add_students([user])
        assert user not in waiting_tag.students
        assert user in manager._course._students

    def test_raises_if_teacher_in_students(self, manager, user):
        user.id = 42
        with pytest.raises(RolesError):
            manager.add_students([user])


class TestAddStudentsByTag:
    def test_raises_tag_not_found(self, manager, user):
        with pytest.raises(UndefinedTagError):
            manager.add_students_by_tag(999, [user])

    def test_raises_default_tag(self, manager_with_tags, user):
        with pytest.raises(ImpossibleOperationError, match="Unable to add student to default tag"):
            manager_with_tags.add_students_by_tag(1, [user])

    def test_adds_to_course_and_tag(self, manager_with_tags, user):
        manager_with_tags.add_students_by_tag(2, [user])
        assert user in manager_with_tags._course._students
        assert user in manager_with_tags._course._tags[1].students  # custom_tag

    def test_skips_duplicates(self, manager_with_tags, user):
        manager_with_tags._course._students.append(user)
        manager_with_tags._course._tags[1].students.append(user)  # custom_tag

        manager_with_tags.add_students_by_tag(2, [user])

        assert len(manager_with_tags._course._students) == 1
        assert len(manager_with_tags._course._tags[1].students) == 1


class TestRequestSubscribe:
    def test_adds_to_waiting_tag(self, manager, user, waiting_tag):
        manager._course.get_tag = lambda name: waiting_tag
        manager._course._students = []  # not subscribed

        manager.request_subscribe([user])
        assert user in waiting_tag.students
        assert user not in manager._course._students

    def test_skips_duplicate_waiting(self, manager, user, waiting_tag):
        manager._course.get_tag = lambda name: waiting_tag
        manager.request_subscribe([user])
        manager.request_subscribe([user])
        assert len(waiting_tag.students) == 1

    def test_raises_already_subscribed(self, manager, user):
        manager._course._students.append(user)
        with pytest.raises(ImpossibleOperationError):
            manager.request_subscribe([user])

    def test_raises_teacher_subscribe(self, manager, user):
        user.id = 42
        with pytest.raises(RolesError):
            manager.request_subscribe([user])


class TestDeleteStudents:
    @pytest.mark.parametrize("ids, initial_len, expected_len", [
        ([1], 2, 1),   # present
        ([999], 2, 2),  # absent
        ([], 2, 2),    # empty
    ])
    def test_delete_students(self, manager, user, ids, initial_len, expected_len):
        u1, u2 = user, User("u2@test.com", "pass")
        u1.id = 1
        manager._course._students = [u1, u2]

        manager.delete_students(ids)
        assert len(manager._course._students) == expected_len

    def test_clears_from_tags(self, manager, user, waiting_tag, custom_tag):
        user.id = 1
        manager._course._students = [user]
        manager._course._tags = [waiting_tag, custom_tag]
        waiting_tag.students = [user]
        custom_tag.students = [user]

        manager.delete_students([1])
        assert user not in waiting_tag.students
        assert user not in custom_tag.students
        assert user not in manager._course._students


class TestDeleteStudentsFromTag:
    def test_raises_not_found(self, manager):
        with pytest.raises(UndefinedTagError):
            manager.delete_students_from_tag(999, [1])

    @pytest.mark.parametrize("ids, expected_len", [
        ([1], 1),
        ([999], 2),
        ([], 2),
    ])
    def test_delete_from_tag(self, manager, user, custom_tag, ids, expected_len):
        manager._course.get_tag_by_id = lambda tid: custom_tag if tid == 2 else None
        u1, u2 = user, User("u2@test.com", "pass")
        u1.id = 1
        custom_tag.students = [u1, u2]

        manager.delete_students_from_tag(2, ids)
        assert len(custom_tag.students) == expected_len
