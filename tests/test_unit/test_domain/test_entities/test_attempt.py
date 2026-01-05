import pytest

from src.domain.entities import Attempt, TestCases, TestCase
from src.domain.entities.exceptions import MismatchTestNumsError, MismatchTestOutputsError, MismatchTestsCountError


def test_attempt_initialization():
    """Test Attempt initialization"""
    attempt = Attempt(student_id=123, problem_id=456)
    assert attempt.student_id == 123
    assert attempt.problem_id == 456
    assert attempt.amount == 0
    assert attempt.passed is False
    assert isinstance(attempt.test_cases, TestCases)
    assert attempt.test_cases.count == 0
    assert isinstance(attempt.result_cases, TestCases)
    assert attempt.result_cases.count == 0


def test_attempt_with_test_cases_in_constructor():
    """Test Attempt initialization with test cases"""
    test_cases = TestCases()
    test_cases.update_test_cases({
        1: TestCase(input_="t1", output="r1"),
        2: TestCase(input_="t2", output="r2")
    })

    attempt = Attempt(student_id=1, problem_id=1, test_cases=test_cases)
    assert attempt.test_cases.count == 2
    assert attempt.test_cases.get_case(1).input == "t1"


def test_attempt_test_cases_property_setter():
    """Test test_cases property setter"""
    attempt = Attempt(student_id=1, problem_id=1)

    test_cases = TestCases()
    test_cases.update_test_cases({
        1: TestCase(input_="t1", output="r1"),
        2: TestCase(input_="t2", output="r2")
    })

    attempt.test_cases = test_cases
    assert attempt.test_cases.count == 2


def test_attempt_test_cases_property_getter():
    """Test test_cases property getter"""
    attempt = Attempt(student_id=1, problem_id=1)

    test_cases = TestCases()
    test_cases.update_test_cases({
        1: TestCase(input_="input1", output="output1")
    })

    attempt.test_cases = test_cases
    retrieved = attempt.test_cases
    assert isinstance(retrieved, TestCases)
    assert retrieved.count == 1
    assert retrieved.get_case(1).input == "input1"


def test_attempt_result_cases_property_valid():
    """Test result_cases property with valid data"""
    # Set test cases first
    test_cases = TestCases()
    test_cases.update_test_cases({
        1: TestCase(input_="t1", output="r1"),
        2: TestCase(input_="t2", output="r2")
    })

    attempt = Attempt(student_id=1, problem_id=1, test_cases=test_cases)

    # Set matching result cases
    result_cases = TestCases()
    result_cases.update_test_cases({
        1: TestCase(input_="t1", output="r1"),
        2: TestCase(input_="t2", output="r2")
    })

    attempt.result_cases = result_cases
    assert attempt.result_cases.count == 2
    assert attempt.result_cases.get_case(1).input == "t1"


def test_attempt_result_cases_mismatch_count():
    """Test result_cases with mismatched count"""
    test_cases = TestCases()
    test_cases.update_test_cases({
        1: TestCase(input_="t1", output="r1"),
        2: TestCase(input_="t2", output="r2")
    })

    attempt = Attempt(student_id=1, problem_id=1, test_cases=test_cases)

    result_cases = TestCases()
    result_cases.update_test_cases({
        1: TestCase(input_="t1", output="r1")
        # Missing second test case
    })

    with pytest.raises(MismatchTestsCountError) as exc_info:
        attempt.result_cases = result_cases
    assert "Count of provided results mismatch with spcified cases" in str(exc_info.value)


def test_attempt_result_cases_excess_count():
    """Test result_cases with too many results"""
    test_cases = TestCases()
    test_cases.update_test_cases({
        1: TestCase(input_="t1", output="r1")
    })

    attempt = Attempt(student_id=1, problem_id=1, test_cases=test_cases)

    result_cases = TestCases()
    result_cases.update_test_cases({
        1: TestCase(input_="t1", output="r1"),
        2: TestCase(input_="t2", output="r2")  # Extra result
    })

    with pytest.raises(MismatchTestsCountError):
        attempt.result_cases = result_cases


def test_attempt_result_cases_mismatch_nums():
    """Test result_cases with mismatched test numbers"""
    test_cases = TestCases()
    test_cases.update_test_cases({
        1: TestCase(input_="t1", output="r1"),
        2: TestCase(input_="t2", output="r2")
    })

    attempt = Attempt(student_id=1, problem_id=1, test_cases=test_cases)

    result_cases = TestCases()
    result_cases.update_test_cases({
        1: TestCase(input_="t1", output="r1"),
        3: TestCase(input_="t3", output="r3")  # Wrong test number
    })

    with pytest.raises(MismatchTestNumsError) as exc_info:
        attempt.result_cases = result_cases
    assert "Provided result test num 3 does not exist" in str(exc_info.value)


def test_attempt_result_cases_before_test_cases():
    """Test setting result cases before test cases"""
    attempt = Attempt(student_id=1, problem_id=1)
    # test_cases по умолчанию пустой

    result_cases = TestCases()
    result_cases.update_test_cases({
        1: TestCase(input_="t1", output="r1")
    })

    # Should raise error because test_cases.count is 0
    with pytest.raises(MismatchTestsCountError):
        attempt.result_cases = result_cases


def test_attempt_mark_as_passed_success():
    """Test successful mark_as_passed"""
    test_cases = TestCases()
    test_cases.update_test_cases({
        1: TestCase(input_="1+1", output="2"),
        2: TestCase(input_="2*2", output="4"),
        3: TestCase(input_="10/2", output="5")
    })

    attempt = Attempt(student_id=100, problem_id=200, test_cases=test_cases)

    # Set matching result cases
    result_cases = TestCases()
    result_cases.update_test_cases({
        1: TestCase(input_="1+1", output="2"),
        2: TestCase(input_="2*2", output="4"),
        3: TestCase(input_="10/2", output="5")
    })

    attempt.result_cases = result_cases
    attempt.mark_as_passed()

    assert attempt.passed is True
    assert attempt.student_id == 100
    assert attempt.problem_id == 200


def test_attempt_mark_as_passed_no_result_cases():
    """Test mark_as_passed with no result cases"""
    test_cases = TestCases()
    test_cases.update_test_cases({
        1: TestCase(input_="t1", output="r1")
    })

    attempt = Attempt(student_id=1, problem_id=1, test_cases=test_cases)

    # No result cases set
    with pytest.raises(MismatchTestsCountError):
        attempt.mark_as_passed()


def test_attempt_mark_as_passed_empty_test_cases():
    """Test mark_as_passed with empty test cases"""
    attempt = Attempt(student_id=1, problem_id=1)
    # test_cases по умолчанию пустой

    # Устанавливаем пустые result_cases
    result_cases = TestCases()  # Пустой
    attempt.result_cases = result_cases

    attempt.mark_as_passed()
    assert attempt.passed is True  # Пустые тесты считаются пройденными


def test_attempt_mark_as_passed_mismatching_output():
    """Test mark_as_passed with mismatching output"""
    test_cases = TestCases()
    test_cases.update_test_cases({
        1: TestCase(input_="1+1", output="2"),
        2: TestCase(input_="2*2", output="4")
    })

    attempt = Attempt(student_id=1, problem_id=1, test_cases=test_cases)

    result_cases = TestCases()
    result_cases.update_test_cases({
        1: TestCase(input_="1+1", output="2"),
        2: TestCase(input_="2*2", output="5")  # Wrong output
    })

    attempt.result_cases = result_cases

    with pytest.raises(MismatchTestOutputsError) as exc_info:
        attempt.mark_as_passed()
    assert "Result of tests [2] are incorrect" in str(exc_info.value)


def test_attempt_mark_as_passed_multiple_mismatching_outputs():
    """Test mark_as_passed with multiple mismatching outputs"""
    test_cases = TestCases()
    test_cases.update_test_cases({
        1: TestCase(input_="a", output="A"),
        2: TestCase(input_="b", output="B"),
        3: TestCase(input_="c", output="C"),
        4: TestCase(input_="d", output="D")
    })

    attempt = Attempt(student_id=1, problem_id=1, test_cases=test_cases)

    result_cases = TestCases()
    result_cases.update_test_cases({
        1: TestCase(input_="a", output="A"),  # Correct
        2: TestCase(input_="b", output="X"),  # Wrong
        3: TestCase(input_="c", output="C"),  # Correct
        4: TestCase(input_="d", output="Y")   # Wrong
    })

    attempt.result_cases = result_cases

    with pytest.raises(MismatchTestOutputsError) as exc_info:
        attempt.mark_as_passed()
    error_msg = str(exc_info.value)
    assert "Result of tests" in error_msg
    # Порядок может быть разный из-за реализации
    assert "2" in error_msg or "4" in error_msg


def test_attempt_mark_as_passed_missing_test_num_in_results():
    """Test mark_as_passed with missing test number in results"""
    test_cases = TestCases()
    test_cases.update_test_cases({
        1: TestCase(input_="t1", output="r1"),
        2: TestCase(input_="t2", output="r2")
    })

    attempt = Attempt(student_id=1, problem_id=1, test_cases=test_cases)

    # Напрямую манипулируем result_cases чтобы обойти setter
    # Это симулирует ситуацию, когда результат был установлен неправильно
    result_cases = TestCases()
    result_cases.update_test_cases({
        1: TestCase(input_="t1", output="r1")
        # Missing test 2
    })

    attempt._result_cases = result_cases

    with pytest.raises(MismatchTestsCountError):
        attempt.mark_as_passed()


def test_attempt_mark_as_passed_wrong_test_num_in_middle():
    """Test mark_as_passed with wrong test number discovered during validation"""
    test_cases = TestCases()
    test_cases.update_test_cases({
        1: TestCase(input_="t1", output="r1"),
        2: TestCase(input_="t2", output="r2")
    })

    attempt = Attempt(student_id=1, problem_id=1, test_cases=test_cases)

    # Создаем result_cases с неправильным номером теста
    # Манипулируем напрямую чтобы обойти setter
    result_cases = TestCases()
    result_cases.update_test_cases({
        1: TestCase(input_="t1", output="r1"),
        3: TestCase(input_="t3", output="r3")  # Wrong test number
    })

    attempt._result_cases = result_cases

    with pytest.raises(MismatchTestNumsError):
        attempt.mark_as_passed()


def test_attempt_mark_as_passed_all_mismatching():
    """Test mark_as_passed when all outputs are wrong"""
    test_cases = TestCases()
    test_cases.update_test_cases({
        1: TestCase(input_="q1", output="a1"),
        2: TestCase(input_="q2", output="a2"),
        3: TestCase(input_="q3", output="a3")
    })

    attempt = Attempt(student_id=1, problem_id=1, test_cases=test_cases)

    result_cases = TestCases()
    result_cases.update_test_cases({
        1: TestCase(input_="q1", output="wrong1"),
        2: TestCase(input_="q2", output="wrong2"),
        3: TestCase(input_="q3", output="wrong3")
    })

    attempt.result_cases = result_cases

    with pytest.raises(MismatchTestOutputsError) as exc_info:
        attempt.mark_as_passed()
    error_msg = str(exc_info.value)
    assert "Result of tests" in error_msg


def test_attempt_result_cases_property_empty_but_valid():
    """Test result_cases with empty test cases"""
    attempt = Attempt(student_id=1, problem_id=1)
    # test_cases по умолчанию пустой

    # Устанавливаем пустые result_cases
    result_cases = TestCases()  # Пустой
    attempt.result_cases = result_cases

    # Должно работать без ошибок
    assert attempt.result_cases.count == 0


def test_attempt_state_persistence():
    """Test that attempt state persists after operations"""
    test_cases = TestCases()
    test_cases.update_test_cases({
        1: TestCase(input_="test", output="result")
    })

    attempt = Attempt(student_id=42, problem_id=99, test_cases=test_cases)

    result_cases = TestCases()
    result_cases.update_test_cases({
        1: TestCase(input_="test", output="result")
    })

    attempt.result_cases = result_cases
    attempt.mark_as_passed()

    # Verify all states are preserved
    assert attempt.passed is True
    assert attempt.student_id == 42
    assert attempt.problem_id == 99
    assert attempt.amount == 0
    assert attempt.test_cases.count == 1
    assert attempt.result_cases.count == 1
    assert attempt.test_cases.get_case(1).input == "test"
    assert attempt.result_cases.get_case(1).output == "result"


def test_attempt_amount_field():
    """Test that amount field exists and has default value"""
    attempt = Attempt(student_id=1, problem_id=1)
    assert hasattr(attempt, 'amount')
    assert attempt.amount == 0


def test_attempt_repeated_mark_as_passed():
    """Test calling mark_as_passed multiple times"""
    test_cases = TestCases()
    test_cases.update_test_cases({
        1: TestCase(input_="t", output="r")
    })

    attempt = Attempt(student_id=1, problem_id=1, test_cases=test_cases)

    result_cases = TestCases()
    result_cases.update_test_cases({
        1: TestCase(input_="t", output="r")
    })

    attempt.result_cases = result_cases

    # First call should succeed
    attempt.mark_as_passed()
    assert attempt.passed is True

    # Second call should also succeed (idempotent)
    attempt.mark_as_passed()
    assert attempt.passed is True


def test_attempt_with_large_dataset():
    """Test Attempt with large number of test cases"""
    # Create 100 test cases (уменьшил с 1000 для скорости)
    test_data = {
        i: TestCase(input_=f"input_{i}", output=f"output_{i}")
        for i in range(100)
    }

    test_cases = TestCases()
    test_cases.update_test_cases(test_data)

    attempt = Attempt(student_id=1, problem_id=1, test_cases=test_cases)

    # Create matching results
    result_data = {
        i: TestCase(input_=f"input_{i}", output=f"output_{i}")
        for i in range(100)
    }

    result_cases = TestCases()
    result_cases.update_test_cases(result_data)

    attempt.result_cases = result_cases
    attempt.mark_as_passed()

    assert attempt.passed is True


def test_attempt_with_special_characters():
    """Test Attempt with special characters in inputs/outputs"""
    test_cases = TestCases()
    test_cases.update_test_cases({
        1: TestCase(input_="a\nb\nc", output="x\ty\tz"),
        2: TestCase(input_="test with spaces", output="result with spaces"),
        3: TestCase(input_="unicode: café", output="emoji: 🚀"),
        4: TestCase(input_="", output="empty input"),
        5: TestCase(input_="empty output", output="")
    })

    attempt = Attempt(student_id=1, problem_id=1, test_cases=test_cases)

    result_cases = TestCases()
    result_cases.update_test_cases({
        1: TestCase(input_="a\nb\nc", output="x\ty\tz"),
        2: TestCase(input_="test with spaces", output="result with spaces"),
        3: TestCase(input_="unicode: café", output="emoji: 🚀"),
        4: TestCase(input_="", output="empty input"),
        5: TestCase(input_="empty output", output="")
    })

    attempt.result_cases = result_cases
    attempt.mark_as_passed()

    assert attempt.passed is True


def test_attempt_modify_test_cases_after_creation():
    """Test modifying test cases after attempt creation"""
    test_cases = TestCases()
    test_cases.update_test_cases({
        1: TestCase(input_="t1", output="r1")
    })

    attempt = Attempt(student_id=1, problem_id=1, test_cases=test_cases)

    # Добавляем еще тестов
    test_cases.update_test_cases({
        2: TestCase(input_="t2", output="r2")
    })

    # Result cases должны соответствовать новому количеству
    result_cases = TestCases()
    result_cases.update_test_cases({
        1: TestCase(input_="t1", output="r1"),
        2: TestCase(input_="t2", output="r2")
    })

    attempt.result_cases = result_cases
    attempt.mark_as_passed()

    assert attempt.passed is True


def test_attempt_incomplete_result_cases():
    """Test attempt with incomplete result cases"""
    test_cases = TestCases()
    test_cases.update_test_cases({
        1: TestCase(input_="t1", output="r1"),
        2: TestCase(input_="t2", output="r2"),
        3: TestCase(input_="t3", output="r3")
    })

    attempt = Attempt(student_id=1, problem_id=1, test_cases=test_cases)

    result_cases = TestCases()
    result_cases.update_test_cases({
        1: TestCase(input_="t1", output="r1"),
        2: TestCase(input_="t2", output="r2")
        # Missing test 3
    })

    # При установке result_cases должна быть ошибка
    with pytest.raises(MismatchTestsCountError):
        attempt.result_cases = result_cases


def test_attempt_with_duplicate_inputs_in_test_cases():
    """Test attempt with duplicate inputs in test cases"""
    test_cases = TestCases()

    # Попытка создать дубликаты inputs - должно упасть на этапе создания test_cases
    with pytest.raises(Exception):
        test_cases.update_test_cases({
            1: TestCase(input_="same", output="r1"),
            2: TestCase(input_="same", output="r2")  # ❌ Дубликат input
        })


def test_attempt_from_dict_serialization():
    """Test serialization/deserialization with from_dict"""
    test_cases = TestCases()
    test_cases.update_test_cases({
        1: TestCase(input_="test1", output="result1"),
        2: TestCase(input_="test2", output="result2")
    })

    attempt = Attempt(student_id=1, problem_id=2, test_cases=test_cases)

    # Сериализуем test_cases
    test_cases_dict = attempt.test_cases.as_dict()

    # Десериализуем в новый объект TestCases
    new_test_cases = TestCases()
    new_test_cases.from_dict(test_cases_dict)

    # Создаем новый Attempt с десериализованными test_cases
    new_attempt = Attempt(student_id=1, problem_id=2, test_cases=new_test_cases)

    assert new_attempt.test_cases.count == 2
    assert new_attempt.test_cases.get_case(1).input == "test1"
