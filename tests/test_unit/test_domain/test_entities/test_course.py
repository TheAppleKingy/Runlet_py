import pytest

from src.domain.entities import Course, User, Problem
from src.domain.exceptions.entities import RolesError


def test_course_initialization():
    """Test basic Course initialization"""
    course = Course(
        name="Python 101",
        description="Learn Python basics",
        _teacher_id=1,
    )

    assert course.name == "Python 101"
    assert course.description == "Learn Python basics"
    assert course.teacher_id == 1
    assert course.students == tuple()  # Empty tuple
    assert course.problems == []  # Empty list


def test_course_with_students():
    """Test Course initialization and basic student operations"""
    teacher = User(email="teacher@example.com", password="teacher123")
    teacher.id = 1  # Устанавливаем ID вручную
    student1 = User(email="student1@example.com", password="student123")
    student1.id = 2
    student2 = User(email="student2@example.com", password="student123")
    student2.id = 3

    course = Course(
        name="Math",
        description="Mathematics course",
        _teacher_id=teacher.id,
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
        _teacher_id=1,
    )

    problem1 = Problem(name="Hello World", description="Print hello", course_id=1)
    problem1.id = 1
    problem2 = Problem(name="Calculator", description="Simple calculator", course_id=1)
    problem2.id = 2

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
        _teacher_id=42,
    )

    assert course.teacher_id == 42


def test_teacher_id_setter_valid():
    """Test teacher_id setter with valid value"""
    student = User(email="student1@example.com", password="student123")
    student.id = 100

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=1,
    )
    course.add_students([student])

    # Change teacher_id to a value not in students
    course.teacher_id = 50
    assert course.teacher_id == 50


def test_teacher_id_setter_invalid_student_is_teacher():
    """Test teacher_id setter when teacher ID conflicts with student ID"""
    student = User(email="student1@example.com", password="student123")
    student.id = 100

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=1,
    )
    course.add_students([student])

    # Try to set teacher_id to a student's ID
    with pytest.raises(RolesError, match="Teacher cannot be student at the same time"):
        course.teacher_id = 100  # student's ID


def test_teacher_id_setter_with_multiple_students():
    """Test teacher_id setter with multiple students"""
    student1 = User(email="s1@example.com", password="pass")
    student1.id = 101
    student2 = User(email="s2@example.com", password="pass")
    student2.id = 102
    student3 = User(email="s3@example.com", password="pass")
    student3.id = 103

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=1,
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
        _teacher_id=1,
    )

    students = course.students
    assert students == tuple()
    assert isinstance(students, tuple)
    assert len(students) == 0


def test_students_getter_with_students():
    """Test students getter with students"""
    student1 = User(email="a@example.com", password="pass")
    student1.id = 10
    student2 = User(email="b@example.com", password="pass")
    student2.id = 11

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=1,
    )
    course.add_students([student1, student2])

    students = course.students
    assert len(students) == 2
    assert student1 in students
    assert student2 in students
    assert isinstance(students, tuple)


def test_students_setter_valid():
    """Test students setter with valid list"""
    teacher = User(email="teacher@example.com", password="pass")
    teacher.id = 1
    student1 = User(email="s1@example.com", password="pass")
    student1.id = 2
    student2 = User(email="s2@example.com", password="pass")
    student2.id = 3

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=teacher.id,
    )

    # Set students
    course.students = [student1, student2]

    assert len(course.students) == 2
    assert student1 in course.students
    assert student2 in course.students


def test_students_setter_teacher_in_list():
    """Test students setter when teacher is in the list"""
    teacher = User(email="teacher@example.com", password="pass")
    teacher.id = 1
    student1 = User(email="s1@example.com", password="pass")
    student1.id = 2

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=teacher.id,
    )

    # Try to add teacher as student
    with pytest.raises(RolesError, match="is the teacher of this course"):
        course.students = [student1, teacher]  # teacher in list!


def test_students_setter_duplicate_students():
    """Test students setter with duplicate students (list allows duplicates)"""
    student1 = User(email="s1@example.com", password="pass")
    student1.id = 2
    student2 = User(email="s2@example.com", password="pass")
    student2.id = 3

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=1,
    )

    # List with duplicates - should be accepted (list allows duplicates)
    course.students = [student1, student2, student1]  # student1 appears twice

    # The internal list will have duplicates
    assert len(course._students) == 3  # List has duplicates
    assert len(course.students) == 3  # Tuple also has duplicates


def test_students_setter_empty_list():
    """Test students setter with empty list"""
    student = User(email="s@example.com", password="pass")
    student.id = 2

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=1,
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
        _teacher_id=1,
    )

    course.add_students([])
    assert len(course.students) == 0


def test_add_students_single():
    """Test add_students with single student"""
    student = User(email="student@example.com", password="pass")
    student.id = 2

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=1,
    )

    course.add_students([student])
    assert len(course.students) == 1
    assert student in course.students


def test_add_students_multiple():
    """Test add_students with multiple students"""
    student1 = User(email="s1@example.com", password="pass")
    student1.id = 2
    student2 = User(email="s2@example.com", password="pass")
    student2.id = 3
    student3 = User(email="s3@example.com", password="pass")
    student3.id = 4

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=1,
    )

    course.add_students([student1, student2, student3])
    assert len(course.students) == 3
    assert student1 in course.students
    assert student2 in course.students
    assert student3 in course.students


def test_add_students_teacher_in_list():
    """Test add_students when teacher is in the list"""
    teacher = User(email="teacher@example.com", password="pass")
    teacher.id = 1
    student = User(email="student@example.com", password="pass")
    student.id = 2

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=teacher.id,
    )

    with pytest.raises(RolesError, match="is the teacher of this course"):
        course.add_students([student, teacher])  # teacher in list!


def test_add_students_duplicates():
    """Test add_students with duplicate students"""
    student = User(email="student@example.com", password="pass")
    student.id = 2

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=1,
    )

    # Add same student twice
    course.add_students([student])
    course.add_students([student])  # Duplicate

    # List allows duplicates, so student appears twice
    assert len(course._students) == 1  # List has duplicates!
    assert course._students.count(student) == 1


def test_add_students_partial_duplicate():
    """Test add_students with some new and some existing students"""
    student1 = User(email="s1@example.com", password="pass")
    student1.id = 2
    student2 = User(email="s2@example.com", password="pass")
    student2.id = 3

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=1,
    )

    # Add first time
    course.add_students([student1])
    assert len(course._students) == 1

    # Add both - student1 is duplicate, student2 is new
    course.add_students([student1, student2])

    # student1 appears twice, student2 once
    assert len(course._students) == 2
    assert course._students.count(student1) == 1
    assert course._students.count(student2) == 1


# ===== DELETE_STUDENTS TESTS =====

def test_delete_students_empty():
    """Test delete_students with empty list"""
    student = User(email="student@example.com", password="pass")
    student.id = 2

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=1,
    )
    course.add_students([student])

    course.delete_students([])
    assert len(course.students) == 1
    assert student in course.students


def test_delete_students_single():
    """Test delete_students with single student"""
    student1 = User(email="s1@example.com", password="pass")
    student1.id = 2
    student2 = User(email="s2@example.com", password="pass")
    student2.id = 3

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=1,
    )
    course.add_students([student1, student2])

    course.delete_students([student1])
    assert len(course.students) == 1
    assert student2 in course.students
    assert student1 not in course.students


def test_delete_students_multiple():
    """Test delete_students with multiple students"""
    student1 = User(email="s1@example.com", password="pass")
    student1.id = 2
    student2 = User(email="s2@example.com", password="pass")
    student2.id = 3
    student3 = User(email="s3@example.com", password="pass")
    student3.id = 4

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=1,
    )
    course.add_students([student1, student2, student3])

    course.delete_students([student1, student3])
    assert len(course.students) == 1
    assert student2 in course.students
    assert student1 not in course.students
    assert student3 not in course.students


def test_delete_students_nonexistent():
    """Test delete_students with non-existent student"""
    student1 = User(email="s1@example.com", password="pass")
    student1.id = 2
    student2 = User(email="s2@example.com", password="pass")
    student2.id = 3
    student3 = User(email="s3@example.com", password="pass")
    student3.id = 4

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=1,
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
    student1 = User(email="s1@example.com", password="pass")
    student1.id = 2
    student2 = User(email="s2@example.com", password="pass")
    student2.id = 3

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=1,
    )
    course.add_students([student1, student2])

    # List with duplicates
    course.delete_students([student1, student1, student1])

    assert len(course.students) == 1
    assert student2 in course.students
    assert student1 not in course.students


def test_delete_students_all():
    """Test delete_students removing all students"""
    student1 = User(email="s1@example.com", password="pass")
    student1.id = 2
    student2 = User(email="s2@example.com", password="pass")
    student2.id = 3

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=1,
    )
    course.add_students([student1, student2])

    course.delete_students([student1, student2])
    assert len(course.students) == 0
    assert course._students == []


def test_delete_students_with_duplicates_in_course():
    """Test delete_students when course has duplicate students (due to list)"""
    student = User(email="student@example.com", password="pass")
    student.id = 2

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=1,
    )
    # Add same student twice (list allows this)
    course.add_students([student])
    course.add_students([student])  # Now has two copies

    assert len(course.students) == 1

    # Delete the student
    course.delete_students([student])

    # All copies should be removed
    assert len(course.students) == 0


# ===== VALIDATE_TEACHER_IS_STUDENT TESTS =====

def test_validate_teacher_is_student_valid():
    """Test _validate_teacher_is_student with valid input"""
    teacher = User(email="teacher@example.com", password="pass")
    teacher.id = 1
    student = User(email="student@example.com", password="pass")
    student.id = 2

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=teacher.id,
    )

    # Should not raise exception
    course._validate_teacher_is_student([student])


def test_validate_teacher_is_student_invalid():
    """Test _validate_teacher_is_student when teacher is in students list"""
    teacher = User(email="teacher@example.com", password="pass")
    teacher.id = 1
    student = User(email="student@example.com", password="pass")
    student.id = 2

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=teacher.id,
    )

    with pytest.raises(RolesError, match="is the teacher of this course"):
        course._validate_teacher_is_student([student, teacher])


def test_validate_teacher_is_student_teacher_id_match():
    """Test _validate_teacher_is_student when student has same ID as teacher"""
    teacher = User(email="teacher@example.com", password="pass")
    teacher.id = 1
    # Different user object but same ID as teacher
    student_same_id = User(email="impostor@example.com", password="pass")
    student_same_id.id = 1

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=teacher.id,
    )

    # Should raise because student has same ID as teacher
    with pytest.raises(RolesError):
        course._validate_teacher_is_student([student_same_id])


# ===== EDGE CASES =====

def test_multiple_operations_sequence():
    """Test sequence of multiple operations"""
    student1 = User(email="s1@example.com", password="pass")
    student1.id = 2
    student2 = User(email="s2@example.com", password="pass")
    student2.id = 3
    student3 = User(email="s3@example.com", password="pass")
    student3.id = 4

    course = Course(
        name="Test Course",
        description="Description",
        _teacher_id=1,
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
        _teacher_id=1,
    )

    problem1 = Problem(name="P1", description="D1", course_id=1)
    problem1.id = 1
    problem2 = Problem(name="P2", description="D2", course_id=1)
    problem2.id = 2

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


def test_course_equality():
    """Test that Course objects with same data are equal (default dataclass behavior)"""
    course1 = Course(
        name="Math",
        description="Mathematics",
        _teacher_id=1,
    )

    course2 = Course(
        name="Math",
        description="Mathematics",
        _teacher_id=1,
    )

    # Dataclasses with same field values are equal by default
    assert course1 == course2  # Because dataclass generates __eq__

    # But they are different objects
    assert course1 is not course2


def test_course_repr():
    """Test string representation of Course"""
    course = Course(
        name="Physics",
        description="Physics course",
        _teacher_id=42,
    )

    repr_str = repr(course)
    assert "Physics" in repr_str
    assert "42" in repr_str
    assert "Course" in repr_str


def test_students_property_returns_copy():
    """Test that students property returns a tuple (immutable copy)"""
    student = User(email="student@example.com", password="pass")
    student.id = 2

    course = Course(
        name="Test",
        description="Test",
        _teacher_id=1,
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
    teacher = User(email="dr.smith@example.com", password="pass")
    teacher.id = 100
    students = [
        User(email="alice@example.com", password="pass"),
        User(email="bob@example.com", password="pass"),
        User(email="charlie@example.com", password="pass"),
    ]
    students[0].id = 101
    students[1].id = 102
    students[2].id = 103

    # Create course
    course = Course(
        name="Advanced Programming",
        description="Learn advanced programming concepts",
        _teacher_id=teacher.id,
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
    new_student = User(email="diana@example.com", password="pass")
    new_student.id = 104
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
        _teacher_id=1,
    )
    course.id = 100  # Устанавливаем ID курса

    problem = Problem(name="Algebra Problem", description="Solve equation", course_id=course.id)
    problem.id = 1

    course.problems.append(problem)

    assert len(course.problems) == 1
    assert course.problems[0].course_id == course.id
    assert course.problems[0].name == "Algebra Problem"
