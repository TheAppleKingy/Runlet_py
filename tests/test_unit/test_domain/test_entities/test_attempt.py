import pytest
from datetime import datetime

from src.domain.entities import Problem, Attempt
from src.domain.value_objects import TestCase, TestCases, Examples
from src.domain.entities.exceptions import (
    AttemptAlreadyInProcessError,
    AlreadyPassedError,
)


class TestAttempt:
    """Тесты для класса Attempt"""

    @pytest.fixture
    def sample_problem(self):
        """Создает тестовую задачу с тест-кейсами"""
        test_cases = TestCases()
        test_cases.set_test_cases({
            1: TestCase(input="2 2", output="4"),
            2: TestCase(input="3 5", output="8"),
            3: TestCase(input="10 20", output="30"),
        })

        problem = Problem(
            name="Test Problem",
            module_id=1,
            description="Test description",
            auto_pass=False,
            show_test_cases=True,
            test_cases=test_cases,
            examples=Examples()
        )
        return problem

    @pytest.fixture
    def sample_attempt(self, sample_problem):
        """Создает тестовую попытку"""
        attempt = Attempt(
            user_id=123,
            problem_id=sample_problem.id,
            code="print('test')"
        )
        # Устанавливаем problem вручную (т.к. init=False)
        attempt.problem = sample_problem
        return attempt

    # ===== ТЕСТЫ ИНИЦИАЛИЗАЦИИ =====

    def test_attempt_creation(self):
        """Проверка создания объекта Attempt"""
        attempt = Attempt(
            user_id=42,
            problem_id=100,
            code="def solve(): pass"
        )

        assert attempt.user_id == 42
        assert attempt.problem_id == 100
        assert attempt.code == "def solve(): pass"
        assert attempt.amount == 0
        assert attempt.tests_passed is False
        assert attempt.confirmed_passed is False
        assert attempt.seen is False
        assert attempt.pending is False
        assert isinstance(attempt.updated_at, datetime)
        assert attempt.test_cases.count == 0

    def test_attempt_with_custom_values(self, sample_problem):
        """Проверка создания с кастомными значениями"""
        test_cases = TestCases()
        test_cases.set_test_cases({
            1: TestCase(input="1", output="2")
        })

        attempt = Attempt(
            user_id=42,
            problem_id=100,
            code="print('hello')"
        )
        attempt.problem = sample_problem
        attempt.test_cases = test_cases
        attempt.amount = 5
        attempt.tests_passed = True
        attempt.confirmed_passed = True
        attempt.seen = True
        attempt.pending = False

        assert attempt.user_id == 42
        assert attempt.problem_id == 100
        assert attempt.code == "print('hello')"
        assert attempt.amount == 5
        assert attempt.tests_passed is True
        assert attempt.confirmed_passed is True
        assert attempt.seen is True
        assert attempt.pending is False
        assert attempt.test_cases.count == 1

    # ===== ТЕСТЫ МЕТОДА start() =====

    def test_start_normal(self, sample_attempt):
        """Проверка обычного старта попытки"""
        initial_amount = sample_attempt.amount
        initial_updated_at = sample_attempt.updated_at

        sample_attempt.start()

        assert sample_attempt.pending is True
        assert sample_attempt.seen is False
        assert sample_attempt.amount == initial_amount + 1
        assert sample_attempt.updated_at > initial_updated_at

    def test_start_when_already_pending(self, sample_attempt):
        """Проверка старта когда уже в процессе"""
        sample_attempt.start()

        with pytest.raises(AttemptAlreadyInProcessError) as exc_info:
            sample_attempt.start()

        assert "Code is already testing now" in str(exc_info.value)

    def test_start_when_already_confirmed(self, sample_attempt):
        """Проверка старта когда уже подтверждено"""
        sample_attempt.confirmed_passed = True

        with pytest.raises(AlreadyPassedError) as exc_info:
            sample_attempt.start()

        assert "Attempt already confirmed by teacher" in str(exc_info.value)

    def test_start_multiple_times(self, sample_attempt):
        """Проверка множественных стартов (между которыми был stop)"""
        sample_attempt.start()
        assert sample_attempt.amount == 1

        sample_attempt.stop(sample_attempt.problem.test_cases)
        sample_attempt.start()
        assert sample_attempt.amount == 2

        sample_attempt.stop(sample_attempt.problem.test_cases)
        sample_attempt.start()
        assert sample_attempt.amount == 3

    # ===== ТЕСТЫ МЕТОДА stop() =====

    def test_stop_with_all_correct(self, sample_attempt, sample_problem):
        """Проверка остановки когда все тесты пройдены правильно"""
        sample_attempt.start()

        # Используем правильные тест-кейсы
        correct_results = sample_problem.test_cases
        sample_attempt.stop(correct_results)

        assert sample_attempt.pending is False
        assert sample_attempt.tests_passed is True
        assert sample_attempt.test_cases == correct_results
        assert sample_attempt.confirmed_passed is False  # auto_pass=False

    def test_stop_with_all_correct_and_auto_pass(self, sample_attempt, sample_problem):
        """Проверка остановки с auto_pass=True"""
        sample_problem.auto_pass = True
        sample_attempt.start()

        correct_results = sample_problem.test_cases
        sample_attempt.stop(correct_results)

        assert sample_attempt.tests_passed is True
        assert sample_attempt.confirmed_passed is True  # auto_pass=True

    def test_stop_with_incorrect_outputs(self, sample_attempt):
        """Проверка остановки когда есть неверные выводы"""
        sample_attempt.start()

        # Создаем результаты с ошибкой во втором тесте
        bad_results = TestCases()
        bad_results.set_test_cases({
            1: TestCase(input="2 2", output="4"),     # правильно
            2: TestCase(input="3 5", output="10"),    # неправильно
            3: TestCase(input="10 20", output="30"),  # правильно
        })

        sample_attempt.stop(bad_results)

        assert sample_attempt.tests_passed is False
        assert sample_attempt.confirmed_passed is False
        assert sample_attempt.test_cases == bad_results

    def test_stop_with_missing_test_nums(self, sample_attempt):
        """Проверка остановки когда не хватает тестов"""
        sample_attempt.start()

        # Только 2 теста из 3
        missing_results = TestCases()
        missing_results.set_test_cases({
            1: TestCase(input="2 2", output="4"),
            2: TestCase(input="3 5", output="8"),
        })

        sample_attempt.stop(missing_results)

        assert sample_attempt.tests_passed is False
        assert sample_attempt.test_cases.count == 2

    def test_stop_with_extra_test_nums(self, sample_attempt):
        """Проверка остановки когда есть лишние тесты"""
        sample_attempt.start()

        # 4 теста вместо 3
        extra_results = TestCases()
        extra_results.set_test_cases({
            1: TestCase(input="2 2", output="4"),
            2: TestCase(input="3 5", output="8"),
            3: TestCase(input="10 20", output="30"),
            4: TestCase(input="1 1", output="2"),
        })

        sample_attempt.stop(extra_results)

        assert sample_attempt.tests_passed is False
        assert sample_attempt.test_cases.count == 4

    def test_stop_with_different_test_nums(self, sample_attempt):
        """Проверка остановки когда номера тестов не совпадают"""
        sample_attempt.start()

        # Тесты с другими номерами
        different_nums = TestCases()
        different_nums.set_test_cases({
            1: TestCase(input="2 2", output="4"),
            3: TestCase(input="3 5", output="8"),
            5: TestCase(input="10 20", output="30"),
        })

        sample_attempt.stop(different_nums)

        assert sample_attempt.tests_passed is False
        assert sample_attempt.test_cases == different_nums

    def test_stop_with_mixed_errors(self, sample_attempt):
        """Проверка остановки со смешанными ошибками"""
        sample_attempt.start()

        # 1 - правильно, 2 - неверный вывод, 3 - нет, 4 - лишний
        mixed_results = TestCases()
        mixed_results.set_test_cases({
            1: TestCase(input="2 2", output="4"),     # правильно
            2: TestCase(input="3 5", output="100"),   # неверный вывод
            4: TestCase(input="7 8", output="15"),    # лишний тест
        })

        sample_attempt.stop(mixed_results)

        assert sample_attempt.tests_passed is False

    def test_stop_updates_timestamp(self, sample_attempt):
        """Проверка что при остановке обновляется время"""
        sample_attempt.start()
        initial_updated_at = sample_attempt.updated_at

        import time
        time.sleep(0.01)  # небольшая задержка

        sample_attempt.stop(sample_attempt.problem.test_cases)

        assert sample_attempt.updated_at > initial_updated_at

    def test_stop_clears_pending(self, sample_attempt):
        """Проверка что при остановке сбрасывается флаг pending"""
        sample_attempt.start()
        assert sample_attempt.pending is True

        sample_attempt.stop(sample_attempt.problem.test_cases)

        assert sample_attempt.pending is False

    def test_stop_without_start(self, sample_attempt):
        """Проверка остановки без предварительного старта"""
        # По логике должно работать, просто обновляет результаты
        results = sample_attempt.problem.test_cases
        sample_attempt.stop(results)

        assert sample_attempt.pending is False
        assert sample_attempt.test_cases == results

    # ===== ТЕСТЫ ВЗАИМОДЕЙСТВИЯ start() И stop() =====

    def test_full_cycle_correct(self, sample_attempt):
        """Полный цикл: старт -> стоп с правильными ответами"""
        sample_attempt.start()
        assert sample_attempt.pending is True
        assert sample_attempt.tests_passed is False

        sample_attempt.stop(sample_attempt.problem.test_cases)

        assert sample_attempt.pending is False
        assert sample_attempt.tests_passed is True
        assert sample_attempt.amount == 1

    def test_full_cycle_incorrect(self, sample_attempt):
        """Полный цикл: старт -> стоп с неправильными ответами"""
        sample_attempt.start()

        bad_results = TestCases()
        bad_results.set_test_cases({
            1: TestCase(input="2 2", output="4"),
            2: TestCase(input="3 5", output="WRONG"),
            3: TestCase(input="10 20", output="30"),
        })

        sample_attempt.stop(bad_results)

        assert sample_attempt.pending is False
        assert sample_attempt.tests_passed is False
        assert sample_attempt.amount == 1

    def test_multiple_cycles(self, sample_attempt):
        """Несколько циклов старт-стоп"""
        for i in range(3):
            sample_attempt.start()
            assert sample_attempt.amount == i + 1
            assert sample_attempt.pending is True

            # Чередуем правильные/неправильные ответы
            if i % 2 == 0:
                sample_attempt.stop(sample_attempt.problem.test_cases)
                assert sample_attempt.tests_passed is True
            else:
                bad_results = TestCases()
                bad_results.set_test_cases({
                    1: TestCase(input="2 2", output="4"),
                    2: TestCase(input="3 5", output="WRONG"),
                    3: TestCase(input="10 20", output="30"),
                })
                sample_attempt.stop(bad_results)
                assert sample_attempt.tests_passed is False

            assert sample_attempt.pending is False

    # ===== ТЕСТЫ НА ГРАНИЧНЫЕ СЛУЧАИ =====

    def test_stop_with_empty_test_cases(self, sample_attempt):
        """Остановка с пустыми тест-кейсами"""
        sample_attempt.start()

        empty_results = TestCases()
        sample_attempt.stop(empty_results)

        assert sample_attempt.tests_passed is False
        assert sample_attempt.test_cases.count == 0

    def test_stop_when_problem_has_no_test_cases(self, sample_attempt):
        """Остановка когда у задачи нет тест-кейсов"""
        sample_attempt.problem.test_cases = TestCases()
        sample_attempt.start()

        results = TestCases()
        results.set_test_cases({
            1: TestCase(input="1", output="2")
        })

        sample_attempt.stop(results)

        # Так как у проблемы нет тестов, любой результат считается неправильным
        assert sample_attempt.tests_passed is False

    def test_start_after_successful_stop(self, sample_attempt):
        """Старт после успешной остановки"""
        sample_attempt.start()
        sample_attempt.stop(sample_attempt.problem.test_cases)
        assert sample_attempt.tests_passed is True

        # Можно стартовать после успеха
        sample_attempt.start()
        assert sample_attempt.pending is True
        assert sample_attempt.amount == 2

    def test_start_after_failed_stop(self, sample_attempt):
        """Старт после неудачной остановки"""
        sample_attempt.start()

        bad_results = TestCases()
        bad_results.set_test_cases({
            1: TestCase(input="2 2", output="WRONG"),
        })
        sample_attempt.stop(bad_results)
        assert sample_attempt.tests_passed is False

        # Должен иметь возможность исправить
        sample_attempt.start()
        assert sample_attempt.pending is True
        assert sample_attempt.amount == 2

    def test_amount_increment_after_multiple_starts(self, sample_attempt):
        """Проверка инкремента amount при множественных стартах"""
        for i in range(5):
            sample_attempt.start()
            assert sample_attempt.amount == i + 1
            sample_attempt.stop(sample_attempt.problem.test_cases)

    def test_seen_flag_behavior(self, sample_attempt):
        """Проверка поведения флага seen"""
        assert sample_attempt.seen is False

        sample_attempt.start()
        assert sample_attempt.seen is False  # seen не меняется при старте

        sample_attempt.stop(sample_attempt.problem.test_cases)
        assert sample_attempt.seen is False  # seen не меняется при стопе

        # seen должен управляться извне (учитель пометил как просмотренное)
        sample_attempt.seen = True
        assert sample_attempt.seen is True

    def test_tests_passed_with_equal_but_different_order(self, sample_attempt):
        """Тесты пройдены, если результаты совпадают (порядок не важен)"""
        sample_attempt.start()

        # Те же тесты, но в другом порядке (по номерам)
        reordered = TestCases()
        reordered.set_test_cases({
            3: TestCase(input="10 20", output="30"),
            1: TestCase(input="2 2", output="4"),
            2: TestCase(input="3 5", output="8"),
        })

        sample_attempt.stop(reordered)

        # Должно быть True, так как содержимое то же
        assert sample_attempt.tests_passed is True

    def test_confirmed_passed_only_with_auto_pass(self, sample_attempt):
        """confirmed_passed должно устанавливаться только при auto_pass=True"""
        sample_attempt.start()
        sample_attempt.stop(sample_attempt.problem.test_cases)
        assert sample_attempt.confirmed_passed is False

        sample_attempt.problem.auto_pass = True
        sample_attempt.start()
        sample_attempt.stop(sample_attempt.problem.test_cases)
        assert sample_attempt.confirmed_passed is True
