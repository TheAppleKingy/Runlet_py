import pytest
from dataclasses import field
from src.domain.entities import Course, Module, User, Problem
from src.domain.entities.exceptions import (
    NamesAlreadyExistError,
    IncorrectModulesOrdersError,
    UndefinedModuleError,
    HasNoDirectAccessError,
    RepeatableNamesError
)
from src.domain.services.course import CourseModulesManagerService


@pytest.fixture
def course():
    """Базовый курс без модулей."""
    course = Course(name="Test Course", _teacher_id=42)
    course.id = 1
    return course


@pytest.fixture
def manager(course):
    """Менеджер с пустым курсом."""
    return CourseModulesManagerService(course)


@pytest.fixture
def module1():
    """Модуль 1."""
    module = Module(name="Module 1", course_id=1)
    module.id = 1
    module.order = 1
    return module


@pytest.fixture
def module2():
    """Модуль 2."""
    module = Module(name="Module 2", course_id=1)
    module.id = 2
    module.order = 2
    return module


@pytest.fixture
def module3():
    """Модуль 3."""
    module = Module(name="Module 3", course_id=1)
    module.id = 3
    module.order = 3
    return module


@pytest.fixture
def course_with_modules(course, module1, module2):
    """Курс с существующими модулями."""
    course._modules = [module1, module2]
    return course


@pytest.fixture
def manager_with_modules(course_with_modules):
    """Менеджер с курсом, содержащим модули."""
    return CourseModulesManagerService(course_with_modules)


# ===================== ТЕСТЫ _validate_repeatable_names =====================

def test_validate_repeatable_names_unique_names(manager):
    """Должен пропускать уникальные имена."""
    modules = [
        Module(name="Module A", course_id=1),
        Module(name="Module B", course_id=1),
        Module(name="Module C", course_id=1)
    ]
    # Не должно быть исключения
    manager._validate_repeatable_names(modules)


def test_validate_repeatable_names_duplicates(manager):
    """Должен кидать ошибку при дубликатах имен."""
    modules = [
        Module(name="Same Name", course_id=1),
        Module(name="Same Name", course_id=1),
        Module(name="Different", course_id=1)
    ]

    with pytest.raises(RepeatableNamesError) as exc_info:
        manager._validate_repeatable_names(modules)

    assert "Names of module cannot match" in str(exc_info.value)


def test_validate_repeatable_names_empty_list(manager):
    """Пустой список должен проходить валидацию."""
    manager._validate_repeatable_names([])


def test_validate_repeatable_names_single_module(manager):
    """Один модуль всегда проходит."""
    manager._validate_repeatable_names([Module(name="Single", course_id=1)])


# ===================== ТЕСТЫ _validate_already_exists =====================

def test_validate_already_exists_no_conflicts(manager_with_modules, module3):
    """Нет конфликтов - новые имена уникальны."""
    manager_with_modules._validate_already_exists(
        manager_with_modules._course.modules,
        [module3]
    )


def test_validate_already_exists_with_conflict(manager_with_modules, module1):
    """Конфликт имен - должно кидать ошибку."""
    with pytest.raises(NamesAlreadyExistError) as exc_info:
        manager_with_modules._validate_already_exists(
            manager_with_modules._course.modules,
            [module1]
        )

    assert "already exists in course" in str(exc_info.value)


def test_validate_already_exists_multiple_conflicts(manager_with_modules, module1, module2):
    """Множественные конфликты."""
    with pytest.raises(NamesAlreadyExistError):
        manager_with_modules._validate_already_exists(
            manager_with_modules._course.modules,
            [module1, module2]
        )


def test_validate_already_exists_empty_incoming(manager_with_modules):
    """Пустой список новых модулей."""
    manager_with_modules._validate_already_exists(
        manager_with_modules._course.modules,
        []
    )


def test_validate_already_exists_empty_current(manager, module1):
    """Текущий список пуст."""
    manager._validate_already_exists([], [module1])  # Не должно быть ошибки


# ===================== ТЕСТЫ _validate_orders =====================

def test_validate_orders_sequential_from_one(manager):
    """Порядки идут последовательно с 1."""
    current = []
    incoming = [
        Module(name="M1", course_id=1, order=1),
        Module(name="M2", course_id=1, order=2),
        Module(name="M3", course_id=1, order=3)
    ]
    manager._validate_orders(current, incoming)


def test_validate_orders_with_existing(manager_with_modules, module3):
    """Добавление модуля с правильным порядком."""
    manager_with_modules._validate_orders(
        manager_with_modules._course.modules,
        [module3]
    )


def test_validate_orders_insert_between(manager_with_modules):
    """Вставка модуля между существующими."""
    new_module = Module(name="Inserted", course_id=1, order=2)
    new_module.id = 4

    with pytest.raises(IncorrectModulesOrdersError):
        manager_with_modules._validate_orders(
            manager_with_modules._course.modules,
            [new_module]
        )


def test_validate_orders_gap_not_allowed(manager_with_modules):
    """Пропуск в порядках недопустим."""
    new_module = Module(name="With Gap", course_id=1, order=5)
    new_module.id = 4

    with pytest.raises(IncorrectModulesOrdersError):
        manager_with_modules._validate_orders(
            manager_with_modules._course.modules,
            [new_module]
        )


def test_validate_orders_duplicate_order(manager_with_modules, module2):
    """Дубликат порядка недопустим."""
    with pytest.raises(IncorrectModulesOrdersError):
        manager_with_modules._validate_orders(
            manager_with_modules._course.modules,
            [module2]  # order=2 уже есть
        )


def test_validate_orders_zero_order(manager):
    """Порядок 0 недопустим."""
    new_module = Module(name="Zero", course_id=1, order=0)
    new_module.id = 4

    with pytest.raises(IncorrectModulesOrdersError):
        manager._validate_orders([], [new_module])


def test_validate_orders_negative_order(manager):
    """Отрицательный порядок недопустим."""
    new_module = Module(name="Negative", course_id=1, order=-1)
    new_module.id = 4

    with pytest.raises(IncorrectModulesOrdersError):
        manager._validate_orders([], [new_module])


def test_validate_orders_multiple_duplicates(manager_with_modules):
    """Множественные дубликаты порядков."""
    new_modules = [
        Module(name="New1", course_id=1, order=2),  # дубль
        Module(name="New2", course_id=1, order=2),  # дубль
        Module(name="New3", course_id=1, order=3)
    ]
    for i, m in enumerate(new_modules):
        m.id = i + 10

    with pytest.raises(IncorrectModulesOrdersError):
        manager_with_modules._validate_orders(
            manager_with_modules._course.modules,
            new_modules
        )


def test_validate_orders_start_not_from_one(manager):
    """Порядки должны начинаться с 1."""
    new_modules = [
        Module(name="M1", course_id=1, order=2),
        Module(name="M2", course_id=1, order=3)
    ]

    with pytest.raises(IncorrectModulesOrdersError):
        manager._validate_orders([], new_modules)


# ===================== ТЕСТЫ add_modules =====================

def test_add_modules_to_empty_course(manager, module1):
    """Добавление модуля в пустой курс."""
    assert len(manager._course.modules) == 0

    manager.add_modules([module1])

    assert len(manager._course.modules) == 1
    assert manager._course.modules[0].name == "Module 1"
    assert manager._course.modules[0].order == 1


def test_add_multiple_modules(manager, module1, module2, module3):
    """Добавление нескольких модулей."""
    manager.add_modules([module1, module2, module3])

    assert len(manager._course.modules) == 3
    orders = [m.order for m in manager._course.modules]
    assert orders == [1, 2, 3]


def test_add_modules_to_existing(manager_with_modules, module3):
    """Добавление модуля к существующим."""
    initial_count = len(manager_with_modules._course.modules)

    manager_with_modules.add_modules([module3])

    assert len(manager_with_modules._course.modules) == initial_count + 1
    assert module3 in manager_with_modules._course.modules


def test_add_modules_with_duplicate_names(manager_with_modules, module1):
    """Добавление модуля с существующим именем."""
    with pytest.raises(NamesAlreadyExistError):
        manager_with_modules.add_modules([module1])

    assert len(manager_with_modules._course.modules) == 2  # не изменилось


def test_add_modules_with_duplicate_orders(manager_with_modules):
    """Добавление модуля с существующим порядком."""
    new_module = Module(name="New", course_id=1, order=2)
    new_module.id = 4

    with pytest.raises(IncorrectModulesOrdersError):
        manager_with_modules.add_modules([new_module])


def test_add_modules_with_self_duplicate_names(manager):
    """Дубликаты имен в одном списке добавления."""
    modules = [
        Module(name="Same", course_id=1, order=1),
        Module(name="Same", course_id=1, order=2)
    ]
    for i, m in enumerate(modules):
        m.id = i + 10

    with pytest.raises(RepeatableNamesError):
        manager.add_modules(modules)


def test_add_modules_empty_list(manager):
    """Добавление пустого списка."""
    initial_count = len(manager._course.modules)
    manager.add_modules([])

    assert len(manager._course.modules) == initial_count


def test_add_modules_reorder_validation(manager_with_modules):
    """Проверка, что порядок валидируется правильно при вставке."""
    # Добавляем модуль с порядком 2 (вставка между 1 и 3)
    new_module = Module(name="Inserted", course_id=1, order=2)
    new_module.id = 4

    # Добавляем еще модуль с порядком 3 (должен быть 3 или 4? - проверим логику)
    another_module = Module(name="Another", course_id=1, order=3)
    another_module.id = 5

    with pytest.raises(IncorrectModulesOrdersError):
        manager_with_modules.add_modules([new_module, another_module])


# ===================== ТЕСТЫ delete_modules =====================

def test_delete_modules_by_id(manager_with_modules, module1):
    """Удаление модуля по ID."""
    assert len(manager_with_modules._course.modules) == 2

    manager_with_modules.delete_modules([module1.id])

    assert len(manager_with_modules._course.modules) == 1
    assert manager_with_modules._course.modules[0].id == 2


def test_delete_multiple_modules(manager_with_modules, module1, module2):
    """Удаление нескольких модулей."""
    manager_with_modules.delete_modules([module1.id, module2.id])

    assert len(manager_with_modules._course.modules) == 0


def test_delete_nonexistent_modules(manager_with_modules):
    """Удаление несуществующих ID."""
    initial_count = len(manager_with_modules._course.modules)

    manager_with_modules.delete_modules([999, 888])

    assert len(manager_with_modules._course.modules) == initial_count


def test_delete_mixed_existing_and_nonexistent(manager_with_modules, module1):
    """Удаление смеси существующих и несуществующих ID."""
    initial_count = len(manager_with_modules._course.modules)

    manager_with_modules.delete_modules([module1.id, 999, 888])

    assert len(manager_with_modules._course.modules) == initial_count - 1
    assert all(m.id != module1.id for m in manager_with_modules._course.modules)


def test_delete_empty_list(manager_with_modules):
    """Удаление с пустым списком ID."""
    initial_count = len(manager_with_modules._course.modules)

    manager_with_modules.delete_modules([])

    assert len(manager_with_modules._course.modules) == initial_count


def test_delete_all_modules(manager_with_modules):
    """Удаление всех модулей."""
    all_ids = [m.id for m in manager_with_modules._course.modules]

    manager_with_modules.delete_modules(all_ids)

    assert len(manager_with_modules._course.modules) == 0


# ===================== ИНТЕГРАЦИОННЫЕ ТЕСТЫ =====================

def test_add_then_delete_workflow(manager):
    """Полный цикл: добавить, потом удалить."""
    # Добавляем модули
    m1 = Module(name="Temp1", course_id=1, order=1)
    m2 = Module(name="Temp2", course_id=1, order=2)
    m1.id = 10
    m2.id = 11

    manager.add_modules([m1, m2])
    assert len(manager._course.modules) == 2

    # Удаляем один
    manager.delete_modules([m1.id])
    assert len(manager._course.modules) == 1
    assert manager._course.modules[0].id == 11

    # Удаляем второй
    manager.delete_modules([m2.id])
    assert len(manager._course.modules) == 0


def test_validate_orders_complex_scenario(manager_with_modules):
    """Сложный сценарий валидации порядков."""
    # Текущие порядки: 1, 2
    new_modules = [
        Module(name="A", course_id=1, order=1),  # дубль с существующим
        Module(name="B", course_id=1, order=3),  # ок, если 1 уберется?
        Module(name="C", course_id=1, order=4)
    ]
    for i, m in enumerate(new_modules):
        m.id = i + 10

    # Должно упасть из-за дубля 1
    with pytest.raises(IncorrectModulesOrdersError):
        manager_with_modules._validate_orders(
            manager_with_modules._course.modules,
            new_modules
        )


def test_cannot_set_modules_directly(course_with_modules):
    """Проверка, что нельзя напрямую присвоить модули."""
    with pytest.raises(HasNoDirectAccessError):
        course_with_modules.modules = []


def test_get_modules_names(course_with_modules):
    """Проверка получения имен модулей."""
    names = course_with_modules.get_modules_names()
    assert names == ["Module 1", "Module 2"]


def test_get_module_by_name(course_with_modules, module1):
    """Получение модуля по имени."""
    found = course_with_modules.get_module("Module 1")
    assert found is not None
    assert found.id == module1.id
    assert found.name == module1.name

    not_found = course_with_modules.get_module("Non Existent")
    assert not_found is None


def test_get_module_by_id(course_with_modules, module1):
    """Получение модуля по ID."""
    found = course_with_modules.get_module_by_id(module1.id)
    assert found is not None
    assert found.name == module1.name

    not_found = course_with_modules.get_module_by_id(999)
    assert not_found is None


# ===================== ТЕСТЫ ГРАНИЧНЫХ СЛУЧАЕВ =====================

def test_add_modules_with_max_order(manager):
    """Добавление модуля с максимальным порядком."""
    modules = [Module(name=f"M{i}", course_id=1, order=i+1) for i in range(100)]
    for i, m in enumerate(modules):
        m.id = i + 100

    manager.add_modules(modules)
    assert len(manager._course.modules) == 100
    assert max(m.order for m in manager._course.modules) == 100


def test_validate_orders_with_large_gap(manager_with_modules):
    """Большой пропуск в порядках."""
    new_module = Module(name="Large Gap", course_id=1, order=100)
    new_module.id = 4

    with pytest.raises(IncorrectModulesOrdersError):
        manager_with_modules._validate_orders(
            manager_with_modules._course.modules,
            [new_module]
        )


def test_add_modules_with_same_order_different_names(manager):
    """Добавление модулей с одинаковым порядком."""
    modules = [
        Module(name="M1", course_id=1, order=1),
        Module(name="M2", course_id=1, order=1)  # одинаковый порядок
    ]
    for i, m in enumerate(modules):
        m.id = i + 10

    with pytest.raises(IncorrectModulesOrdersError):
        manager.add_modules(modules)


def test_delete_modules_preserves_remaining(manager_with_modules, module1):
    """Удаление не должно влиять на оставшиеся модули."""
    remaining = [m for m in manager_with_modules._course.modules if m.id != module1.id]
    remaining_names = [m.name for m in remaining]

    manager_with_modules.delete_modules([module1.id])

    assert [m.name for m in manager_with_modules._course.modules] == remaining_names
