import pytest
from runlet.domain.value_objects import TestCase, TestCases
from runlet.domain.value_objects.exceptions import DuplicateTestCaseInput, ValidationTestCaseError


class TestTestCases:
    """Тесты для класса TestCases"""

    # ===== ТЕСТЫ ИНИЦИАЛИЗАЦИИ =====

    def test_create_empty(self):
        """Создание пустого TestCases"""
        test_cases = TestCases()

        assert test_cases.count == 0
        assert test_cases.as_dict() == {}
        assert list(test_cases) == []

    def test_create_with_valid_data(self):
        """Создание с валидными данными"""
        data = {
            1: TestCase(input="1 2", output="3"),
            2: TestCase(input="4 5", output="9"),
            3: TestCase(input="7 8", output="15")
        }
        test_cases = TestCases(_data=data)

        assert test_cases.count == 3
        assert test_cases.get_case(1).input == "1 2"
        assert test_cases.get_case(2).output == "9"
        assert test_cases.get_case(3).input == "7 8"

    def test_create_with_invalid_key_type(self):
        """Создание с невалидным типом ключа"""
        data = {
            "1": TestCase(input="1 2", output="3"),  # строка
            2: TestCase(input="4 5", output="9")
        }

        with pytest.raises(ValidationTestCaseError, match="Number of test should be natural int"):
            TestCases(_data=data)  # type: ignore

    def test_create_with_zero_key(self):
        """Создание с ключом 0 (не натуральное число)"""
        data = {
            0: TestCase(input="1 2", output="3"),
            1: TestCase(input="4 5", output="9")
        }

        with pytest.raises(ValidationTestCaseError, match="Number of test should be natural int"):
            TestCases(_data=data)

    def test_create_with_negative_key(self):
        """Создание с отрицательным ключом"""
        data = {
            -1: TestCase(input="1 2", output="3"),
            1: TestCase(input="4 5", output="9")
        }

        with pytest.raises(ValidationTestCaseError, match="Number of test should be natural int"):
            TestCases(_data=data)

    def test_create_with_duplicate_inputs_same_output(self):
        """Создание с дубликатами input+output - должны отфильтроваться"""
        data = {
            1: TestCase(input="1 2", output="3"),
            2: TestCase(input="1 2", output="3"),  # дубликат
            3: TestCase(input="4 5", output="9"),
            4: TestCase(input="4 5", output="9")   # дубликат
        }

        test_cases = TestCases(_data=data)

        assert test_cases.count == 2
        # Должны остаться первые вхождения
        assert 1 in test_cases.as_dict()
        assert 3 in test_cases.as_dict()
        assert 2 not in test_cases.as_dict()
        assert 4 not in test_cases.as_dict()

    def test_create_with_duplicate_inputs_different_output(self):
        """Создание с дубликатами input но разным output - ошибка"""
        data = {
            1: TestCase(input="1 2", output="3"),
            2: TestCase(input="1 2", output="4"),  # тот же input, другой output
            3: TestCase(input="4 5", output="9")
        }

        with pytest.raises(DuplicateTestCaseInput, match="Inputs cannot match"):
            TestCases(_data=data)

    # ===== ТЕСТЫ set_test_cases (ПОЛНАЯ ЗАМЕНА) =====

    def test_set_on_empty(self):
        """set_test_cases на пустой объект"""
        test_cases = TestCases()

        new_data = {
            1: TestCase(input="1", output="1"),
            2: TestCase(input="2", output="2")
        }
        test_cases.set_test_cases(new_data)

        assert test_cases.count == 2
        assert test_cases.get_case(1).input == "1"
        assert test_cases.get_case(2).output == "2"

    def test_set_completely_replaces_existing(self):
        """set_test_cases полностью заменяет существующие данные"""
        original = {
            1: TestCase(input="old1", output="old1"),
            2: TestCase(input="old2", output="old2"),
            3: TestCase(input="old3", output="old3")
        }
        test_cases = TestCases(_data=original)

        new_data = {
            4: TestCase(input="new4", output="new4"),
            5: TestCase(input="new5", output="new5")
        }
        test_cases.set_test_cases(new_data)

        assert test_cases.count == 2
        assert test_cases.get_case(1) is None  # старые удалены
        assert test_cases.get_case(2) is None
        assert test_cases.get_case(3) is None
        assert test_cases.get_case(4).input == "new4"
        assert test_cases.get_case(5).output == "new5"

    def test_set_with_overlapping_keys(self):
        """set_test_cases с пересекающимися ключами - старые заменяются"""
        original = {
            1: TestCase(input="old1", output="old1"),
            2: TestCase(input="old2", output="old2")
        }
        test_cases = TestCases(_data=original)

        new_data = {
            2: TestCase(input="new2", output="new2"),  # ключ 2 перезаписан
            3: TestCase(input="new3", output="new3")
        }
        test_cases.set_test_cases(new_data)

        assert test_cases.count == 2
        assert test_cases.get_case(1) is None  # удален
        assert test_cases.get_case(2).input == "new2"  # обновлен
        assert test_cases.get_case(3).input == "new3"  # добавлен

    def test_set_with_duplicates_in_new_data(self):
        """set_test_cases с дубликатами в новых данных"""
        test_cases = TestCases()

        new_data = {
            1: TestCase(input="1 2", output="3"),
            2: TestCase(input="1 2", output="3"),  # дубликат
            3: TestCase(input="4 5", output="9")
        }
        test_cases.set_test_cases(new_data)

        assert test_cases.count == 2
        assert 1 in test_cases.as_dict()
        assert 3 in test_cases.as_dict()
        assert 2 not in test_cases.as_dict()

    def test_set_with_duplicate_input_different_output(self):
        """set_test_cases с дубликатом input но разным output"""
        test_cases = TestCases()

        new_data = {
            1: TestCase(input="1 2", output="3"),
            2: TestCase(input="1 2", output="4")  # тот же input, другой output
        }

        with pytest.raises(DuplicateTestCaseInput):
            test_cases.set_test_cases(new_data)

    def test_set_empty_data(self):
        """set_test_cases с пустыми данными"""
        original = {
            1: TestCase(input="old", output="old")
        }
        test_cases = TestCases(_data=original)

        test_cases.set_test_cases({})

        assert test_cases.count == 0
        assert test_cases.as_dict() == {}

    # ===== ТЕСТЫ get_case =====

    def test_get_existing_case(self):
        """Получение существующего тест-кейса"""
        data = {1: TestCase(input="test", output="result")}
        test_cases = TestCases(_data=data)

        case = test_cases.get_case(1)
        assert case is not None
        assert case.input == "test"
        assert case.output == "result"

    def test_get_nonexistent_case(self):
        """Получение несуществующего тест-кейса"""
        test_cases = TestCases()

        assert test_cases.get_case(999) is None

    def test_get_after_set(self):
        """get_case после set_test_cases"""
        test_cases = TestCases()
        test_cases.set_test_cases({1: TestCase(input="a", output="b")})

        assert test_cases.get_case(1).input == "a"

        test_cases.set_test_cases({2: TestCase(input="c", output="d")})

        assert test_cases.get_case(1) is None
        assert test_cases.get_case(2).input == "c"

    # ===== ТЕСТЫ delete_test_cases =====

    def test_delete_single(self):
        """Удаление одного тест-кейса"""
        data = {
            1: TestCase(input="1", output="1"),
            2: TestCase(input="2", output="2"),
            3: TestCase(input="3", output="3")
        }
        test_cases = TestCases(_data=data)

        test_cases.delete_test_cases([2])

        assert test_cases.count == 2
        assert test_cases.get_case(1) is not None
        assert test_cases.get_case(2) is None
        assert test_cases.get_case(3) is not None

    def test_delete_multiple(self):
        """Удаление нескольких тест-кейсов"""
        data = {
            1: TestCase(input="1", output="1"),
            2: TestCase(input="2", output="2"),
            3: TestCase(input="3", output="3"),
            4: TestCase(input="4", output="4")
        }
        test_cases = TestCases(_data=data)

        test_cases.delete_test_cases([1, 3, 5])  # 5 не существует

        assert test_cases.count == 2
        assert test_cases.get_case(2) is not None
        assert test_cases.get_case(4) is not None
        assert test_cases.get_case(1) is None
        assert test_cases.get_case(3) is None

    def test_delete_all(self):
        """Удаление всех тест-кейсов"""
        data = {
            1: TestCase(input="1", output="1"),
            2: TestCase(input="2", output="2")
        }
        test_cases = TestCases(_data=data)

        test_cases.delete_test_cases([1, 2])

        assert test_cases.count == 0
        assert test_cases.as_dict() == {}

    def test_delete_empty_list(self):
        """Удаление с пустым списком"""
        data = {1: TestCase(input="1", output="1")}
        test_cases = TestCases(_data=data)

        test_cases.delete_test_cases([])

        assert test_cases.count == 1

    def test_delete_nonexistent(self):
        """Удаление несуществующих ключей"""
        data = {1: TestCase(input="1", output="1")}
        test_cases = TestCases(_data=data)

        test_cases.delete_test_cases([999, 888])

        assert test_cases.count == 1

    # ===== ТЕСТЫ as_dict =====

    def test_as_dict_empty(self):
        """as_dict для пустого объекта"""
        test_cases = TestCases()
        assert test_cases.as_dict() == {}

    def test_as_dict_with_data(self):
        """as_dict с данными"""
        data = {
            1: TestCase(input="1 2", output="3"),
            2: TestCase(input="4 5", output="9")
        }
        test_cases = TestCases(_data=data)

        result = test_cases.as_dict()
        assert result == {
            1: {"input": "1 2", "output": "3"},
            2: {"input": "4 5", "output": "9"}
        }

    def test_as_dict_returns_copy(self):
        """as_dict возвращает копию, не оригинал"""
        data = {1: TestCase(input="test", output="result")}
        test_cases = TestCases(_data=data)

        result = test_cases.as_dict()
        result[2] = {"input": "hack", "output": "hack"}  # изменяем результат

        assert test_cases.count == 1  # оригинал не изменился
        assert test_cases.get_case(2) is None

    # ===== ТЕСТЫ from_dict =====

    def test_from_dict_valid(self):
        """Создание TestCases из словаря словарей"""
        data = {
            1: {"input": "1 2", "output": "3"},
            2: {"input": "4 5", "output": "9"},
            3: {"input": "7 8", "output": "15"}
        }

        test_cases = TestCases.from_dict(data)

        assert test_cases.count == 3
        assert test_cases.get_case(1).input == "1 2"
        assert test_cases.get_case(2).output == "9"
        assert test_cases.get_case(3).input == "7 8"

    def test_from_dict_with_duplicates(self):
        """from_dict с дубликатами"""
        data = {
            1: {"input": "1 2", "output": "3"},
            2: {"input": "1 2", "output": "3"},  # дубликат
            3: {"input": "4 5", "output": "9"}
        }

        test_cases = TestCases.from_dict(data)

        assert test_cases.count == 2
        assert 1 in test_cases.as_dict()
        assert 3 in test_cases.as_dict()
        assert 2 not in test_cases.as_dict()

    def test_from_dict_with_invalid_data(self):
        """from_dict с невалидными данными"""
        data = {
            1: {"input": "1 2", "output": "3"},
            2: {"input": 123, "output": "9"}  # input не строка
        }

        with pytest.raises(ValidationTestCaseError):
            TestCases.from_dict(data)  # type: ignore

    def test_from_dict_empty(self):
        """from_dict с пустым словарем"""
        test_cases = TestCases.from_dict({})

        assert test_cases.count == 0
        assert test_cases.as_dict() == {}

    # ===== ТЕСТЫ __iter__ =====

    def test_iter_empty(self):
        """Итерация по пустому объекту"""
        test_cases = TestCases()

        items = list(test_cases)
        assert items == []

    def test_iter_with_data(self):
        """Итерация по объекту с данными"""
        data = {
            1: TestCase(input="1", output="1"),
            2: TestCase(input="2", output="2")
        }
        test_cases = TestCases(_data=data)

        items = list(test_cases)
        assert len(items) == 2
        assert isinstance(items[0], tuple)
        assert items[0][0] in [1, 2]
        assert isinstance(items[0][1], TestCase)

    def test_iter_order_preserved(self):
        """Итерация сохраняет порядок вставки"""
        data = {
            3: TestCase(input="3", output="3"),
            1: TestCase(input="1", output="1"),
            2: TestCase(input="2", output="2")
        }
        test_cases = TestCases(_data=data)

        keys = [key for key, _ in test_cases]
        assert keys == [3, 1, 2]  # порядок вставки сохраняется

    # ===== ТЕСТЫ property count =====

    def test_count_after_operations(self):
        """count после различных операций"""
        test_cases = TestCases()
        assert test_cases.count == 0

        # set
        test_cases.set_test_cases({
            1: TestCase(input="1", output="1"),
            2: TestCase(input="2", output="2")
        })
        assert test_cases.count == 2

        # delete
        test_cases.delete_test_cases([1])
        assert test_cases.count == 1

        # set again (замена)
        test_cases.set_test_cases({
            3: TestCase(input="3", output="3")
        })
        assert test_cases.count == 1
        assert test_cases.get_case(3) is not None
        assert test_cases.get_case(2) is None  # старые удалены

    # ===== ТЕСТЫ НА ВЗАИМОДЕЙСТВИЕ МЕТОДОВ =====

    def test_set_then_delete(self):
        """set_test_cases затем delete_test_cases"""
        test_cases = TestCases()

        test_cases.set_test_cases({
            1: TestCase(input="a", output="a"),
            2: TestCase(input="b", output="b"),
            3: TestCase(input="c", output="c")
        })
        assert test_cases.count == 3

        test_cases.delete_test_cases([1, 3])
        assert test_cases.count == 1
        assert test_cases.get_case(2).input == "b"

    def test_from_dict_then_set(self):
        """from_dict затем set_test_cases"""
        test_cases = TestCases.from_dict({
            1: {"input": "old", "output": "old"}
        })
        assert test_cases.count == 1

        test_cases.set_test_cases({
            2: TestCase(input="new", output="new")
        })
        assert test_cases.count == 1
        assert test_cases.get_case(2).input == "new"
        assert test_cases.get_case(1) is None

    def test_as_dict_after_set(self):
        """as_dict после set_test_cases"""
        test_cases = TestCases()
        test_cases.set_test_cases({
            1: TestCase(input="x", output="y")
        })

        assert test_cases.as_dict() == {
            1: {"input": "x", "output": "y"}
        }

    # ===== ТЕСТЫ ГРАНИЧНЫХ СЛУЧАЕВ =====

    def test_large_numbers_as_keys(self):
        """Большие числа в качестве ключей"""
        data = {
            999999: TestCase(input="big", output="number"),
            1000000: TestCase(input="very big", output="very number")
        }
        test_cases = TestCases(_data=data)

        assert test_cases.count == 2
        assert test_cases.get_case(999999).input == "big"
        assert test_cases.get_case(1000000).output == "very number"

    def test_special_characters_in_input(self):
        """Спецсимволы в input/output"""
        data = {
            1: TestCase(input="!@#$%^&*()", output="\\n\\t\\r"),
            2: TestCase(input="你好世界", output="안녕하세요"),
            3: TestCase(input="\n\t\r", output="   ")
        }
        test_cases = TestCases(_data=data)

        assert test_cases.count == 3
        assert test_cases.get_case(1).input == "!@#$%^&*()"
        assert test_cases.get_case(1).output == "\\n\\t\\r"
        assert test_cases.get_case(2).input == "你好世界"
        assert test_cases.get_case(3).input == "\n\t\r"

    def test_empty_strings(self):
        """Пустые строки в input/output"""
        data = {
            1: TestCase(input="", output=""),
            2: TestCase(input=" ", output=" ")
        }
        test_cases = TestCases(_data=data)

        assert test_cases.count == 2
        assert test_cases.get_case(1).input == ""
        assert test_cases.get_case(1).output == ""
        assert test_cases.get_case(2).input == " "
        assert test_cases.get_case(2).output == " "

    def test_very_long_strings(self):
        """Очень длинные строки"""
        long_input = "a" * 10000
        long_output = "b" * 10000

        data = {1: TestCase(input=long_input, output=long_output)}
        test_cases = TestCases(_data=data)

        assert test_cases.count == 1
        assert len(test_cases.get_case(1).input) == 10000
        assert len(test_cases.get_case(1).output) == 10000

    def test_max_int_key(self):
        """Максимальное значение int как ключ"""
        max_int = 2**31 - 1
        data = {max_int: TestCase(input="max", output="int")}

        test_cases = TestCases(_data=data)

        assert test_cases.count == 1
        assert test_cases.get_case(max_int).input == "max"

    # ===== ТЕСТЫ ИНТЕГРАЦИОННЫЕ =====

    def test_complete_workflow(self):
        """Полный рабочий процесс"""
        # 1. Создание пустого
        test_cases = TestCases()
        assert test_cases.count == 0

        # 2. Установка данных
        test_cases.set_test_cases({
            1: TestCase(input="1 2", output="3"),
            2: TestCase(input="4 5", output="9"),
            3: TestCase(input="7 8", output="15")
        })
        assert test_cases.count == 3

        # 3. Получение конкретного
        case = test_cases.get_case(2)
        assert case is not None
        assert case.input == "4 5"

        # 4. Удаление одного
        test_cases.delete_test_cases([1])
        assert test_cases.count == 2
        assert test_cases.get_case(1) is None

        # 5. Конвертация в dict
        as_dict = test_cases.as_dict()
        assert as_dict == {
            2: {"input": "4 5", "output": "9"},
            3: {"input": "7 8", "output": "15"}
        }

        # 6. Создание нового из dict
        new_test_cases = TestCases.from_dict(as_dict)
        assert new_test_cases.count == 2
        assert new_test_cases.get_case(2).input == "4 5"

        # 7. Полная замена данных
        new_test_cases.set_test_cases({
            10: TestCase(input="new", output="new")
        })
        assert new_test_cases.count == 1
        assert new_test_cases.get_case(10).input == "new"
        assert new_test_cases.get_case(2) is None

    def test_duplicate_handling_through_operations(self):
        """Обработка дубликатов через разные операции"""
        test_cases = TestCases()

        # Первая установка - ок
        test_cases.set_test_cases({
            1: TestCase(input="same", output="1"),
            2: TestCase(input="different", output="2")
        })
        assert test_cases.count == 2

        # Попытка установить с дубликатом input но разным output
        with pytest.raises(DuplicateTestCaseInput):
            test_cases.set_test_cases({
                3: TestCase(input="same", output="3"),  # конфликт с existing
                4: TestCase(input="same", output="4")
            })

        # Данные не изменились
        assert test_cases.count == 2
        assert test_cases.get_case(1).output == "1"
