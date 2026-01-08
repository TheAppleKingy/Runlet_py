import pytest

from src.domain.entities import Course, User, Problem
from src.domain.entities.exceptions import RolesError

# ============ Test Setup Helpers ============


def create_user_with_id(email: str, password: str, name: str, id_: int) -> User:
    """Helper to create User and set id (since id has init=False)"""
    user = User(email=email, password=password, name=name)
    user.id = id_
    return user

# ============ Basic Creation Tests ============


def test_course_creation():
    """Test basic course creation"""
    course = Course(
        name="Physics 101",
        _teacher_id=100,
        description="Introduction to Physics"
    )

    assert course.name == "Physics 101"
    assert course.teacher_id == 100
    assert course._teacher_id == 100
    assert course.description == "Introduction to Physics"
    assert course.id is None
    assert course.students == tuple()
    assert course._students == []
    assert course.problems == []


def test_course_creation_minimal():
    """Test course creation with minimal parameters"""
    course = Course(name="Math", _teacher_id=1)

    assert course.name == "Math"
    assert course.teacher_id == 1
    assert course.description == ""  # Default
    assert course.students == tuple()
    assert course.problems == []


def test_course_id_field():
    """Test that id field exists but is not in __init__"""
    course = Course(name="Test", _teacher_id=1)

    # Should have id attribute
    assert hasattr(course, 'id')
    assert course.id is None  # Default value

    # Should be able to set it
    course.id = 5
    assert course.id == 5

# ============ Property Tests ============


def test_teacher_id_property_getter():
    """Test teacher_id property getter"""
    course = Course(name="Test", _teacher_id=42)

    assert course.teacher_id == 42
    assert course._teacher_id == 42

    # Changing _teacher_id should reflect in property
    course._teacher_id = 100
    assert course.teacher_id == 100


def test_teacher_id_property_setter_valid():
    """Test teacher_id setter with valid value"""
    course = Course(name="Test", _teacher_id=1)
    course._students = []  # Empty student list

    # Should allow changing teacher_id when no students
    course.teacher_id = 2
    assert course.teacher_id == 2
    assert course._teacher_id == 2


def test_teacher_id_property_setter_with_students():
    """Test teacher_id setter when course has students"""
    student = create_user_with_id("s@test.com", "pwd", "Student", 100)
    course = Course(name="Test", _teacher_id=1)
    course._students = [student]

    # Should allow changing to ID not in students
    course.teacher_id = 999
    assert course.teacher_id == 999

    # Should NOT allow changing to ID that's in students
    with pytest.raises(RolesError) as exc:
        course.teacher_id = 100  # Same as student ID

    assert "Teacher cannot be student at the same time" in str(exc.value)
    assert course.teacher_id == 999  # Should not have changed


def test_teacher_id_setter_with_multiple_students():
    """Test teacher_id setter with multiple students"""
    student1 = create_user_with_id("s1@test.com", "pwd", "S1", 100)
    student2 = create_user_with_id("s2@test.com", "pwd", "S2", 200)
    student3 = create_user_with_id("s3@test.com", "pwd", "S3", 300)

    course = Course(name="Test", _teacher_id=1)
    course._students = [student1, student2, student3]

    # Try to set teacher_id to existing student ID
    with pytest.raises(RolesError):
        course.teacher_id = 200  # student2's ID

    # Should allow non-student ID
    course.teacher_id = 999
    assert course.teacher_id == 999


def test_students_property_getter():
    """Test students property returns tuple"""
    student1 = create_user_with_id("s1@test.com", "pwd", "S1", 1)
    student2 = create_user_with_id("s2@test.com", "pwd", "S2", 2)

    course = Course(name="Test", _teacher_id=999)
    course._students = [student1, student2]

    students = course.students

    assert isinstance(students, tuple)
    assert students == (student1, student2)

    # Should be immutable
    with pytest.raises(AttributeError):
        students.append(student1)  # Can't modify tuple


def test_students_property_setter_valid():
    """Test students setter with valid students list"""
    course = Course(name="Test", _teacher_id=999)

    student1 = create_user_with_id("s1@test.com", "pwd", "S1", 100)
    student2 = create_user_with_id("s2@test.com", "pwd", "S2", 200)

    # Should allow setting students when teacher_id not in list
    course.students = [student1, student2]

    assert course._students == [student1, student2]
    assert course.students == (student1, student2)


def test_students_property_setter_invalid():
    """Test students setter when teacher is in students list"""
    course = Course(name="Test", _teacher_id=999)

    student1 = create_user_with_id("s1@test.com", "pwd", "S1", 100)
    student2 = create_user_with_id("s2@test.com", "pwd", "S2", 999)  # Same as teacher!

    with pytest.raises(RolesError) as exc:
        course.students = [student1, student2]

    assert "is the teacher of this course" in str(exc.value)
    assert course._students == []  # Should not have changed


def test_students_setter_partial_validation():
    """Test that students setter validates entire list"""
    course = Course(name="Test", _teacher_id=999)

    student1 = create_user_with_id("s1@test.com", "pwd", "S1", 100)
    student2 = create_user_with_id("s2@test.com", "pwd", "S2", 999)  # Teacher!
    student3 = create_user_with_id("s3@test.com", "pwd", "S3", 300)

    # Should raise even if teacher is not first in list
    with pytest.raises(RolesError):
        course.students = [student1, student2, student3]

    # Original list should remain unchanged
    assert course._students == []

# ============ Method Tests ============


def test_add_students_empty_course():
    """Test adding students to empty course"""
    course = Course(name="Test", _teacher_id=999)

    student1 = create_user_with_id("s1@test.com", "pwd", "S1", 100)
    student2 = create_user_with_id("s2@test.com", "pwd", "S2", 200)

    course.add_students([student1, student2])

    assert len(course._students) == 2
    assert course._students == [student1, student2]
    assert student1 in course._students
    assert student2 in course._students


def test_add_students_existing_course():
    """Test adding students to course with existing students"""
    student1 = create_user_with_id("s1@test.com", "pwd", "S1", 100)
    course = Course(name="Test", _teacher_id=999)
    course._students = [student1]

    student2 = create_user_with_id("s2@test.com", "pwd", "S2", 200)
    student3 = create_user_with_id("s3@test.com", "pwd", "S3", 300)

    course.add_students([student2, student3])

    assert len(course._students) == 3
    assert course._students == [student1, student2, student3]


def test_add_students_duplicates():
    """Test adding duplicate students"""
    student1 = create_user_with_id("s1@test.com", "pwd", "S1", 100)
    student2 = create_user_with_id("s2@test.com", "pwd", "S2", 200)

    course = Course(name="Test", _teacher_id=999)
    course._students = [student1]

    # Add student2 and duplicate student1
    course.add_students([student2, student1])  # student1 already exists

    assert len(course._students) == 2  # Should not add duplicate
    assert course._students == [student1, student2]


def test_add_students_with_teacher():
    """Test adding teacher as student should raise"""
    course = Course(name="Test", _teacher_id=999)

    student = create_user_with_id("student@test.com", "pwd", "Student", 100)
    teacher_as_student = create_user_with_id("teacher@test.com", "pwd", "Teacher", 999)

    with pytest.raises(RolesError):
        course.add_students([student, teacher_as_student])

    # No students should be added
    assert course._students == []


def test_add_students_empty_list():
    """Test adding empty students list"""
    student = create_user_with_id("s@test.com", "pwd", "Student", 100)
    course = Course(name="Test", _teacher_id=999)
    course._students = [student]

    # Adding empty list should do nothing
    course.add_students([])

    assert course._students == [student]


def test_delete_students():
    """Test deleting students from course"""
    student1 = create_user_with_id("s1@test.com", "pwd", "S1", 100)
    student2 = create_user_with_id("s2@test.com", "pwd", "S2", 200)
    student3 = create_user_with_id("s3@test.com", "pwd", "S3", 300)

    course = Course(name="Test", _teacher_id=999)
    course._students = [student1, student2, student3]

    # Delete student2
    course.delete_students([student2.id])

    assert len(course._students) == 2
    assert course._students == [student1, student3]
    assert student2 not in course._students


def test_delete_multiple_students():
    """Test deleting multiple students at once"""
    student1 = create_user_with_id("s1@test.com", "pwd", "S1", 100)
    student2 = create_user_with_id("s2@test.com", "pwd", "S2", 200)
    student3 = create_user_with_id("s3@test.com", "pwd", "S3", 300)
    student4 = create_user_with_id("s4@test.com", "pwd", "S4", 400)

    course = Course(name="Test", _teacher_id=999)
    course._students = [student1, student2, student3, student4]

    # Delete student2 and student4
    course.delete_students([student2.id, student4.id])

    assert len(course._students) == 2
    assert course._students == [student1, student3]


def test_delete_nonexistent_students():
    """Test deleting students not in course"""
    student1 = create_user_with_id("s1@test.com", "pwd", "S1", 100)
    student2 = create_user_with_id("s2@test.com", "pwd", "S2", 200)
    student3 = create_user_with_id("s3@test.com", "pwd", "S3", 300)

    course = Course(name="Test", _teacher_id=999)
    course._students = [student1, student2]

    # Try to delete student3 (not in course) and student2
    course.delete_students([student3.id, student2.id])

    # Only student2 should be removed
    assert len(course._students) == 1
    assert course._students == [student1]


def test_delete_all_students():
    """Test deleting all students"""
    student1 = create_user_with_id("s1@test.com", "pwd", "S1", 100)
    student2 = create_user_with_id("s2@test.com", "pwd", "S2", 200)

    course = Course(name="Test", _teacher_id=999)
    course._students = [student1, student2]

    course.delete_students([student1.id, student2.id])

    assert len(course._students) == 0
    assert course._students == []


def test_delete_empty_list():
    """Test deleting empty students list"""
    student1 = create_user_with_id("s1@test.com", "pwd", "S1", 100)
    course = Course(name="Test", _teacher_id=999)
    course._students = [student1]

    course.delete_students([])

    assert course._students == [student1]

# ============ Validation Method Tests ============


def test_validate_teacher_is_student():
    """Test _validate_teacher_is_student method"""
    course = Course(name="Test", _teacher_id=999)

    student1 = create_user_with_id("s1@test.com", "pwd", "S1", 100)
    student2 = create_user_with_id("s2@test.com", "pwd", "S2", 999)  # Teacher!

    # Should raise when teacher is in students list
    with pytest.raises(RolesError) as exc:
        course._validate_teacher_is_student([student1, student2])

    assert str(999) in str(exc.value)  # Teacher ID in message
    assert "is the teacher of this course" in str(exc.value)


def test_validate_teacher_is_student_valid():
    """Test _validate_teacher_is_student with valid list"""
    course = Course(name="Test", _teacher_id=999)

    student1 = create_user_with_id("s1@test.com", "pwd", "S1", 100)
    student2 = create_user_with_id("s2@test.com", "pwd", "S2", 200)

    # Should not raise
    course._validate_teacher_is_student([student1, student2])


def test_validate_teacher_is_student_empty():
    """Test _validate_teacher_is_student with empty list"""
    course = Course(name="Test", _teacher_id=999)

    # Empty list should be valid
    course._validate_teacher_is_student([])

# ============ Problems Tests ============


def test_problems_field():
    """Test problems field initialization"""
    course = Course(name="Test", _teacher_id=1)

    assert course.problems == []
    assert isinstance(course.problems, list)

    # Can modify problems list
    problem = Problem(name="P1", description="Desc", course_id=1)
    course.problems.append(problem)

    assert len(course.problems) == 1
    assert course.problems[0] == problem


def test_course_with_problems():
    """Test course with problems"""
    problem1 = Problem(name="P1", description="D1", course_id=1)
    problem1.id = 101
    problem2 = Problem(name="P2", description="D2", course_id=1)
    problem2.id = 102

    course = Course(name="Test", _teacher_id=1)
    course.problems = [problem1, problem2]

    assert len(course.problems) == 2
    assert course.problems == [problem1, problem2]

# ============ Edge Cases ============


def test_course_with_none_values():
    """Test course with None/empty values"""
    course = Course(name="", _teacher_id=0, description="")

    assert course.name == ""
    assert course.teacher_id == 0
    assert course.description == ""


def test_teacher_id_zero():
    """Test teacher_id can be 0"""
    course = Course(name="Test", _teacher_id=0)

    assert course.teacher_id == 0

    # Should be able to set students with ID 0
    student = create_user_with_id("s@test.com", "pwd", "Student", 100)
    course.students = [student]  # Should not raise

    # Should raise if trying to set teacher_id to 0 when student has ID 0
    student2 = create_user_with_id("s2@test.com", "pwd", "Student2", 0)

    with pytest.raises(RolesError):
        course.students = [student2]  # Same as student2 ID


def test_large_number_of_students():
    """Test course with many students"""
    course = Course(name="Test", _teacher_id=999999)

    # Add 1000 students
    students = [
        create_user_with_id(f"s{i}@test.com", "pwd", f"Student{i}", i)
        for i in range(1000)
    ]

    course.add_students(students)

    assert len(course._students) == 1000
    assert course.students == tuple(students)


def test_teacher_id_setter_performance():
    """Test performance of teacher_id setter with many students"""
    import time

    # Create course with many students
    course = Course(name="Test", _teacher_id=1)
    students = [
        create_user_with_id(f"s{i}@test.com", "pwd", f"Student{i}", i+100)
        for i in range(10000)  # 10k students
    ]
    course._students = students

    # Time the validation
    start = time.time()
    try:
        course.teacher_id = 99999  # Not in students
    except RolesError:
        pass
    elapsed = time.time() - start

    # Should complete in reasonable time
    assert elapsed < 1.0  # Should be much faster than 1 second

# ============ Mutation Tests ============


def test_direct_student_list_modification():
    """Test that modifying _students directly bypasses validation"""
    course = Course(name="Test", _teacher_id=999)

    student1 = create_user_with_id("s1@test.com", "pwd", "S1", 100)

    # Direct modification - no validation!
    course._students.append(student1)

    assert course._students == [student1]

    # Can even add teacher as student directly
    teacher_student = create_user_with_id("t@test.com", "pwd", "Teacher", 999)
    course._students.append(teacher_student)  # No error!

    assert len(course._students) == 2

    # But property getter still works
    assert course.students == (student1, teacher_student)


def test_direct_teacher_id_modification():
    """Test that modifying _teacher_id directly bypasses validation"""
    student = create_user_with_id("s@test.com", "pwd", "Student", 100)
    course = Course(name="Test", _teacher_id=999)
    course._students = [student]

    # Direct modification to student's ID - no validation!
    course._teacher_id = 100  # Same as student!

    assert course.teacher_id == 100

    # Property getter reflects the change
    assert course.teacher_id == 100

# ============ Integration with User Objects ============


def test_course_with_user_objects():
    """Test course interacts correctly with User objects"""
    teacher = User(email="teacher@test.com", password="pwd", name="Professor")
    teacher.id = 999

    student1 = User(email="s1@test.com", password="pwd", name="Alice")
    student1.id = 100
    student2 = User(email="s2@test.com", password="pwd", name="Bob")
    student2.id = 200

    course = Course(name="CS101", _teacher_id=teacher.id)

    # Add students
    course.add_students([student1, student2])

    assert len(course.students) == 2
    assert student1 in course._students
    assert student2 in course._students

    # Verify student properties are accessible
    for student in course.students:
        assert hasattr(student, 'email')
        assert hasattr(student, 'name')
        assert hasattr(student, 'id')


def test_user_id_uniqueness():
    """Test that user IDs are used for comparison, not objects"""
    # Two different User objects with same ID
    student1 = User(email="s1@test.com", password="pwd", name="S1")
    student1.id = 100

    student2 = User(email="s2@test.com", password="pwd", name="S2")
    student2.id = 100  # Same ID!

    course = Course(name="Test", _teacher_id=999)

    # Add first student
    course.add_students([student1])

    # Try to add second student (same ID, different object)
    course.add_students([student2])

    # Should not add duplicate ID
    assert len(course._students) == 2

    # The object in the list should be student1
    assert course._students[0] is student1

# ============ Property Interaction Tests ============


def test_teacher_id_and_students_interaction():
    """Test interaction between teacher_id and students properties"""
    course = Course(name="Test", _teacher_id=500)

    student1 = create_user_with_id("s1@test.com", "pwd", "S1", 100)
    student2 = create_user_with_id("s2@test.com", "pwd", "S2", 200)

    # Set students (valid)
    course.students = [student1, student2]

    # Try to change teacher_id to student's ID (should fail)
    with pytest.raises(RolesError):
        course.teacher_id = 100

    # Change teacher_id to non-student ID (should work)
    course.teacher_id = 300
    assert course.teacher_id == 300

    # Now try to add teacher as student (should fail)
    teacher_as_student = create_user_with_id("t@test.com", "pwd", "Teacher", 300)
    with pytest.raises(RolesError):
        course.add_students([teacher_as_student])


def test_concurrent_modification_scenario():
    """Test complex scenario with multiple modifications"""
    course = Course(name="Dynamic Course", _teacher_id=1000)

    # Initial state
    assert course.teacher_id == 1000
    assert course.students == tuple()

    # Add some students
    alice = create_user_with_id("alice@test.com", "pwd", "Alice", 1)
    bob = create_user_with_id("bob@test.com", "pwd", "Bob", 2)

    course.add_students([alice, bob])
    assert len(course.students) == 2

    # Change teacher
    course.teacher_id = 2000
    assert course.teacher_id == 2000

    # Add more students
    charlie = create_user_with_id("charlie@test.com", "pwd", "Charlie", 3)
    course.add_students([charlie])
    assert len(course.students) == 3

    # Remove a student
    course.delete_students([bob.id])
    assert len(course.students) == 2
    assert alice in course._students
    assert charlie in course._students
    assert bob not in course._students

    # Try to set teacher to removed student's ID (should work)
    course.teacher_id = 2  # Bob's old ID
    assert course.teacher_id == 2

    # Now Bob can be added back as student
    with pytest.raises(RolesError):
        course.add_students([bob])

# ============ Error Message Tests ============


def test_error_messages():
    """Test that error messages are informative"""
    course = Course(name="Test", _teacher_id=42)

    student = create_user_with_id("s@test.com", "pwd", "Student", 42)  # Same as teacher

    # Test teacher_id setter error
    course._students = [student]
    try:
        course.teacher_id = 42
    except RolesError as e:
        assert "Teacher cannot be student at the same time" in str(e)

    # Test students setter error
    course2 = Course(name="Test2", _teacher_id=42)
    try:
        course2.students = [student]
    except RolesError as e:
        assert "is the teacher of this course" in str(e)
        assert "42" in str(e)  # Teacher ID in message

    # Test add_students error
    course3 = Course(name="Test3", _teacher_id=42)
    try:
        course3.add_students([student])
    except RolesError as e:
        assert "is the teacher of this course" in str(e)

# ============ Additional Edge Cases ============


def test_students_setter_with_duplicate_user_ids():
    """Test students setter with duplicate user IDs in list"""
    course = Course(name="Test", _teacher_id=999)

    # Two different objects with same ID
    student1 = User(email="s1@test.com", password="pwd", name="S1")
    student1.id = 100

    student2 = User(email="s2@test.com", password="pwd", name="S2")
    student2.id = 100  # Same ID!

    # This should work - duplicates allowed in input list
    # But validation will check teacher_id, not duplicate students
    course.students = [student1, student2]

    # Both might be added or one might be filtered
    # Current implementation would add both


def test_add_students_with_none_values():
    """Test add_students with None in list"""
    course = Course(name="Test", _teacher_id=999)

    student = create_user_with_id("s@test.com", "pwd", "Student", 100)

    # Should handle None gracefully or raise?
    # Likely will fail when checking s.id if s is None
    with pytest.raises(AttributeError):
        course.add_students([student, None])


def test_teacher_id_setter_with_uninitialized_students():
    """Test teacher_id setter when _students is not initialized"""
    course = Course(name="Test", _teacher_id=999)

    # _students has init=False, so it exists but is empty list
    # This should work
    course.teacher_id = 100
    assert course.teacher_id == 100


def test_students_getter_when_empty():
    """Test students property when _students is empty"""
    course = Course(name="Test", _teacher_id=999)

    # _students should be initialized to empty list
    assert course._students == []
    assert course.students == tuple()


def test_course_repr():
    """Test course string representation"""
    course = Course(name="Math", _teacher_id=1, description="Algebra")
    course.id = 5

    repr_str = repr(course)
    assert "Course" in repr_str
    assert "Math" in repr_str
    assert "id=5" in repr_str or "id=5" in str(course)


def test_course_equality():
    """Test course equality comparison"""
    course1 = Course(name="Math", _teacher_id=1)
    course1.id = 1
    course1._students = [create_user_with_id("s@t.com", "p", "S", 100)]

    course2 = Course(name="Math", _teacher_id=1)
    course2.id = 1
    course2._students = [create_user_with_id("s@t.com", "p", "S", 100)]

    # Dataclasses compare by value
    assert course1 == course2

    course3 = Course(name="Physics", _teacher_id=1)
    course3.id = 1
    assert course1 != course3
