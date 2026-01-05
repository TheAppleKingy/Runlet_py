import pytest

from src.domain.entities import Course, User, Problem, Tag
from src.domain.entities.exceptions import RolesError


def test_course_initialization():
    """Test basic Course initialization"""
    course = Course(
        name="Python 101",
        description="Learn Python basics",
        teacher_id=1,
    )

    assert course.name == "Python 101"
    assert course.description == "Learn Python basics"
    assert course.teacher_id == 1
    assert course.students == tuple()  # Empty tuple
    assert course.problems == []  # Empty list


def test_course_with_students():
    """Test Course initialization and basic student operations"""
    teacher = User(email="teacher@example.com", password="teacher123", id_=1)
    student1 = User(email="student1@example.com", password="student123", id_=2)
    student2 = User(email="student2@example.com", password="student123", id_=3)

    course = Course(
        name="Math",
        description="Mathematics course",
        teacher_id=teacher.id,
    )

    # Test initial state
    assert course.students == tuple()
    assert len(course.students) == 0

    # Test adding students
    course.add_students([student1, student2])
    assert len(course.students) == 2
    assert student1 in course.students
    assert student2 in course.students

    # Test students property returns tuple
    assert isinstance(course.students, tuple)


def test_course_with_problems():
    """Test Course initialization with problems"""
    course = Course(
        name="Programming",
        description="Programming course",
        teacher_id=1,
    )

    problem1 = Problem(name="Hello World", description="Print hello", course_id=course.id)
    problem2 = Problem(name="Calculator", description="Simple calculator", course_id=course.id)

    course.problems.append(problem1)
    course.problems.append(problem2)

    assert len(course.problems) == 2
    assert problem1 in course.problems
    assert problem2 in course.problems


# ===== TEACHER ID TESTS =====

def test_teacher_id_getter():
    """Test teacher_id property getter"""
    course = Course(
        name="Test",
        description="Test",
        teacher_id=42,
    )

    assert course.teacher_id == 42


def test_teacher_id_setter_valid():
    """Test teacher_id setter with valid value"""
    student = User(email="student1@example.com", password="student123", id_=100)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )
    course.add_students([student])

    # Change teacher_id to a value not in students
    course.teacher_id = 50
    assert course.teacher_id == 50


def test_teacher_id_setter_invalid_student_is_teacher():
    """Test teacher_id setter when teacher ID conflicts with student ID"""
    student = User(email="student1@example.com", password="student123", id_=100)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )
    course.add_students([student])

    # Try to set teacher_id to a student's ID
    with pytest.raises(RolesError, match="Teacher cannot be student at the same time"):
        course.teacher_id = 100  # student's ID


def test_teacher_id_setter_with_multiple_students():
    """Test teacher_id setter with multiple students"""
    student1 = User(email="s1@example.com", password="pass", id_=101)
    student2 = User(email="s2@example.com", password="pass", id_=102)
    student3 = User(email="s3@example.com", password="pass", id_=103)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )
    course.add_students([student1, student2, student3])

    # Valid change
    course.teacher_id = 200
    assert course.teacher_id == 200

    # Invalid change - teacher_id equals student1's ID
    with pytest.raises(RolesError):
        course.teacher_id = 101


# ===== STUDENTS PROPERTY TESTS =====

def test_students_getter_empty():
    """Test students getter when no students"""
    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )

    students = course.students
    assert students == tuple()
    assert isinstance(students, tuple)
    assert len(students) == 0


def test_students_getter_with_students():
    """Test students getter with students"""
    student1 = User(email="a@example.com", password="pass", id_=10)
    student2 = User(email="b@example.com", password="pass", id_=11)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )
    course.add_students([student1, student2])

    students = course.students
    assert len(students) == 2
    assert student1 in students
    assert student2 in students
    assert isinstance(students, tuple)


def test_students_setter_valid():
    """Test students setter with valid list"""
    teacher = User(email="teacher@example.com", password="pass", id_=1)
    student1 = User(email="s1@example.com", password="pass", id_=2)
    student2 = User(email="s2@example.com", password="pass", id_=3)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=teacher.id,
    )

    # Set students
    course.students = [student1, student2]

    assert len(course.students) == 2
    assert student1 in course.students
    assert student2 in course.students


def test_students_setter_teacher_in_list():
    """Test students setter when teacher is in the list"""
    teacher = User(email="teacher@example.com", password="pass", id_=1)
    student1 = User(email="s1@example.com", password="pass", id_=2)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=teacher.id,
    )

    # Try to add teacher as student
    with pytest.raises(RolesError, match="is the teacher of this course"):
        course.students = [student1, teacher]  # teacher in list!


def test_students_setter_duplicate_students():
    """Test students setter with duplicate students (list allows duplicates)"""
    student1 = User(email="s1@example.com", password="pass", id_=2)
    student2 = User(email="s2@example.com", password="pass", id_=3)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )

    # List with duplicates - should be accepted (list allows duplicates)
    course.students = [student1, student2, student1]  # student1 appears twice

    # The internal list will have duplicates
    assert len(course._students) == 3  # List has duplicates
    assert len(course.students) == 3  # Tuple also has duplicates


def test_students_setter_empty_list():
    """Test students setter with empty list"""
    student = User(email="s@example.com", password="pass", id_=2)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )
    course.add_students([student])

    # Replace with empty list
    course.students = []

    assert len(course.students) == 0
    assert course._students == []


# ===== ADD_STUDENTS TESTS =====

def test_add_students_empty():
    """Test add_students with empty list"""
    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )

    course.add_students([])
    assert len(course.students) == 0


def test_add_students_single():
    """Test add_students with single student"""
    student = User(email="student@example.com", password="pass", id_=2)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )

    course.add_students([student])
    assert len(course.students) == 1
    assert student in course.students


def test_add_students_multiple():
    """Test add_students with multiple students"""
    student1 = User(email="s1@example.com", password="pass", id_=2)
    student2 = User(email="s2@example.com", password="pass", id_=3)
    student3 = User(email="s3@example.com", password="pass", id_=4)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )

    course.add_students([student1, student2, student3])
    assert len(course.students) == 3
    assert student1 in course.students
    assert student2 in course.students
    assert student3 in course.students


def test_add_students_teacher_in_list():
    """Test add_students when teacher is in the list"""
    teacher = User(email="teacher@example.com", password="pass", id_=1)
    student = User(email="student@example.com", password="pass", id_=2)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=teacher.id,
    )

    with pytest.raises(RolesError, match="is the teacher of this course"):
        course.add_students([student, teacher])  # teacher in list!


def test_add_students_duplicates():
    """Test add_students with duplicate students"""
    student = User(email="student@example.com", password="pass", id_=2)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )

    # Add same student twice
    course.add_students([student])
    course.add_students([student])  # Duplicate

    # List prevents duplicates, so student appears only once
    assert len(course._students) == 1  # List prevents duplicates
    assert course._students.count(student) == 1


def test_add_students_partial_duplicate():
    """Test add_students with some new and some existing students"""
    student1 = User(email="s1@example.com", password="pass", id_=2)
    student2 = User(email="s2@example.com", password="pass", id_=3)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )

    # Add first time
    course.add_students([student1])
    assert len(course._students) == 1

    # Add both - student1 is duplicate, student2 is new
    course.add_students([student1, student2])

    # student1 appears once, student2 once
    assert len(course._students) == 2
    assert course._students.count(student1) == 1
    assert course._students.count(student2) == 1


# ===== DELETE_STUDENTS TESTS =====

def test_delete_students_empty():
    """Test delete_students with empty list"""
    student = User(email="student@example.com", password="pass", id_=2)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )
    course.add_students([student])

    course.delete_students([])
    assert len(course.students) == 1
    assert student in course.students


def test_delete_students_single():
    """Test delete_students with single student"""
    student1 = User(email="s1@example.com", password="pass", id_=2)
    student2 = User(email="s2@example.com", password="pass", id_=3)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )
    course.add_students([student1, student2])

    course.delete_students([student1])
    assert len(course.students) == 1
    assert student2 in course.students
    assert student1 not in course.students


def test_delete_students_multiple():
    """Test delete_students with multiple students"""
    student1 = User(email="s1@example.com", password="pass", id_=2)
    student2 = User(email="s2@example.com", password="pass", id_=3)
    student3 = User(email="s3@example.com", password="pass", id_=4)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )
    course.add_students([student1, student2, student3])

    course.delete_students([student1, student3])
    assert len(course.students) == 1
    assert student2 in course.students
    assert student1 not in course.students
    assert student3 not in course.students


def test_delete_students_nonexistent():
    """Test delete_students with non-existent student"""
    student1 = User(email="s1@example.com", password="pass", id_=2)
    student2 = User(email="s2@example.com", password="pass", id_=3)
    student3 = User(email="s3@example.com", password="pass", id_=4)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )
    course.add_students([student1, student3])

    # Delete student2 (not in course) and student1
    course.delete_students([student1, student2])

    # student1 removed, student2 ignored, student3 remains
    assert len(course.students) == 1
    assert student3 in course.students
    assert student1 not in course.students


def test_delete_students_duplicates_in_list():
    """Test delete_students with duplicate students in input list"""
    student1 = User(email="s1@example.com", password="pass", id_=2)
    student2 = User(email="s2@example.com", password="pass", id_=3)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )
    course.add_students([student1, student2])

    # List with duplicates
    course.delete_students([student1, student1, student1])

    assert len(course.students) == 1
    assert student2 in course.students
    assert student1 not in course.students


def test_delete_students_all():
    """Test delete_students removing all students"""
    student1 = User(email="s1@example.com", password="pass", id_=2)
    student2 = User(email="s2@example.com", password="pass", id_=3)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )
    course.add_students([student1, student2])

    course.delete_students([student1, student2])
    assert len(course.students) == 0
    assert course._students == []


# ===== VALIDATE_TEACHER_IS_STUDENT TESTS =====

def test_validate_teacher_is_student_valid():
    """Test _validate_teacher_is_student with valid input"""
    teacher = User(email="teacher@example.com", password="pass", id_=1)
    student = User(email="student@example.com", password="pass", id_=2)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=teacher.id,
    )

    # Should not raise exception
    course._validate_teacher_is_student([student])


def test_validate_teacher_is_student_invalid():
    """Test _validate_teacher_is_student when teacher is in students list"""
    teacher = User(email="teacher@example.com", password="pass", id_=1)
    student = User(email="student@example.com", password="pass", id_=2)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=teacher.id,
    )

    with pytest.raises(RolesError, match="is the teacher of this course"):
        course._validate_teacher_is_student([student, teacher])


def test_validate_teacher_is_student_teacher_id_match():
    """Test _validate_teacher_is_student when student has same ID as teacher"""
    teacher = User(email="teacher@example.com", password="pass", id_=1)
    # Different user object but same ID as teacher
    student_same_id = User(email="impostor@example.com", password="pass", id_=1)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=teacher.id,
    )

    # Should raise because student has same ID as teacher
    with pytest.raises(RolesError):
        course._validate_teacher_is_student([student_same_id])


# ===== EDGE CASES =====

def test_multiple_operations_sequence():
    """Test sequence of multiple operations"""
    student1 = User(email="s1@example.com", password="pass", id_=2)
    student2 = User(email="s2@example.com", password="pass", id_=3)
    student3 = User(email="s3@example.com", password="pass", id_=4)

    course = Course(
        name="Test Course",
        description="Description",
        teacher_id=1,
    )

    # Add students
    course.add_students([student1, student2])
    assert len(course.students) == 2

    # Add more students
    course.add_students([student3])
    assert len(course.students) == 3

    # Delete some students
    course.delete_students([student1])
    assert len(course.students) == 2
    assert student2 in course.students
    assert student3 in course.students

    # Replace all students
    course.students = [student1]  # student1 is back
    assert len(course.students) == 1
    assert student1 in course.students
    assert student2 not in course.students
    assert student3 not in course.students


def test_problems_list_is_mutable():
    """Test that problems list is mutable and can be modified directly"""
    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )

    problem1 = Problem(name="P1", description="D1", course_id=course.id)
    problem2 = Problem(name="P2", description="D2", course_id=course.id)

    # Direct modification (no setter/getter for problems)
    course.problems.append(problem1)
    course.problems.append(problem2)

    assert len(course.problems) == 2
    assert problem1 in course.problems
    assert problem2 in course.problems

    # Can also modify directly
    course.problems.remove(problem1)
    assert len(course.problems) == 1
    assert problem1 not in course.problems
    assert problem2 in course.problems


def test_students_property_returns_copy():
    """Test that students property returns a tuple (immutable copy)"""
    student = User(email="student@example.com", password="pass", id_=2)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )
    course.add_students([student])

    students_tuple = course.students
    assert isinstance(students_tuple, tuple)

    # Try to modify the tuple (should fail or not affect original)
    # Tuples are immutable, so this would fail
    with pytest.raises(AttributeError):
        students_tuple.append(student)  # Can't append to tuple


def test_concurrent_modification_scenario():
    """Test scenario that might happen in real usage"""
    # Create users
    teacher = User(email="dr.smith@example.com", password="pass", id_=100)
    students = [
        User(email="alice@example.com", password="pass", id_=101),
        User(email="bob@example.com", password="pass", id_=102),
        User(email="charlie@example.com", password="pass", id_=103),
    ]

    # Create course
    course = Course(
        name="Advanced Programming",
        description="Learn advanced programming concepts",
        teacher_id=teacher.id,
    )

    # Add all students
    course.add_students(students)
    assert len(course.students) == 3

    # Bob drops the course
    course.delete_students([students[1]])  # Bob is index 1
    assert len(course.students) == 2
    assert students[0] in course.students  # Alice
    assert students[1] not in course.students  # Bob
    assert students[2] in course.students  # Charlie

    # New student enrolls
    new_student = User(email="diana@example.com", password="pass", id_=104)
    course.add_students([new_student])
    assert len(course.students) == 3
    assert new_student in course.students

    # Teacher tries to enroll as student (should fail)
    with pytest.raises(RolesError):
        course.add_students([teacher])

    # Try to set teacher_id to a student's ID (should fail)
    with pytest.raises(RolesError):
        course.teacher_id = 101  # Alice's ID


# ===== TEST WITH PROBLEM'S COURSE_ID =====

def test_problem_course_id_relationship():
    """Test that problem's course_id relates to course"""
    course = Course(
        name="Math Course",
        description="Math",
        teacher_id=1,
    )
    course.id = 100  # Устанавливаем ID курса

    problem = Problem(name="Algebra Problem", description="Solve equation", course_id=course.id)

    course.problems.append(problem)

    assert len(course.problems) == 1
    assert course.problems[0].course_id == course.id
    assert course.problems[0].name == "Algebra Problem"


def test_course_with_tags():
    """Test that users can have tags"""
    user = User(
        email="user@example.com",
        password="password",
        name="John",
        tags=[Tag(name="python"), Tag(name="backend")]
    )

    course = Course(
        name="Test Course",
        description="Test",
        teacher_id=1,
    )

    course.add_students([user])

    assert len(user.tags) == 2
    assert user.tags[0].name == "python"
    assert user.tags[1].name == "backend"


def test_course_id_property():
    """Test course id property"""
    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )

    assert course.id is None  # По умолчанию None

    course.id = 42
    assert course.id == 42


def test_teacher_without_id():
    """Test course with teacher without id"""
    course = Course(
        name="Test",
        description="Test",
        teacher_id=None,  # Допустимо
    )

    assert course.teacher_id is None

    # Можно установить teacher_id позже
    course.teacher_id = 10
    assert course.teacher_id == 10


def test_add_students_without_ids():
    """Test adding students without ids"""
    student1 = User(email="s1@example.com", password="pass")  # Без id
    student2 = User(email="s2@example.com", password="pass")  # Без id

    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )

    # Должно работать, даже если у студентов нет id
    course.add_students([student1, student2])
    assert len(course.students) == 2

    # Но валидация teacher_id vs student.id все равно работает
    with pytest.raises(RolesError):
        course.teacher_id = None  # teacher_id станет None


def test_teacher_id_none_with_students():
    """Test teacher_id=None with students"""
    student = User(email="student@example.com", password="pass", id_=100)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=None,
    )

    course.add_students([student])

    # Установка teacher_id в None должна работать
    course.teacher_id = None
    assert course.teacher_id is None


def test_delete_nonexistent_student_no_error():
    """Test deleting non-existent student doesn't cause error"""
    student1 = User(email="s1@example.com", password="pass", id_=3)
    student2 = User(email="s2@example.com", password="pass", id_=2)

    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )

    course.add_students([student1])

    # Удаление несуществующего студента (student2) не должно вызывать ошибку
    course.delete_students([student2])
    assert len(course.students) == 1
    assert student1 in course.students


def test_students_setter_with_none():
    """Test students setter with None (should raise TypeError)"""
    course = Course(
        name="Test",
        description="Test",
        teacher_id=1,
    )

    with pytest.raises(TypeError):
        course.students = None  # Должно требовать list


def test_course_with_default_values():
    """Test Course with all default values"""
    course = Course()

    assert course.name == ""
    assert course.description == ""
    assert course.teacher_id is None
    assert course.students == tuple()
    assert course.problems == []
    assert course.id is None


def test_course_comparison():
    """Test that Course objects can be compared"""
    course1 = Course(name="Math", teacher_id=1, id=10)
    course2 = Course(name="Math", teacher_id=1, id=10)
    course3 = Course(name="Physics", teacher_id=2, id=20)

    # Обычные классы без __eq__ сравниваются по id объекта
    assert course1 != course2  # Разные объекты
    assert course1 != course3  # Разные объекты

    # Но можно сравнивать атрибуты
    assert course1.name == course2.name
    assert course1.teacher_id == course2.teacher_id
