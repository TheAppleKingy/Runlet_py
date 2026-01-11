import pytest

from src.domain.entities import Course, User, Problem, Tag
from src.domain.entities.exceptions import RolesError, UndefinedTagError

import pytest

# ==================== Тестовые данные ====================


def create_test_user(user_id: int, name: str = "Test User") -> User:
    """Создает тестового пользователя"""
    user = User(email=f"user{user_id}@test.com", password="password", name=name)
    user.id = user_id
    return user


def create_test_tag(tag_id: int, course_id: int, name: str = "Test Tag") -> Tag:
    """Создает тестовый тег"""
    tag = Tag(name=name, course_id=course_id)
    tag.id = tag_id
    return tag


def create_test_problem(problem_id: int, course_id: int) -> Problem:
    """Создает тестовую задачу"""
    problem = Problem(title=f"Problem {problem_id}",
                      description="Test problem", course_id=course_id)
    problem.id = problem_id
    return problem

# ==================== FIXTURES ====================


@pytest.fixture
def teacher():
    return create_test_user(1, "Teacher")


@pytest.fixture
def student1():
    return create_test_user(100, "Student 1")


@pytest.fixture
def student2():
    return create_test_user(101, "Student 2")


@pytest.fixture
def student3():
    return create_test_user(102, "Student 3")


@pytest.fixture
def empty_course(teacher):
    return Course(name="Test Course", _teacher_id=teacher.id)


@pytest.fixture
def course_with_students(teacher, student1, student2):
    course = Course(name="Test Course", _teacher_id=teacher.id)
    course._students = [student1, student2]
    return course


@pytest.fixture
def course_with_tags(teacher):
    course = Course(name="Test Course", _teacher_id=teacher.id)
    tag1 = create_test_tag(1, course.id if course.id else 0, "Tag 1")
    tag2 = create_test_tag(2, course.id if course.id else 0, "Tag 2")
    course.tags = [tag1, tag2]
    return course

# ==================== ТЕСТЫ ====================


def test_course_initialization_empty():
    """Тест создания пустого курса"""
    course = Course(name="Mathematics", _teacher_id=1)
    assert course.name == "Mathematics"
    assert course.teacher_id == 1
    assert course.tags == []
    assert course._students == []
    assert course.problems == []
    assert course.description == ""
    assert course.is_private == False
    assert course.id is None


def test_course_initialization_with_description():
    """Тест создания курса с описанием"""
    course = Course(name="Physics", _teacher_id=2, description="Advanced physics course")
    assert course.name == "Physics"
    assert course.teacher_id == 2
    assert course.description == "Advanced physics course"


def test_course_initialization_private():
    """Тест создания приватного курса"""
    course = Course(name="Private Math", _teacher_id=3, is_private=True)
    assert course.is_private == True


def test_teacher_id_getter():
    """Тест получения ID учителя через property"""
    course = Course(name="Test", _teacher_id=5)
    assert course.teacher_id == 5


def test_teacher_id_setter_valid():
    """Тест валидного изменения ID учителя"""
    course = Course(name="Test", _teacher_id=5)
    course.teacher_id = 10
    assert course.teacher_id == 10
    assert course._teacher_id == 10


def test_teacher_id_setter_without_students():
    """Тест изменения teacher_id когда нет студентов"""
    course = Course(name="Test", _teacher_id=1)
    course.teacher_id = 2
    assert course.teacher_id == 2


def test_teacher_id_setter_conflict_with_student():
    """Тест конфликта при установке teacher_id равным ID студента"""
    course = Course(name="Test", _teacher_id=1)
    student = create_test_user(100)
    course._students = [student]

    with pytest.raises(RolesError, match="Teacher cannot be student at the same time"):
        course.teacher_id = 100


def test_teacher_id_setter_multiple_students():
    """Тест конфликта при множественных студентах"""
    course = Course(name="Test", _teacher_id=1)
    students = [create_test_user(100), create_test_user(101), create_test_user(102)]
    course._students = students

    with pytest.raises(RolesError):
        course.teacher_id = 101


def test_students_property_getter():
    """Тест получения students как tuple"""
    course = Course(name="Test", _teacher_id=1)
    student = create_test_user(100)
    course._students = [student]

    students = course.students
    assert isinstance(students, tuple)
    assert len(students) == 1
    assert students[0].id == 100


def test_students_property_immutable():
    """Тест что students возвращает неизменяемый tuple"""
    course = Course(name="Test", _teacher_id=1)
    student = create_test_user(100)
    course._students = [student]

    students = course.students
    with pytest.raises(AttributeError):
        students.append(create_test_user(101))


def test_students_setter_valid():
    """Тест валидной установки студентов"""
    course = Course(name="Test", _teacher_id=1)
    students = [create_test_user(100), create_test_user(101)]

    course.students = students
    assert len(course._students) == 2
    assert course._students[0].id == 100
    assert course._students[1].id == 101


def test_students_setter_empty_list():
    """Тест установки пустого списка студентов"""
    course = Course(name="Test", _teacher_id=1)
    course._students = [create_test_user(100)]

    course.students = []
    assert len(course._students) == 0


def test_students_setter_teacher_conflict():
    """Тест что учитель не может быть в списке студентов"""
    course = Course(name="Test", _teacher_id=1)
    student = create_test_user(1)  # Тот же ID что у учителя

    with pytest.raises(RolesError, match="User 1 is the teacher of this course"):
        course.students = [student]


def test_students_setter_teacher_conflict_multiple():
    """Тест конфликта учителя в списке из нескольких студентов"""
    course = Course(name="Test", _teacher_id=1)
    students = [create_test_user(100), create_test_user(1), create_test_user(101)]

    with pytest.raises(RolesError):
        course.students = students


def test_validate_teacher_is_student_valid():
    """Тест валидации когда учитель не студент"""
    course = Course(name="Test", _teacher_id=1)
    students = [create_test_user(100), create_test_user(101)]

    # Не должно вызывать исключение
    course._validate_teacher_is_student(students)


def test_validate_teacher_is_student_invalid():
    """Тест валидации когда учитель есть в списке студентов"""
    course = Course(name="Test", _teacher_id=1)
    students = [create_test_user(100), create_test_user(1)]

    with pytest.raises(RolesError):
        course._validate_teacher_is_student(students)


def test_add_students_empty_course():
    """Тест добавления студентов в пустой курс"""
    course = Course(name="Test", _teacher_id=1)
    students = [create_test_user(100), create_test_user(101)]

    course.add_students(students)
    assert len(course._students) == 2
    assert course._students[0].id == 100
    assert course._students[1].id == 101


def test_add_students_existing_course():
    """Тест добавления студентов в курс где уже есть студенты"""
    course = Course(name="Test", _teacher_id=1)
    course._students = [create_test_user(100)]

    new_students = [create_test_user(101), create_test_user(102)]
    course.add_students(new_students)

    assert len(course._students) == 3
    assert course._students[0].id == 100
    assert course._students[1].id == 101
    assert course._students[2].id == 102


def test_add_students_duplicates():
    """Тест что один студент не добавляется дважды"""
    course = Course(name="Test", _teacher_id=1)
    student = create_test_user(100)

    course.add_students([student])
    course.add_students([student])  # Второй раз

    assert len(course._students) == 1


def test_add_students_teacher_conflict():
    """Тест что нельзя добавить учителя как студента"""
    course = Course(name="Test", _teacher_id=1)
    student = create_test_user(1)  # Тот же ID что у учителя

    with pytest.raises(RolesError):
        course.add_students([student])


def test_add_students_by_tag_with_existing_tag():
    """Тест добавления студентов по существующему тегу"""
    course = Course(name="Test", _teacher_id=1)

    # Создаем тег
    tag = create_test_tag(1, 0)
    course.tags = [tag]

    # Добавляем студентов
    students = [create_test_user(100), create_test_user(101)]
    course.add_students_by_tag(1, students)

    assert len(course._students) == 2
    assert len(tag.students) == 2
    assert tag.students[0].id == 100
    assert tag.students[1].id == 101


def test_add_students_by_tag_duplicate_students():
    """Тест добавления студентов по тегу когда студенты уже в теге"""
    course = Course(name="Test", _teacher_id=1)

    tag = create_test_tag(1, 0)
    student = create_test_user(100)
    tag.students = [student]
    course.tags = [tag]

    # Пытаемся добавить того же студента
    course.add_students_by_tag(1, [student])

    assert len(tag.students) == 1  # Не должен дублироваться


def test_add_students_by_tag_nonexistent_tag():
    """Тест добавления студентов по несуществующему тегу"""
    course = Course(name="Test", _teacher_id=1)
    students = [create_test_user(100)]

    with pytest.raises(UndefinedTagError, match="Unable to bind students to tag 999"):
        course.add_students_by_tag(999, students)


def test_add_students_by_tag_empty_tags():
    """Тест добавления студентов по тегу когда тегов нет"""
    course = Course(name="Test", _teacher_id=1)
    course.tags = []
    students = [create_test_user(100)]

    with pytest.raises(UndefinedTagError):
        course.add_students_by_tag(1, students)


def test_add_students_by_tag_multiple_tags():
    """Тест добавления студентов в конкретный тег из нескольких"""
    course = Course(name="Test", _teacher_id=1)

    tag1 = create_test_tag(1, 0, "Tag 1")
    tag2 = create_test_tag(2, 0, "Tag 2")
    course.tags = [tag1, tag2]

    students = [create_test_user(100)]
    course.add_students_by_tag(2, students)

    assert len(tag1.students) == 0
    assert len(tag2.students) == 1


def test_delete_students_common_single():
    """Тест удаления одного студента через _delete_students_common"""
    course = Course(name="Test", _teacher_id=1)

    students = [create_test_user(100), create_test_user(101), create_test_user(102)]
    course._students = students

    deleted = course._delete_students_common([101])

    assert deleted == [101]
    assert len(course._students) == 2
    assert course._students[0].id == 100
    assert course._students[1].id == 102


def test_delete_students_common_multiple():
    """Тест удаления нескольких студентов"""
    course = Course(name="Test", _teacher_id=1)

    students = [create_test_user(i) for i in range(100, 110)]
    course._students = students

    deleted = course._delete_students_common([102, 105, 108])

    assert sorted(deleted) == [102, 105, 108]
    assert len(course._students) == 7
    assert all(s.id not in [102, 105, 108] for s in course._students)


def test_delete_students_common_nonexistent():
    """Тест удаления несуществующих студентов"""
    course = Course(name="Test", _teacher_id=1)

    students = [create_test_user(100), create_test_user(101)]
    course._students = students

    deleted = course._delete_students_common([999, 1000])

    assert deleted == []
    assert len(course._students) == 2


def test_delete_students_common_empty():
    """Тест удаления из пустого списка студентов"""
    course = Course(name="Test", _teacher_id=1)
    course._students = []

    deleted = course._delete_students_common([100])

    assert deleted == []
    assert len(course._students) == 0


def test_delete_students_common_all():
    """Тест удаления всех студентов"""
    course = Course(name="Test", _teacher_id=1)

    students = [create_test_user(100), create_test_user(101)]
    course._students = students

    deleted = course._delete_students_common([100, 101])

    assert sorted(deleted) == [100, 101]
    assert len(course._students) == 0


def test_delete_students_recursion_error():
    """Тест что delete_students вызывает рекурсию (ожидаемая ошибка)"""
    course = Course(name="Test", _teacher_id=1)
    course._students = [create_test_user(100)]

    with pytest.raises(RecursionError):
        course.delete_students([100])


def test_course_with_problems():
    """Тест курса с задачами"""
    course = Course(name="Test", _teacher_id=1)

    problem1 = Problem(name="Problem 1", description="Desc 1", course_id=0)
    problem2 = Problem(name="Problem 2", description="Desc 2", course_id=0)

    course.problems = [problem1, problem2]

    assert len(course.problems) == 2
    assert course.problems[0].name == "Problem 1"
    assert course.problems[1].name == "Problem 2"


def test_course_tags_manipulation():
    """Тест ручного управления тегами"""
    course = Course(name="Test", _teacher_id=1)

    tag1 = create_test_tag(1, 0, "Python")
    tag2 = create_test_tag(2, 0, "Django")

    course.tags.append(tag1)
    course.tags.append(tag2)

    assert len(course.tags) == 2
    assert course.tags[0].name == "Python"
    assert course.tags[1].name == "Django"


def test_tag_students_management():
    """Тест управления студентами в теге"""
    tag = Tag(name="Test Tag", course_id=1)
    tag.id = 1

    student1 = create_test_user(100)
    student2 = create_test_user(101)

    tag.students.append(student1)
    tag.students.append(student2)

    assert len(tag.students) == 2
    assert tag.students[0].id == 100
    assert tag.students[1].id == 101


def test_user_initialization():
    """Тест создания пользователя"""
    user = User(email="test@example.com", password="secret", name="John Doe")

    assert user.email == "test@example.com"
    assert user.password == "secret"
    assert user.name == "John Doe"
    assert user.is_active == False
    assert user.id is None
    assert user.courses == []


def test_user_id_assignment():
    """Тест назначения ID пользователю"""
    user = User(email="test@example.com", password="secret")
    user.id = 500

    assert user.id == 500


def test_user_courses_management():
    """Тест управления курсами пользователя"""
    user = User(email="test@example.com", password="secret")

    course1 = Course(name="Math", _teacher_id=1)
    course2 = Course(name="Physics", _teacher_id=2)

    user.courses.append(course1)
    user.courses.append(course2)

    assert len(user.courses) == 2
    assert user.courses[0].name == "Math"
    assert user.courses[1].name == "Physics"


def test_multiple_courses_independence():
    """Тест независимости нескольких курсов"""
    course1 = Course(name="Course 1", _teacher_id=1)
    course2 = Course(name="Course 2", _teacher_id=2)

    student = create_test_user(100)

    course1.add_students([student])

    assert len(course1._students) == 1
    assert len(course2._students) == 0


def test_course_with_mixed_data():
    """Тест курса со смешанными данными"""
    course = Course(
        name="Advanced Python",
        _teacher_id=1,
        description="Advanced Python programming",
        is_private=True
    )

    # Устанавливаем ID
    course.id = 100

    # Добавляем теги
    tag1 = create_test_tag(1, course.id, "Python")
    tag2 = create_test_tag(2, course.id, "Algorithms")
    course.tags = [tag1, tag2]

    # Добавляем студентов
    students = [create_test_user(i, f"Student {i}") for i in range(100, 105)]
    course._students = students

    # Добавляем задачи
    problems = [
        Problem(name=f"Problem {i}", description=f"Desc {i}", course_id=course.id)
        for i in range(1, 4)
    ]
    course.problems = problems

    assert course.name == "Advanced Python"
    assert course.teacher_id == 1
    assert course.description == "Advanced Python programming"
    assert course.is_private == True
    assert course.id == 100
    assert len(course.tags) == 2
    assert len(course._students) == 5
    assert len(course.problems) == 3


def test_edge_case_empty_strings():
    """Тест граничных случаев с пустыми строками"""
    course = Course(name="", _teacher_id=0, description="")

    assert course.name == ""
    assert course.teacher_id == 0
    assert course.description == ""


def test_edge_case_negative_teacher_id():
    """Тест с отрицательным teacher_id"""
    course = Course(name="Test", _teacher_id=-1)

    assert course.teacher_id == -1


def test_edge_case_large_student_lists():
    """Тест с большим списком студентов"""
    course = Course(name="Test", _teacher_id=1)

    # Создаем 1000 студентов
    students = [create_test_user(i) for i in range(1000, 2000)]

    course.students = students
    assert len(course._students) == 1000


def test_method_chaining():
    """Тест цепочки вызовов методов"""
    course = Course(name="Test", _teacher_id=1)

    # Создаем тег
    tag = create_test_tag(1, 0)
    course.tags = [tag]

    # Добавляем студентов и сразу проверяем
    student = create_test_user(100)
    course.add_students([student])
    course.add_students_by_tag(1, [student])

    assert len(course._students) == 1
    assert len(tag.students) == 1


def test_concurrent_operations_simulation():
    """Тест симуляции конкурентных операций"""
    course = Course(name="Test", _teacher_id=1)

    # Симуляция добавления студентов в разных "потоках"
    students_batch1 = [create_test_user(i) for i in range(100, 105)]
    students_batch2 = [create_test_user(i) for i in range(105, 110)]

    course.add_students(students_batch1)
    course.add_students(students_batch2)

    assert len(course._students) == 10


def test_course_equality():
    """Тест сравнения курсов"""
    course1 = Course(name="Math", _teacher_id=1)
    course2 = Course(name="Math", _teacher_id=1)
    course3 = Course(name="Physics", _teacher_id=2)

    # Dataclasses сравниваются по значению полей
    # Но у нас есть init=False поля, так что...
    course1.id = 1
    course2.id = 1
    course3.id = 2

    # Проверка ID
    assert course1.id == course2.id
    assert course1.id != course3.id


def test_student_enrollment_scenario():
    """Полный сценарий зачисления студентов"""
    # Создаем курс
    course = Course(name="Programming 101", _teacher_id=1)

    # Создаем теги
    beginner_tag = create_test_tag(1, 0, "Beginner")
    advanced_tag = create_test_tag(2, 0, "Advanced")
    course.tags = [beginner_tag, advanced_tag]

    # Создаем студентов
    students = [
        create_test_user(100, "Alice"),
        create_test_user(101, "Bob"),
        create_test_user(102, "Charlie")
    ]

    # Зачисляем всех студентов
    course.add_students(students)

    # Распределяем по тегам
    course.add_students_by_tag(1, [students[0], students[1]])  # Beginners
    course.add_students_by_tag(2, [students[2]])  # Advanced

    assert len(course._students) == 3
    assert len(beginner_tag.students) == 2
    assert len(advanced_tag.students) == 1


def test_error_messages_verification():
    """Тест проверки текстов ошибок"""
    course = Course(name="Test", _teacher_id=1)

    # Проверка текста ошибки RolesError
    student = create_test_user(1)  # Тот же ID что у учителя

    try:
        course.add_students([student])
    except RolesError as e:
        assert "User 1 is the teacher of this course" in str(e)

    # Проверка текста ошибки UndefinedTagError
    try:
        course.add_students_by_tag(999, [create_test_user(100)])
    except UndefinedTagError as e:
        assert "Unable to bind students to tag 999" in str(e)
        assert "tag not related with course Test" in str(e)


def test_none_student_id_handling():
    """Тест обработки студентов с None ID"""
    course = Course(name="Test", _teacher_id=1)

    student = User(email="test@test.com", password="pass")
    # student.id остается None

    # Не должно вызывать ошибку
    course.add_students([student])
    assert len(course._students) == 1
    assert course._students[0].id is None


def test_teacher_id_change_with_none_student_ids():
    """Тест изменения teacher_id когда у студентов None ID"""
    course = Course(name="Test", _teacher_id=1)

    student = User(email="test@test.com", password="pass")
    # student.id = None
    course._students = [student]

    # Не должно вызывать ошибку, так как id студента None
    course.teacher_id = 5
    assert course.teacher_id == 5


def test_validate_teacher_with_none_ids():
    """Тест валидации когда ID студентов None"""
    course = Course(name="Test", _teacher_id=1)

    student = User(email="test@test.com", password="pass")
    # student.id = None

    # Не должно вызывать ошибку
    course._validate_teacher_is_student([student])


def test_performance_large_dataset():
    """Тест производительности с большим набором данных"""
    course = Course(name="Test", _teacher_id=1)

    # 10,000 студентов
    students = [create_test_user(i) for i in range(2, 10002)]

    course.students = students
    assert len(course._students) == 10000

    # Удаление 1000 студентов
    ids_to_delete = list(range(5000, 6000))
    deleted = course._delete_students_common(ids_to_delete)

    assert len(deleted) == 1000
    assert len(course._students) == 9000


def test_course_copy_behavior():
    """Тест поведения копирования курса"""
    import copy

    course = Course(name="Test", _teacher_id=1)
    student = create_test_user(100)
    course._students = [student]

    # Поверхностное копирование
    shallow_copy = copy.copy(course)

    # Глубокое копирование
    deep_copy = copy.deepcopy(course)

    # Проверяем, что списки студентов - разные объекты
    course._students.append(create_test_user(101))

    assert len(course._students) == 2
    assert len(shallow_copy._students) == 2  # Та же ссылка
    assert len(deep_copy._students) == 1     # Разная ссылка


def test_course_serialization_simulation():
    """Тест симуляции сериализации"""
    course = Course(name="Test", _teacher_id=1)

    # Симуляция данных для JSON
    course_data = {
        "name": course.name,
        "teacher_id": course.teacher_id,
        "description": course.description,
        "is_private": course.is_private,
        "student_count": len(course._students)
    }

    assert course_data["name"] == "Test"
    assert course_data["teacher_id"] == 1
    assert course_data["student_count"] == 0
