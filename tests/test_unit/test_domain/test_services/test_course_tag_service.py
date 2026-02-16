import pytest
from enum import Enum
from dataclasses import field
from src.domain.entities import Course, Tag, User
from src.domain.entities.exceptions import (
    NamesAlreadyExistError,
    ImpossibleOperationError,
    AttributeRequired,
    HasNoDirectAccessError,
    RepeatableNamesError
)
from src.domain.services.course import CourseTagManagerService


class DefautTagType(Enum):
    WAITING_FOR_SUBSCRIBE = "Ожидают зачисления"

    @classmethod
    def names(cls):
        return [type_.value for type_ in cls]


@pytest.fixture
def course():
    """Базовый курс с дефолтным тегом."""
    course = Course(name="Test Course", _teacher_id=42)
    course.id = 1

    # Создаем только один дефолтный тег
    waiting_tag = Tag(name=DefautTagType.WAITING_FOR_SUBSCRIBE.value, course_id=course.id)
    waiting_tag.id = 1

    course._tags = [waiting_tag]

    return course


@pytest.fixture
def manager(course):
    """Менеджер с курсом."""
    return CourseTagManagerService(course)


@pytest.fixture
def custom_tag1():
    """Пользовательский тег 1."""
    tag = Tag(name="Advanced", course_id=1)
    tag.id = 3
    tag.students = []
    return tag


@pytest.fixture
def custom_tag2():
    """Пользовательский тег 2."""
    tag = Tag(name="Beginners", course_id=1)
    tag.id = 4
    tag.students = []
    return tag


@pytest.fixture
def custom_tag3():
    """Пользовательский тег 3."""
    tag = Tag(name="Extra", course_id=1)
    tag.id = 5
    tag.students = []
    return tag


@pytest.fixture
def student():
    """Студент для тестов."""
    user = User(email="student@example.com", password="pass", name="Student")
    user.id = 100
    return user


# ===================== ТЕСТЫ __post_init__ =====================

def test_tag_creation_with_name():
    """Тег должен создаваться с именем."""
    tag = Tag(name="Valid Tag", course_id=1)
    assert tag.name == "Valid Tag"
    assert tag.course_id == 1
    assert tag.students == []


def test_tag_creation_without_name():
    """Тег без имени должен кидать ошибку."""
    with pytest.raises(AttributeRequired, match="Tag must has name"):
        Tag(name=None, course_id=1)  # type: ignore


# ===================== ТЕСТЫ _validate_repeatable_names =====================

def test_validate_repeatable_names_unique_tags(manager, custom_tag1, custom_tag2):
    """Уникальные имена тегов проходят валидацию."""
    manager._validate_repeatable_names([custom_tag1, custom_tag2])


def test_validate_repeatable_names_duplicate_tags(manager, custom_tag1):
    """Дубликаты имен тегов вызывают ошибку."""
    tag_duplicate = Tag(name="Advanced", course_id=1)
    tag_duplicate.id = 10

    with pytest.raises(RepeatableNamesError) as exc_info:
        manager._validate_repeatable_names([custom_tag1, tag_duplicate])

    assert "Names of tag cannot match" in str(exc_info.value)


def test_validate_repeatable_names_empty_list(manager):
    """Пустой список тегов проходит валидацию."""
    manager._validate_repeatable_names([])


def test_validate_repeatable_names_single_tag(manager, custom_tag1):
    """Один тег всегда проходит."""
    manager._validate_repeatable_names([custom_tag1])


# ===================== ТЕСТЫ _validate_already_exists =====================

def test_validate_already_exists_no_conflicts(manager, custom_tag1):
    """Новые теги не конфликтуют с существующими."""
    manager._validate_already_exists(manager._course.tags, [custom_tag1])


def test_validate_already_exists_with_conflict(manager, custom_tag1):
    """Конфликт с существующим тегом."""
    # Сначала добавляем тег
    manager._course._tags.append(custom_tag1)

    # Пытаемся добавить такой же
    new_tag = Tag(name="Advanced", course_id=1)
    new_tag.id = 10

    with pytest.raises(NamesAlreadyExistError) as exc_info:
        manager._validate_already_exists(manager._course.tags, [new_tag])

    assert "already exists in course" in str(exc_info.value)


def test_validate_already_exists_with_default_tag(manager):
    """Конфликт с дефолтным тегом."""
    default_tag_name = DefautTagType.WAITING_FOR_SUBSCRIBE.value
    new_tag = Tag(name=default_tag_name, course_id=1)
    new_tag.id = 10

    with pytest.raises(NamesAlreadyExistError):
        manager._validate_already_exists(manager._course.tags, [new_tag])


def test_validate_already_exists_multiple_conflicts(manager, custom_tag1, custom_tag2):
    """Множественные конфликты."""
    manager._course._tags.append(custom_tag1)
    manager._course._tags.append(custom_tag2)

    conflict1 = Tag(name="Advanced", course_id=1)  # конфликт с custom_tag1
    conflict2 = Tag(name="Beginners", course_id=1)  # конфликт с custom_tag2
    conflict1.id = 10
    conflict2.id = 11

    with pytest.raises(NamesAlreadyExistError):
        manager._validate_already_exists(manager._course.tags, [conflict1, conflict2])


def test_validate_already_exists_empty_incoming(manager):
    """Пустой список новых тегов."""
    manager._validate_already_exists(manager._course.tags, [])


def test_validate_already_exists_empty_current(manager, custom_tag1):
    """Текущий список пуст."""
    manager._course._tags = []  # очищаем теги
    manager._validate_already_exists([], [custom_tag1])  # не должно быть ошибки


# ===================== ТЕСТЫ _validate_incoming_tags =====================

def test_validate_incoming_tags_valid(manager, custom_tag1, custom_tag2):
    """Валидация корректных тегов."""
    manager._validate_incoming_tags([custom_tag1, custom_tag2])


def test_validate_incoming_tags_with_duplicates(manager, custom_tag1):
    """Валидация с дубликатами в добавляемых тегах."""
    tag_duplicate = Tag(name="Advanced", course_id=1)
    tag_duplicate.id = 10

    with pytest.raises(RepeatableNamesError):
        manager._validate_incoming_tags([custom_tag1, tag_duplicate])


def test_validate_incoming_tags_conflict_with_existing(manager, custom_tag1):
    """Валидация с конфликтом с существующими тегами."""
    manager._course._tags.append(custom_tag1)

    new_tag = Tag(name="Advanced", course_id=1)
    new_tag.id = 10

    with pytest.raises(NamesAlreadyExistError):
        manager._validate_incoming_tags([new_tag])


def test_validate_incoming_tags_conflict_with_default(manager):
    """Валидация с конфликтом с дефолтным тегом."""
    new_tag = Tag(name=DefautTagType.WAITING_FOR_SUBSCRIBE.value, course_id=1)
    new_tag.id = 10

    with pytest.raises(NamesAlreadyExistError):
        manager._validate_incoming_tags([new_tag])


def test_validate_incoming_tags_empty_list(manager):
    """Валидация пустого списка."""
    manager._validate_incoming_tags([])


# ===================== ТЕСТЫ add_tags =====================

def test_add_tags_to_course(manager, custom_tag1, custom_tag2):
    """Добавление тегов в курс."""
    initial_count = len(manager._course.tags)

    manager.add_tags([custom_tag1, custom_tag2])

    assert len(manager._course.tags) == initial_count + 2
    assert custom_tag1 in manager._course.tags
    assert custom_tag2 in manager._course.tags


def test_add_single_tag(manager, custom_tag1):
    """Добавление одного тега."""
    initial_count = len(manager._course.tags)

    manager.add_tags([custom_tag1])

    assert len(manager._course.tags) == initial_count + 1
    assert custom_tag1 in manager._course.tags


def test_add_tags_with_duplicate_names_in_input(manager, custom_tag1):
    """Добавление тегов с дублирующимися именами в одном списке."""
    tag_duplicate = Tag(name="Advanced", course_id=1)
    tag_duplicate.id = 10

    with pytest.raises(RepeatableNamesError):
        manager.add_tags([custom_tag1, tag_duplicate])

    assert custom_tag1 not in manager._course.tags  # ничего не добавилось


def test_add_tags_conflict_with_existing(manager, custom_tag1):
    """Добавление тега с именем, которое уже существует."""
    manager.add_tags([custom_tag1])  # добавляем первый раз

    same_name_tag = Tag(name="Advanced", course_id=1)
    same_name_tag.id = 10

    with pytest.raises(NamesAlreadyExistError):
        manager.add_tags([same_name_tag])

    assert len(manager._course.tags) == 2  # 1 дефолтный + 1 custom


def test_add_tags_conflict_with_default(manager):
    """Добавление тега с именем дефолтного тега."""
    default_name = DefautTagType.WAITING_FOR_SUBSCRIBE.value
    new_tag = Tag(name=default_name, course_id=1)
    new_tag.id = 10

    with pytest.raises(NamesAlreadyExistError):
        manager.add_tags([new_tag])

    assert len(manager._course.tags) == 1  # только дефолтный


def test_add_tags_empty_list(manager):
    """Добавление пустого списка тегов."""
    initial_count = len(manager._course.tags)

    manager.add_tags([])

    assert len(manager._course.tags) == initial_count


def test_add_tags_preserves_default_tag(manager, custom_tag1):
    """Добавление не должно влиять на дефолтный тег."""
    default_tag_before = manager._course.get_tag(DefautTagType.WAITING_FOR_SUBSCRIBE.value)

    manager.add_tags([custom_tag1])

    default_tag_after = manager._course.get_tag(DefautTagType.WAITING_FOR_SUBSCRIBE.value)
    assert default_tag_before == default_tag_after
    assert default_tag_after in manager._course.tags


# ===================== ТЕСТЫ delete_tags =====================

def test_delete_custom_tag(manager, custom_tag1):
    """Удаление пользовательского тега."""
    manager.add_tags([custom_tag1])
    assert custom_tag1 in manager._course.tags

    manager.delete_tags([custom_tag1.id])

    assert custom_tag1 not in manager._course.tags


def test_delete_multiple_custom_tags(manager, custom_tag1, custom_tag2, custom_tag3):
    """Удаление нескольких пользовательских тегов."""
    manager.add_tags([custom_tag1, custom_tag2, custom_tag3])
    assert len(manager._course.tags) == 4  # 1 дефолтный + 3 новых

    manager.delete_tags([custom_tag1.id, custom_tag3.id])

    assert len(manager._course.tags) == 2  # 1 дефолтный + 1 оставшийся
    assert custom_tag1 not in manager._course.tags
    assert custom_tag2 in manager._course.tags
    assert custom_tag3 not in manager._course.tags


def test_delete_default_tag_error(manager):
    """Попытка удалить дефолтный тег вызывает ошибку."""
    default_tag = manager._course.get_tag(DefautTagType.WAITING_FOR_SUBSCRIBE.value)

    with pytest.raises(ImpossibleOperationError) as exc_info:
        manager.delete_tags([default_tag.id])

    assert "Unable to delete default tag" in str(exc_info.value)


def test_delete_multiple_tags_with_default(manager, custom_tag1):
    """Попытка удалить смесь дефолтного и пользовательского тегов."""
    manager.add_tags([custom_tag1])

    default_tag = manager._course.get_tag(DefautTagType.WAITING_FOR_SUBSCRIBE.value)

    with pytest.raises(ImpossibleOperationError):
        manager.delete_tags([default_tag.id, custom_tag1.id])

    # Ничего не должно удалиться
    assert default_tag in manager._course.tags
    assert custom_tag1 in manager._course.tags


def test_delete_nonexistent_tag(manager, custom_tag1):
    """Удаление несуществующего тега."""
    manager.add_tags([custom_tag1])
    initial_count = len(manager._course.tags)

    manager.delete_tags([999, 888])

    assert len(manager._course.tags) == initial_count
    assert custom_tag1 in manager._course.tags


def test_delete_mixed_existing_and_nonexistent(manager, custom_tag1):
    """Удаление смеси существующих и несуществующих ID."""
    manager.add_tags([custom_tag1])
    initial_count = len(manager._course.tags)

    manager.delete_tags([custom_tag1.id, 999, 888])

    assert len(manager._course.tags) == initial_count - 1
    assert custom_tag1 not in manager._course.tags


def test_delete_empty_list(manager, custom_tag1):
    """Удаление с пустым списком ID."""
    manager.add_tags([custom_tag1])
    initial_count = len(manager._course.tags)

    manager.delete_tags([])

    assert len(manager._course.tags) == initial_count


def test_delete_all_custom_tags(manager, custom_tag1, custom_tag2):
    """Удаление всех пользовательских тегов."""
    manager.add_tags([custom_tag1, custom_tag2])
    custom_ids = [custom_tag1.id, custom_tag2.id]

    manager.delete_tags(custom_ids)

    # Должен остаться только дефолтный
    assert len(manager._course.tags) == 1
    assert manager._course.tags[0].name == DefautTagType.WAITING_FOR_SUBSCRIBE.value


# ===================== ТЕСТЫ ГРАНИЧНЫХ СЛУЧАЕВ =====================

def test_add_tags_with_special_characters(manager):
    """Добавление тегов со спецсимволами в имени."""
    special_tags = [
        Tag(name="Tag-1", course_id=1),
        Tag(name="Tag_2", course_id=1),
        Tag(name="Tag 3", course_id=1),
        Tag(name="Tag.4", course_id=1)
    ]
    for i, tag in enumerate(special_tags):
        tag.id = i + 10

    manager.add_tags(special_tags)

    assert len(manager._course.tags) == 5  # 1 дефолтный + 4 новых


def test_add_tags_maximum_length_name(manager):
    """Добавление тега с очень длинным именем."""
    long_name = "A" * 255
    long_tag = Tag(name=long_name, course_id=1)
    long_tag.id = 10

    manager.add_tags([long_tag])

    assert long_tag in manager._course.tags


def test_add_tags_unicode_names(manager):
    """Добавление тегов с юникодными именами."""
    unicode_tags = [
        Tag(name="Тег", course_id=1),
        Tag(name="タグ", course_id=1),
        Tag(name="标签", course_id=1)
    ]
    for i, tag in enumerate(unicode_tags):
        tag.id = i + 10

    manager.add_tags(unicode_tags)

    assert len(manager._course.tags) == 4  # 1 дефолтный + 3 новых


def test_add_tags_after_delete(manager, custom_tag1):
    """Добавление тега после удаления."""
    manager.add_tags([custom_tag1])
    assert custom_tag1 in manager._course.tags

    manager.delete_tags([custom_tag1.id])
    assert custom_tag1 not in manager._course.tags

    # Добавляем тег с таким же именем (должно работать, т.к. удалили)
    same_name_tag = Tag(name="Advanced", course_id=1)
    same_name_tag.id = 20

    manager.add_tags([same_name_tag])
    assert same_name_tag in manager._course.tags


def test_add_duplicate_after_delete_different_id(manager, custom_tag1):
    """Добавление тега с тем же именем после удаления (другой ID)."""
    manager.add_tags([custom_tag1])
    manager.delete_tags([custom_tag1.id])

    new_tag = Tag(name="Advanced", course_id=1)
    new_tag.id = 20

    manager.add_tags([new_tag])
    assert new_tag in manager._course.tags
    assert len(manager._course.tags) == 2  # дефолтный + новый


# ===================== ТЕСТЫ НА ВЗАИМОДЕЙСТВИЕ С КУРСОМ =====================

def test_get_tag_by_id(manager, custom_tag1):
    """Получение тега по ID."""
    manager.add_tags([custom_tag1])

    found = manager._course.get_tag_by_id(custom_tag1.id)
    assert found is not None
    assert found.name == custom_tag1.name

    not_found = manager._course.get_tag_by_id(999)
    assert not_found is None


def test_get_tag_by_name(manager, custom_tag1):
    """Получение тега по имени."""
    manager.add_tags([custom_tag1])

    found = manager._course.get_tag("Advanced")
    assert found is not None
    assert found.id == custom_tag1.id

    not_found = manager._course.get_tag("Non Existent")
    assert not_found is None


def test_get_default_tag_by_name(manager):
    """Получение дефолтного тега по имени."""
    waiting_tag = manager._course.get_tag(DefautTagType.WAITING_FOR_SUBSCRIBE.value)
    assert waiting_tag is not None
    assert waiting_tag.name == DefautTagType.WAITING_FOR_SUBSCRIBE.value


def test_get_tags_names(manager, custom_tag1, custom_tag2):
    """Получение списка имен тегов."""
    manager.add_tags([custom_tag1, custom_tag2])

    names = manager._course.get_tags_names()
    assert len(names) == 3
    assert DefautTagType.WAITING_FOR_SUBSCRIBE.value in names
    assert "Advanced" in names
    assert "Beginners" in names


def test_cannot_set_tags_directly(manager):
    """Проверка, что нельзя напрямую присвоить теги."""
    with pytest.raises(HasNoDirectAccessError):
        manager._course.tags = []  # type: ignore


# ===================== ИНТЕГРАЦИОННЫЕ ТЕСТЫ =====================

def test_complete_tag_workflow(manager, custom_tag1, custom_tag2, student):
    """Полный рабочий процесс с тегами."""
    # 1. Добавляем теги
    manager.add_tags([custom_tag1, custom_tag2])
    assert len(manager._course.tags) == 3  # дефолтный + 2 новых

    # 2. Добавляем студентов в теги
    custom_tag1.students.append(student)
    assert len(custom_tag1.students) == 1

    # 3. Пытаемся удалить дефолтный тег (должно падать)
    default_tag = manager._course.get_tag(DefautTagType.WAITING_FOR_SUBSCRIBE.value)
    with pytest.raises(ImpossibleOperationError):
        manager.delete_tags([default_tag.id])

    # 4. Удаляем пользовательский тег
    manager.delete_tags([custom_tag1.id])
    assert custom_tag1 not in manager._course.tags
    assert custom_tag2 in manager._course.tags

    # 5. Проверяем, что дефолтный тег остался
    assert len(manager._course.tags) == 2
    assert manager._course.get_tag(DefautTagType.WAITING_FOR_SUBSCRIBE.value) is not None


def test_multiple_operations_sequence(manager, custom_tag1, custom_tag2, custom_tag3):
    """Последовательность множественных операций."""
    # Добавляем пачку тегов
    manager.add_tags([custom_tag1, custom_tag2])
    assert len(manager._course.tags) == 3  # дефолтный + 2

    # Пытаемся добавить дубликат
    with pytest.raises(NamesAlreadyExistError):
        manager.add_tags([custom_tag1])
    assert len(manager._course.tags) == 3  # не изменилось

    # Добавляем еще один
    manager.add_tags([custom_tag3])
    assert len(manager._course.tags) == 4

    # Удаляем два
    manager.delete_tags([custom_tag1.id, custom_tag3.id])
    assert len(manager._course.tags) == 2  # дефолтный + custom_tag2

    # Проверяем, что осталось
    remaining_names = [t.name for t in manager._course.tags]
    assert set(remaining_names) == {
        DefautTagType.WAITING_FOR_SUBSCRIBE.value,
        "Beginners"
    }


def test_add_max_tags(manager):
    """Добавление максимального количества тегов."""
    tags = []
    for i in range(50):
        tag = Tag(name=f"Tag{i}", course_id=1)
        tag.id = i + 10
        tags.append(tag)

    manager.add_tags(tags)

    assert len(manager._course.tags) == 51  # 50 новых + 1 дефолтный
