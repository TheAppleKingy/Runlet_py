import pytest

from src.domain.entities import Attempt, Problem
from src.domain.value_objects import TestCase, TestCases
from src.domain.entities.exceptions import MismatchTestNumsError, MismatchTestOutputsError, MismatchTestsCountError


@pytest.fixture
def problem_with_cases():
    """
    Problem с тремя корректными тестами:
    1 -> (in1, out1)
    2 -> (in2, out2)
    3 -> (in3, out3)
    """
    data = {
        1: TestCase(input="in1", output="out1"),
        2: TestCase(input="in2", output="out2"),
        3: TestCase(input="in3", output="out3"),
    }
    tc = TestCases(_data=data)
    problem = Problem(name="p1", description="desc", module_id=1, test_cases=tc)
    return problem


def make_attempt(user_id: int, problem: Problem, provided_data: dict[int, tuple[str, str]]):
    """
    Утилита для создания Attempt с заданными результатами пользователя.
    provided_data: {num: (input, output)}
    """
    attempt_cases = {
        num: TestCase(input=inp, output=out)
        for num, (inp, out) in provided_data.items()
    }
    attempt_tc = TestCases(_data=attempt_cases)
    attempt = Attempt(user_id=user_id, problem_id=problem.id)
    attempt.problem = problem
    attempt.test_cases = attempt_tc
    return attempt


def test_mark_as_passed_success(problem_with_cases):
    """
    Все номера и outputs совпадают — попытка помечается как passed=True.
    """
    provided = {
        1: ("in1", "out1"),
        2: ("in2", "out2"),
        3: ("in3", "out3"),
    }
    attempt = make_attempt(user_id=10, problem=problem_with_cases, provided_data=provided)

    attempt.mark_as_passed()

    assert attempt.passed is True


def test_mark_as_passed_mismatch_count(problem_with_cases):
    """
    Кол-во результатов не совпадает с кол-вом тестов в задаче -> MismatchTestsCountError.
    """
    provided = {
        1: ("in1", "out1"),
        2: ("in2", "out2"),
        # третий тест не передан
    }
    attempt = make_attempt(user_id=10, problem=problem_with_cases, provided_data=provided)

    with pytest.raises(MismatchTestsCountError):
        attempt.mark_as_passed()


def test_mark_as_passed_mismatching_outputs(problem_with_cases):
    """
    Номера есть, но хотя бы один output отличается -> MismatchTestOutputsError.
    """
    provided = {
        1: ("in1", "WRONG"),
        2: ("in2", "out2"),
        3: ("in3", "out3"),
    }
    attempt = make_attempt(user_id=10, problem=problem_with_cases, provided_data=provided)

    with pytest.raises(MismatchTestOutputsError) as exc:
        attempt.mark_as_passed()

    # опционально проверяем, что номер неправильного теста указан в сообщении
    assert "1" in str(exc.value)


def test_mark_as_passed_mismatching_nums(problem_with_cases):
    """
    Переданы результаты по несуществующему номеру теста -> MismatchTestNumsError.
    В твоей реализации это случится, когда get_case(num) вернул None.
    """
    provided = {
        1: ("in1", "out1"),
        2: ("in2", "out2"),
        999: ("inX", "outX"),  # в problem нет такого номера
    }
    attempt = make_attempt(user_id=10, problem=problem_with_cases, provided_data=provided)

    with pytest.raises(MismatchTestNumsError) as exc:
        attempt.mark_as_passed()

    assert "999" in str(exc.value)


def test_mark_as_passed_not_marked_on_error(problem_with_cases):
    """
    При любой ошибке passed должен остаться False.
    """
    provided = {
        1: ("in1", "WRONG"),
        2: ("in2", "out2"),
        3: ("in3", "out3"),
    }
    attempt = make_attempt(user_id=10, problem=problem_with_cases, provided_data=provided)

    with pytest.raises(MismatchTestOutputsError):
        attempt.mark_as_passed()

    assert attempt.passed is False
