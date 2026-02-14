import pytest

from src.domain.entities import Course, User, Tag, DefautTagType
from src.domain.entities.exceptions import (
    RolesError,
    UndefinedTagError,
    ImpossibleOperationError
)
from src.domain.services import CourseStudentsManagerService


@pytest.fixture
def teacher():
    """Фикстура для создания учителя"""
    user = User(email="teacher@test.com", password="pass123", name="Teacher")
    user.id = 1
    user.is_active = True
    return user


@pytest.fixture
def student1():
    """Фикстура для создания первого студента"""
    user = User(email="student1@test.com", password="pass123", name="Student 1")
    user.id = 2
    user.is_active = True
    return user


@pytest.fixture
def student2():
    """Фикстура для создания второго студента"""
    user = User(email="student2@test.com", password="pass123", name="Student 2")
    user.id = 3
    user.is_active = True
    return user


@pytest.fixture
def student3():
    """Фикстура для создания третьего студента"""
    user = User(email="student3@test.com", password="pass123", name="Student 3")
    user.id = 4
    user.is_active = True
    return user


@pytest.fixture
def course(teacher):
    """Фикстура для создания курса"""
    course = Course(
        name="Test Course",
        _teacher_id=teacher.id,
        description="Test Description"
    )
    course.id = 100

    # Добавляем теги по умолчанию
    waiting_tag = Tag(name=DefautTagType.WAITING_FOR_SUBSCRIBE.value, course_id=course.id)
    waiting_tag.id = 1
    custom_tag = Tag(name="Python Developers", course_id=course.id)
    custom_tag.id = 2
    another_tag = Tag(name="Beginners", course_id=course.id)
    another_tag.id = 3

    course._tags = [waiting_tag, custom_tag, another_tag]

    return course


@pytest.fixture
def service(course):
    """Фикстура для создания сервиса"""
    return CourseStudentsManagerService(course)


def test_add_students_success(service, course, student1, student2):
    """Тест успешного добавления студентов в курс"""
    # Act
    service.add_students([student1, student2])

    # Assert
    assert len(course.students) == 2
    assert student1 in course.students
    assert student2 in course.students

    # Проверяем, что студенты не добавляются повторно
    service.add_students([student1])
    assert len(course.students) == 2


def test_add_students_removes_from_waiting_tag(service, course, student1, student2):
    """Тест удаления студентов из тега ожидания при добавлении в курс"""
    # Arrange
    waiting_tag = course.get_tag(DefautTagType.WAITING_FOR_SUBSCRIBE.value)
    waiting_tag.students = [student1, student2]

    # Act
    service.add_students([student1])

    # Assert
    assert student1 not in waiting_tag.students
    assert student2 in waiting_tag.students  # Должен остаться, т.к. не добавляли


def test_add_students_teacher_as_student_error(service, teacher, student1):
    """Тест ошибки при попытке добавить учителя как студента"""
    # Act & Assert
    with pytest.raises(RolesError) as exc_info:
        service.add_students([teacher, student1])

    assert "User is the teacher of this course" in str(exc_info.value)
    assert len(service._course.students) == 0  # Никто не должен добавиться


def test_add_students_by_tag_success(service, course, student1, student2):
    """Тест успешного добавления студентов в курс и тег"""
    # Act
    service.add_students_by_tag("Python Developers", [student1, student2])

    # Assert
    assert len(course.students) == 2
    assert student1 in course.students
    assert student2 in course.students

    # Проверяем добавление в тег
    tag = course.get_tag("Python Developers")
    assert len(tag.students) == 2
    assert student1 in tag.students
    assert student2 in tag.students


def test_add_students_by_tag_existing_students(service, course, student1, student2):
    """Тест добавления уже существующих студентов в новый тег"""
    # Arrange
    service.add_students([student1])
    tag = course.get_tag("Python Developers")

    # Act
    service.add_students_by_tag("Python Developers", [student1, student2])

    # Assert
    assert len(course.students) == 2  # student2 должен добавиться
    assert len(tag.students) == 2
    assert student1 in tag.students  # Не должен дублироваться
    assert student2 in tag.students


def test_add_students_by_tag_default_tag_error(service):
    """Тест ошибки при попытке добавить студентов в тег по умолчанию"""
    # Act & Assert
    with pytest.raises(ImpossibleOperationError) as exc_info:
        service.add_students_by_tag(DefautTagType.WAITING_FOR_SUBSCRIBE.value, [])

    assert "Unable to add student to default tag" in str(exc_info.value)


def test_add_students_by_tag_undefined_tag_error(service):
    """Тест ошибки при попытке добавить студентов в несуществующий тег"""
    # Act & Assert
    with pytest.raises(UndefinedTagError) as exc_info:
        service.add_students_by_tag("NonExistentTag", [])

    assert "tag not related with course" in str(exc_info.value)


def test_add_students_by_tag_teacher_error(service, teacher):
    """Тест ошибки при добавлении учителя через тег"""
    # Act & Assert
    with pytest.raises(RolesError) as exc_info:
        service.add_students_by_tag("Python Developers", [teacher])

    assert "User is the teacher of this course" in str(exc_info.value)


def test_request_subscribe_success(service, course, student1, student2):
    """Тест успешной заявки на подписку"""
    # Act
    service.request_subscribe([student1, student2])

    # Assert
    waiting_tag = course.get_tag(DefautTagType.WAITING_FOR_SUBSCRIBE.value)
    assert len(waiting_tag.students) == 2
    assert student1 in waiting_tag.students
    assert student2 in waiting_tag.students
    assert len(course.students) == 0  # Студенты еще не добавлены в курс


def test_request_subscribe_no_duplicates(service, course, student1):
    """Тест отсутствия дубликатов при повторной заявке"""
    # Arrange
    waiting_tag = course.get_tag(DefautTagType.WAITING_FOR_SUBSCRIBE.value)

    # Act
    service.request_subscribe([student1])
    service.request_subscribe([student1])

    # Assert
    assert len(waiting_tag.students) == 1


def test_request_subscribe_teacher_error(service, teacher):
    """Тест ошибки при заявке учителя на подписку"""
    # Act & Assert
    with pytest.raises(RolesError) as exc_info:
        service.request_subscribe([teacher])

    assert "User is the teacher of this course" in str(exc_info.value)


def test_delete_students_success(service, course, student1, student2, student3):
    """Тест успешного удаления студентов из курса и всех тегов"""
    # Arrange
    # Добавляем студентов в курс
    service.add_students([student1, student2, student3])

    # Добавляем студентов в разные теги
    python_tag = course.get_tag("Python Developers")
    beginners_tag = course.get_tag("Beginners")
    python_tag.students = [student1, student2]
    beginners_tag.students = [student2, student3]

    # Act
    service.delete_students([student1.id, student2.id])

    # Assert
    assert len(course.students) == 1
    assert course.students[0].id == student3.id

    # Проверяем теги
    assert len(python_tag.students) == 0
    assert len(beginners_tag.students) == 1
    assert beginners_tag.students[0].id == student3.id


def test_delete_students_no_ids(service, course, student1):
    """Тест удаления с пустым списком ID"""
    # Arrange
    service.add_students([student1])

    # Act
    service.delete_students([])

    # Assert
    assert len(course.students) == 1


def test_delete_students_non_existent_ids(service, course, student1):
    """Тест удаления несуществующих ID"""
    # Arrange
    service.add_students([student1])

    # Act
    service.delete_students([999, 1000])

    # Assert
    assert len(course.students) == 1
    assert student1 in course.students


def test_integration_full_flow(service, course, student1, student2, student3):
    """Интеграционный тест полного цикла работы со студентами"""

    # 1. Студенты подают заявки
    service.request_subscribe([student1, student2, student3])
    waiting_tag = course.get_tag(DefautTagType.WAITING_FOR_SUBSCRIBE.value)
    assert len(waiting_tag.students) == 3

    # 2. Добавляем двух студентов в курс и в тег Python
    service.add_students_by_tag("Python Developers", [student1, student2])
    assert len(course.students) == 2
    assert student1 in course.students
    assert student2 in course.students
    assert student3 not in course.students

    # Проверяем удаление из waiting_tag
    assert student1 not in waiting_tag.students
    assert student2 not in waiting_tag.students
    assert student3 in waiting_tag.students

    # 3. Добавляем третьего студента в другой тег
    service.add_students_by_tag("Beginners", [student3])
    assert len(course.students) == 3
    assert student3 in course.students
    assert student3 not in waiting_tag.students  # Должен удалиться из waiting

    # 4. Удаляем одного студента
    service.delete_students([student2.id])
    assert len(course.students) == 2
    assert student2 not in course.students

    # Проверяем теги
    python_tag = course.get_tag("Python Developers")
    beginners_tag = course.get_tag("Beginners")
    assert student1 in python_tag.students
    assert student2 not in python_tag.students
    assert student3 in beginners_tag.students


def test_edge_case_empty_students_list(service, course):
    """Тест граничного случая с пустым списком студентов"""

    # Не должно вызывать ошибок
    service.add_students([])
    service.add_students_by_tag("Python Developers", [])
    service.request_subscribe([])

    assert len(course.students) == 0

    waiting_tag = course.get_tag(DefautTagType.WAITING_FOR_SUBSCRIBE.value)
    assert len(waiting_tag.students) == 0


def test_multiple_operations_with_same_student(service, course, student1):
    """Тест множественных операций с одним студентом"""

    # 1. Заявка
    service.request_subscribe([student1])
    waiting_tag = course.get_tag(DefautTagType.WAITING_FOR_SUBSCRIBE.value)
    assert student1 in waiting_tag.students

    # 2. Добавление в курс
    service.add_students([student1])
    assert student1 in course.students
    assert student1 not in waiting_tag.students

    # 3. Добавление в тег
    service.add_students_by_tag("Python Developers", [student1])
    python_tag = course.get_tag("Python Developers")
    assert student1 in python_tag.students

    # 4. Попытка повторного добавления в waiting (не должно работать)
    with pytest.raises(ImpossibleOperationError):
        service.request_subscribe([student1])
    assert student1 not in waiting_tag.students

    # 5. Удаление
    service.delete_students([student1.id])
    assert student1 not in course.students
    assert student1 not in python_tag.students
    assert student1 not in waiting_tag.students
