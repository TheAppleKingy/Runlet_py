import pytest

from src.domain.entities import TestCase, TestCases
from src.domain.entities.exceptions import DuplicateTestCaseInput, ValidationTestCaseError

# ============================================
# TestCases Tests
# ============================================


def test_testcases_empty_initialization():
    """Test TestCases with empty initialization"""
    tc = TestCases()
    assert tc.count == 0
    assert list(tc) == []
    assert tc.as_dict() == {}


def test_testcases_with_update_flag():
    """Test TestCases with_update flag"""
    tc1 = TestCases(with_update=True)
    assert tc1.with_update is True

    tc2 = TestCases(with_update=False)
    assert tc2.with_update is False

    tc3 = TestCases()  # default
    assert tc3.with_update is False


def test_testcases_iteration():
    """Test iteration over TestCases"""
    tc = TestCases()
    tc.update_test_cases({
        1: TestCase(input_="a", output="b"),
        2: TestCase(input_="c", output="d")
    })

    items = list(tc)
    assert len(items) == 2

    # Проверяем порядок и содержимое
    assert items[0][0] == 1
    assert items[0][1].input == "a"
    assert items[0][1].output == "b"

    assert items[1][0] == 2
    assert items[1][1].input == "c"
    assert items[1][1].output == "d"


def test_testcases_duplicate_inputs_different_outputs():
    """Test validation for duplicate inputs with different outputs"""
    tc = TestCases()
    with pytest.raises(DuplicateTestCaseInput):
        tc.update_test_cases({
            1: TestCase(input_="same_input", output="out1"),
            2: TestCase(input_="same_input", output="out2")  # ❌ Дубликат input
        })


def test_testcases_io_exact_duplicates_removed():
    """Test exact duplicates (same input AND output) are removed"""
    tc = TestCases()
    tc.update_test_cases({
        1: TestCase(input_="in1", output="out1"),
        2: TestCase(input_="in1", output="out1"),  # ❌ Полный дубликат
        3: TestCase(input_="in2", output="out2")
    })

    # ✅ Должен удалить один из полных дубликатов
    assert tc.count == 2

    # Проверяем, что остались уникальные пары input/output
    unique_pairs = set((case.input, case.output) for case in tc._data.values())
    assert len(unique_pairs) == 2
    assert ("in1", "out1") in unique_pairs
    assert ("in2", "out2") in unique_pairs


def test_testcases_get_case():
    """Test get_case method"""
    tc = TestCases()
    tc.update_test_cases({
        1: TestCase(input_="test1", output="result1"),
        2: TestCase(input_="test2", output="result2")
    })

    case1 = tc.get_case(1)
    assert case1 is not None
    assert case1.input == "test1"
    assert case1.output == "result1"

    case2 = tc.get_case(2)
    assert case2.input == "test2"
    assert case2.output == "result2"

    # Несуществующий тест
    case_nonexistent = tc.get_case(99)
    assert case_nonexistent is None


def test_testcases_as_dict():
    """Test as_dict method"""
    tc = TestCases()
    tc.update_test_cases({
        1: TestCase(input_="i1", output="o1"),
        2: TestCase(input_="i2", output="o2")
    })

    result = tc.as_dict()
    assert result == {
        1: {"input": "i1", "output": "o1"},
        2: {"input": "i2", "output": "o2"}
    }


def test_testcases_from_dict():
    """Test from_dict method"""
    tc = TestCases()
    result = tc.from_dict({
        1: {"input": "test1", "output": "result1"},
        2: {"input": "test2", "output": "result2"}
    })

    assert result is tc  # ✅ Возвращает self
    assert tc.count == 2
    assert tc.get_case(1).input == "test1"
    assert tc.get_case(2).output == "result2"

    # Проверяем сериализацию/десериализацию
    dict_repr = tc.as_dict()
    assert dict_repr == {
        1: {"input": "test1", "output": "result1"},
        2: {"input": "test2", "output": "result2"}
    }


def test_testcases_from_dict_chainable():
    """Test chaining from_dict calls"""
    tc = TestCases()
    tc.from_dict({
        1: {"input": "a", "output": "b"}
    }).from_dict({
        2: {"input": "c", "output": "d"}
    })

    assert tc.count == 2
    assert tc.get_case(1).input == "a"
    assert tc.get_case(2).input == "c"


def test_testcases_from_dict_with_duplicates():
    """Test from_dict with duplicates in input data"""
    tc = TestCases()

    # Дубликаты во входных данных должны быть удалены
    tc.from_dict({
        1: {"input": "same", "output": "out1"},
        2: {"input": "same", "output": "out1"},  # Полный дубликат
        3: {"input": "different", "output": "out2"}
    })

    assert tc.count == 2  # Один дубликат удален


def test_testcases_from_dict_invalid_data():
    """Test from_dict with invalid data"""
    tc = TestCases()

    with pytest.raises(ValidationTestCaseError):
        tc.from_dict({
            1: {"input": 123, "output": "output"}  # ❌ input не строка
        })


def test_testcases_update_test_cases():
    """Test update_test_cases method"""
    tc = TestCases()

    # Первоначальные данные
    tc.update_test_cases({
        1: TestCase(input_="in1", output="out1"),
        2: TestCase(input_="in2", output="out2")
    })

    # Обновление новыми данными
    tc.update_test_cases({
        3: TestCase(input_="in3", output="out3"),
        4: TestCase(input_="in4", output="out4")
    })

    assert tc.count == 4
    assert tc.get_case(1).input == "in1"
    assert tc.get_case(3).input == "in3"
    assert tc.get_case(4).output == "out4"


def test_testcases_update_with_overwrite():
    """Test update overwrites existing keys"""
    tc = TestCases()

    tc.update_test_cases({
        1: TestCase(input_="old", output="data")
    })

    # Обновляем тот же ключ
    tc.update_test_cases({
        1: TestCase(input_="new", output="data")
    })

    assert tc.count == 1
    assert tc.get_case(1).input == "new"


def test_testcases_update_with_duplicate_input_should_fail():
    """Test update with duplicate input should fail"""
    tc = TestCases()

    tc.update_test_cases({
        1: TestCase(input_="unique1", output="out1")
    })

    # Попытка добавить тест с тем же input
    with pytest.raises(DuplicateTestCaseInput):
        tc.update_test_cases({
            2: TestCase(input_="unique1", output="out2")  # ❌ Дубликат input
        })


def test_testcases_update_with_empty_dict():
    """Test updating with empty dictionary"""
    tc = TestCases()
    tc.update_test_cases({
        1: TestCase(input_="a", output="b")
    })

    # Обновление пустым словарем не должно ничего менять
    tc.update_test_cases({})
    assert tc.count == 1
    assert tc.get_case(1).input == "a"


def test_testcases_delete_test_cases():
    """Test delete_test_cases method"""
    tc = TestCases()
    tc.update_test_cases({
        1: TestCase(input_="a", output="b"),
        2: TestCase(input_="c", output="d"),
        3: TestCase(input_="e", output="f")
    })

    tc.delete_test_cases([1, 3])

    assert tc.count == 1
    assert tc.get_case(2) is not None
    assert tc.get_case(1) is None
    assert tc.get_case(3) is None


def test_testcases_delete_nonexistent():
    """Test deleting nonexistent test cases"""
    tc = TestCases()
    tc.update_test_cases({
        1: TestCase(input_="a", output="b")
    })

    # Удаление несуществующих ключей не должно вызывать ошибок
    tc.delete_test_cases([99, 100])
    assert tc.count == 1


def test_testcases_delete_empty_list():
    """Test deleting with empty list"""
    tc = TestCases()
    tc.update_test_cases({
        1: TestCase(input_="a", output="b")
    })

    tc.delete_test_cases([])
    assert tc.count == 1


def test_testcases_count_property():
    """Test count property"""
    tc = TestCases()
    assert tc.count == 0

    tc.update_test_cases({
        1: TestCase(input_="a", output="b"),
        2: TestCase(input_="c", output="d"),
        3: TestCase(input_="e", output="f")
    })
    assert tc.count == 3

    tc.delete_test_cases([1])
    assert tc.count == 2

    tc.update_test_cases({4: TestCase(input_="g", output="h")})
    assert tc.count == 3


def test_testcases_mixed_case_validations():
    """Test mixed validation scenarios"""
    tc = TestCases()

    # Все уникальные inputs - должно пройти
    tc.update_test_cases({
        1: TestCase(input_="a", output="1"),
        2: TestCase(input_="b", output="2"),
        3: TestCase(input_="c", output="3")
    })
    assert tc.count == 3

    # Попытка добавить дубликат input - должно упасть
    with pytest.raises(DuplicateTestCaseInput):
        tc.update_test_cases({4: TestCase(input_="a", output="4")})


def test_testcases_duplicate_input_output_pairs():
    """Test exact duplicate input/output pairs"""
    tc = TestCases()

    tc.update_test_cases({
        1: TestCase(input_="same", output="same"),
        2: TestCase(input_="same", output="same"),  # ❌ Полный дубликат
        3: TestCase(input_="different", output="output")
    })

    # ✅ Должен удалить один из полных дубликатов
    assert tc.count == 2

    # Проверяем, что остались уникальные пары
    unique_pairs = set((case.input, case.output) for case in tc._data.values())
    assert len(unique_pairs) == 2


def test_testcases_edge_case_empty_strings():
    """Test with empty strings as valid input/output"""
    tc = TestCases()

    tc.update_test_cases({
        1: TestCase(input_="", output=""),
        2: TestCase(input_=" ", output=" "),
        3: TestCase(input_="\t", output="\n")
    })

    assert tc.count == 3
    assert tc.get_case(1).input == ""
    assert tc.get_case(2).input == " "
    assert tc.get_case(3).input == "\t"


def test_testcases_large_number_of_cases():
    """Test with larger number of test cases"""
    tc = TestCases()

    # Добавляем 100 тестов
    test_data = {
        i: TestCase(input_=f"input_{i}", output=f"output_{i}")
        for i in range(100)
    }
    tc.update_test_cases(test_data)

    assert tc.count == 100
    assert tc.get_case(50).input == "input_50"
    assert tc.get_case(99).output == "output_99"


def test_testcases_serialization_roundtrip():
    """Test serialization/deserialization roundtrip"""
    tc1 = TestCases()
    tc1.update_test_cases({
        1: TestCase(input_="test1", output="result1"),
        2: TestCase(input_="test2", output="result2")
    })

    # Сериализуем
    dict_repr = tc1.as_dict()

    # Десериализуем в новый объект
    tc2 = TestCases().from_dict(dict_repr)

    # Проверяем равенство
    assert tc2.count == tc1.count
    assert tc2.as_dict() == dict_repr

    # Проверяем отдельные тесты
    assert tc2.get_case(1).input == "test1"
    assert tc2.get_case(2).output == "result2"


def test_testcases_clear_data():
    """Test clearing all data"""
    tc = TestCases()
    tc.update_test_cases({
        1: TestCase(input_="a", output="b"),
        2: TestCase(input_="c", output="d")
    })

    # Удаляем все
    tc.delete_test_cases([1, 2])
    assert tc.count == 0
    assert tc.as_dict() == {}
    assert list(tc) == []


def test_testcases_complex_update_scenario():
    """Test complex update scenario with duplicates"""
    tc = TestCases()

    # Этап 1: Добавляем начальные данные
    tc.update_test_cases({
        1: TestCase(input_="in1", output="out1"),
        2: TestCase(input_="in2", output="out2")
    })

    # Этап 2: Обновляем с дубликатом (должен упасть)
    try:
        tc.update_test_cases({
            3: TestCase(input_="in1", output="out3")  # ❌ Дубликат in1
        })
        pytest.fail("Should have raised DuplicateTestCaseInput")
    except DuplicateTestCaseInput:
        pass

    # Данные не должны измениться после неудачного обновления
    assert tc.count == 2
    assert tc.get_case(1).input == "in1"
    assert tc.get_case(2).input == "in2"


def test_testcases_with_update_flag_behavior():
    """Test behavior with with_update flag"""
    # Пока with_update не используется в логике, но тест на будущее
    tc = TestCases(with_update=True)
    assert tc.with_update is True

    # Проверяем, что базовая функциональность работает
    tc.update_test_cases({1: TestCase(input_="test", output="output")})
    assert tc.count == 1
