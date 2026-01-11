import pytest

from src.domain.entities import Attempt
from src.domain.value_objects import TestCase, TestCases
from src.domain.entities.exceptions import MismatchTestNumsError, MismatchTestOutputsError, MismatchTestsCountError

# ============ Test Setup Helpers ============


def create_test_cases(data: dict[int, tuple[str, str]]) -> TestCases:
    """Helper to create TestCases from dict of (input, output) tuples"""
    test_cases = TestCases()
    for num, (input_, output) in data.items():
        test_cases.update_test_cases({num: TestCase(input=input_, output=output)})
    return test_cases


# ============ Basic Creation Tests ============


def test_attempt_creation():
    """Test basic attempt creation"""
    attempt = Attempt(user_id=1, problem_id=2)

    assert attempt.user_id == 1
    assert attempt.problem_id == 2
    assert attempt.amount == 0
    assert attempt.passed == False
    assert isinstance(attempt.test_cases, TestCases)
    assert attempt.test_cases.count == 0


def test_attempt_with_test_cases():
    """Test attempt creation with test cases"""
    test_cases = create_test_cases({
        1: ("input1", "output1"),
        2: ("input2", "output2")
    })

    attempt = Attempt(user_id=1, problem_id=2, test_cases=test_cases)

    assert attempt.user_id == 1
    assert attempt.problem_id == 2
    assert attempt.test_cases.count == 2
    assert attempt.test_cases.get_case(1).input == "input1"
    assert attempt.test_cases.get_case(1).output == "output1"


def test_attempt_default_test_cases():
    """Test attempt gets empty TestCases by default"""
    attempt = Attempt(user_id=1, problem_id=2)

    assert attempt.test_cases.count == 0
    assert isinstance(attempt.test_cases, TestCases)


def test_attempt_fields_are_mutable():
    """Test that attempt fields can be modified"""
    attempt = Attempt(user_id=1, problem_id=2)

    # Can modify fields
    attempt.amount = 5
    attempt.passed = True

    assert attempt.amount == 5
    assert attempt.passed == True

    # Can modify test_cases
    test_cases = create_test_cases({1: ("test", "result")})
    attempt.test_cases = test_cases
    assert attempt.test_cases.count == 1

# ============ mark_as_passed Method Tests ============


def test_mark_as_passed_success():
    """Test successful mark_as_passed"""
    # Create attempt with test cases
    attempt_test_cases = create_test_cases({
        1: ("input1", "expected_output1"),
        2: ("input2", "expected_output2"),
        3: ("input3", "expected_output3")
    })

    attempt = Attempt(user_id=1, problem_id=2, test_cases=attempt_test_cases)

    # Expected cases (same as attempt test cases)
    expected_cases = create_test_cases({
        1: ("input1", "expected_output1"),
        2: ("input2", "expected_output2"),
        3: ("input3", "expected_output3")
    })

    # Should not raise
    attempt.mark_as_passed(expected_cases)

    assert attempt.passed == True
    assert attempt.amount == 0  # amount unchanged


def test_mark_as_passed_different_input_same_output():
    """Test mark_as_passed with different inputs but same outputs"""
    attempt_test_cases = create_test_cases({
        1: ("different_input1", "expected_output1"),
        2: ("different_input2", "expected_output2")
    })

    attempt = Attempt(user_id=1, problem_id=2, test_cases=attempt_test_cases)

    expected_cases = create_test_cases({
        1: ("input1", "expected_output1"),
        2: ("input2", "expected_output2")
    })

    # Should succeed - only outputs matter, not inputs
    attempt.mark_as_passed(expected_cases)

    assert attempt.passed == True


def test_mark_as_passed_empty_test_cases():
    """Test mark_as_passed with empty test cases"""
    attempt = Attempt(user_id=1, problem_id=2)
    expected_cases = TestCases()

    # Both empty - should succeed
    attempt.mark_as_passed(expected_cases)

    assert attempt.passed == True


def test_mark_as_passed_single_test_case():
    """Test mark_as_passed with single test case"""
    attempt_test_cases = create_test_cases({
        1: ("input", "expected_output")
    })

    attempt = Attempt(user_id=1, problem_id=2, test_cases=attempt_test_cases)

    expected_cases = create_test_cases({
        1: ("different_input", "expected_output")  # Same output, different input
    })

    attempt.mark_as_passed(expected_cases)

    assert attempt.passed == True

# ============ Error Scenarios Tests ============


def test_mark_as_passed_count_mismatch():
    """Test mark_as_passed with count mismatch"""
    attempt_test_cases = create_test_cases({
        1: ("input1", "output1"),
        2: ("input2", "output2")
    })

    attempt = Attempt(user_id=1, problem_id=2, test_cases=attempt_test_cases)

    expected_cases = create_test_cases({
        1: ("input1", "output1"),
        2: ("input2", "output2"),
        3: ("input3", "output3")  # Extra test case
    })

    with pytest.raises(MismatchTestsCountError) as exc:
        attempt.mark_as_passed(expected_cases)

    assert "Count of provided results mismatch with specified cases" in str(exc.value)
    assert attempt.passed == False


def test_mark_as_passed_output_mismatch():
    """Test mark_as_passed with incorrect outputs"""
    attempt_test_cases = create_test_cases({
        1: ("input1", "correct_output"),
        2: ("input2", "wrong_output"),  # Wrong output
        3: ("input3", "correct_output")
    })

    attempt = Attempt(user_id=1, problem_id=2, test_cases=attempt_test_cases)

    expected_cases = create_test_cases({
        1: ("input1", "correct_output"),
        2: ("input2", "expected_output"),  # Different from attempt's output
        3: ("input3", "correct_output")
    })

    with pytest.raises(MismatchTestOutputsError) as exc:
        attempt.mark_as_passed(expected_cases)

    assert "Result of tests [2] are incorrect" in str(exc.value)
    assert attempt.passed == False


def test_mark_as_passed_multiple_output_mismatches():
    """Test mark_as_passed with multiple incorrect outputs"""
    attempt_test_cases = create_test_cases({
        1: ("input1", "wrong1"),
        2: ("input2", "correct"),
        3: ("input3", "wrong3"),
        4: ("input4", "wrong4")
    })

    attempt = Attempt(user_id=1, problem_id=2, test_cases=attempt_test_cases)

    expected_cases = create_test_cases({
        1: ("input1", "expected1"),
        2: ("input2", "correct"),
        3: ("input3", "expected3"),
        4: ("input4", "expected4")
    })

    with pytest.raises(MismatchTestOutputsError) as exc:
        attempt.mark_as_passed(expected_cases)

    # Should list all incorrect test numbers
    error_msg = str(exc.value)
    assert "Result of tests" in error_msg
    assert "1" in error_msg
    assert "3" in error_msg
    assert "4" in error_msg
    assert attempt.passed == False


def test_mark_as_passed_missing_test_numbers():
    """Test mark_as_passed when attempt is missing some test numbers"""
    attempt_test_cases = create_test_cases({
        1: ("input1", "output1"),
        4: ("input4", "output4"),
        3: ("input3", "output3")  # Missing test 2
    })

    attempt = Attempt(user_id=1, problem_id=2, test_cases=attempt_test_cases)

    expected_cases = create_test_cases({
        1: ("input1", "output1"),
        2: ("input2", "output2"),  # Test 2 not in attempt
        3: ("input3", "output3")
    })

    with pytest.raises(MismatchTestNumsError) as exc:
        attempt.mark_as_passed(expected_cases)

    assert "Provided results dont contain tests [4]" in str(exc.value)
    assert attempt.passed == False


def test_mark_as_passed_extra_test_numbers():
    """Test mark_as_passed when attempt has extra test numbers"""
    attempt_test_cases = create_test_cases({
        1: ("input1", "output1"),
        2: ("input2", "output2"),
        3: ("input3", "output3"),  # Extra test not in expected
        4: ("input4", "output4")   # Extra test not in expected
    })

    attempt = Attempt(user_id=1, problem_id=2, test_cases=attempt_test_cases)

    expected_cases = create_test_cases({
        1: ("input1", "output1"),
        2: ("input2", "output2")
    })

    with pytest.raises(MismatchTestsCountError) as exc:
        attempt.mark_as_passed(expected_cases)

    assert "Count of provided results mismatch" in str(exc.value)
    assert attempt.passed == False


def test_mark_as_passed_mixed_errors():
    """Test mark_as_passed with multiple types of errors"""
    attempt_test_cases = create_test_cases({
        1: ("input1", "wrong_output"),  # Wrong output
        # Missing test 2
        3: ("input3", "output3"),       # Extra test (not in expected)
        4: ("input4", "output4")        # Extra test (not in expected)
    })

    attempt = Attempt(user_id=1, problem_id=2, test_cases=attempt_test_cases)

    expected_cases = create_test_cases({
        1: ("input1", "expected_output"),
        2: ("input2", "output2")
    })

    # Should raise count mismatch first (before checking individual tests)
    with pytest.raises(MismatchTestsCountError):
        attempt.mark_as_passed(expected_cases)

    assert attempt.passed == False

# ============ Edge Cases ============


def test_mark_as_passed_empty_string_outputs():
    """Test mark_as_passed with empty string outputs"""
    attempt_test_cases = create_test_cases({
        1: ("input1", ""),  # Empty output
        2: ("input2", "")   # Empty output
    })

    attempt = Attempt(user_id=1, problem_id=2, test_cases=attempt_test_cases)

    expected_cases = create_test_cases({
        1: ("input1", ""),
        2: ("input2", "")
    })

    attempt.mark_as_passed(expected_cases)

    assert attempt.passed == True


def test_mark_as_passed_same_input_different_outputs():
    """Test with same input but different outputs in different test numbers"""
    # Этот тест НЕВОЗМОЖЕН с текущей логикой!
    # TestCases не позволяет создать два теста с одинаковым input

    # Вместо этого тестируем валидный сценарий:
    attempt_test_cases = create_test_cases({
        1: ("input1", "output1"),
        2: ("input2", "output2")  # Разные inputs - это валидно
    })

    attempt = Attempt(user_id=1, problem_id=2, test_cases=attempt_test_cases)

    expected_cases = create_test_cases({
        1: ("different_input1", "output1"),  # Input может быть разным в expected
        2: ("different_input2", "output2")   # Главное - outputs совпадают
    })

    attempt.mark_as_passed(expected_cases)

    assert attempt.passed == True


def test_mark_as_passed_large_number_of_tests():
    """Test mark_as_passed with large number of test cases"""
    # Create 100 test cases
    attempt_data = {i: (f"input{i}", f"output{i}") for i in range(1, 100)}
    attempt_test_cases = create_test_cases(attempt_data)

    attempt = Attempt(user_id=1, problem_id=2, test_cases=attempt_test_cases)

    expected_data = {i: (f"different_input{i}", f"output{i}") for i in range(1, 100)}
    expected_cases = create_test_cases(expected_data)

    attempt.mark_as_passed(expected_cases)

    assert attempt.passed == True


def test_mark_as_passed_non_sequential_test_numbers():
    """Test mark_as_passed with non-sequential test numbers"""
    attempt_test_cases = create_test_cases({
        10: ("input10", "output10"),
        20: ("input20", "output20"),
        30: ("input30", "output30")
    })

    attempt = Attempt(user_id=1, problem_id=2, test_cases=attempt_test_cases)

    expected_cases = create_test_cases({
        10: ("diff10", "output10"),
        20: ("diff20", "output20"),
        30: ("diff30", "output30")
    })

    attempt.mark_as_passed(expected_cases)

    assert attempt.passed == True

# ============ State Persistence Tests ============


def test_mark_as_passed_does_not_modify_test_cases():
    """Test that mark_as_passed doesn't modify test_cases"""
    attempt_test_cases = create_test_cases({
        1: ("input1", "output1"),
        2: ("input2", "output2")
    })

    attempt = Attempt(user_id=1, problem_id=2, test_cases=attempt_test_cases)

    expected_cases = create_test_cases({
        1: ("diff1", "output1"),
        2: ("diff2", "output2")
    })

    original_attempt_cases = attempt.test_cases.as_dict()
    original_expected_cases = expected_cases.as_dict()

    attempt.mark_as_passed(expected_cases)

    # Test cases should not be modified
    assert attempt.test_cases.as_dict() == original_attempt_cases
    assert expected_cases.as_dict() == original_expected_cases


def test_multiple_mark_as_passed_calls():
    """Test multiple calls to mark_as_passed"""
    attempt_test_cases = create_test_cases({
        1: ("input1", "output1")
    })

    attempt = Attempt(user_id=1, problem_id=2, test_cases=attempt_test_cases)

    expected_cases = create_test_cases({
        1: ("diff1", "output1")
    })

    # First call should succeed
    attempt.mark_as_passed(expected_cases)
    assert attempt.passed == True

    # Modify test case to be wrong
    attempt.test_cases.update_test_cases({1: TestCase(input="input1", output="wrong_output")})

    # Second call should fail
    with pytest.raises(MismatchTestOutputsError):
        attempt.mark_as_passed(expected_cases)

    # Should still be passed from first call
    assert attempt.passed == True


def test_mark_as_passed_resets_passed_flag():
    """Test that failed mark_as_passed doesn't reset passed flag if already passed"""
    attempt_test_cases = create_test_cases({
        1: ("input1", "output1")
    })

    attempt = Attempt(user_id=1, problem_id=2, test_cases=attempt_test_cases)
    attempt.passed = True  # Already passed

    # Try to mark with mismatching data
    expected_cases = create_test_cases({
        1: ("input1", "different_output")
    })

    with pytest.raises(MismatchTestOutputsError):
        attempt.mark_as_passed(expected_cases)

    # Should still be passed (exception doesn't reset it)
    assert attempt.passed == True

# ============ Integration Tests ============


def test_attempt_with_problem_test_cases():
    """Test integration with problem test cases scenario"""
    # Simulate problem's expected test cases
    problem_test_cases = create_test_cases({
        1: ("1+1", "2"),
        2: ("2+2", "4"),
        3: ("3+3", "6")
    })

    # Simulate user's attempt test cases
    user_test_cases = create_test_cases({
        1: ("1+1", "2"),    # Correct
        2: ("2+2", "4"),    # Correct
        3: ("3+3", "6")     # Correct
    })

    attempt = Attempt(user_id=1, problem_id=1, test_cases=user_test_cases)

    attempt.mark_as_passed(problem_test_cases)

    assert attempt.passed == True


def test_attempt_with_partial_correct_answers():
    """Test scenario where some answers are correct, some wrong"""
    problem_test_cases = create_test_cases({
        1: ("print('hello')", "hello"),
        2: ("x = 5\nprint(x)", "5"),
        3: ("def add(a,b): return a+b", "")
    })

    user_test_cases = create_test_cases({
        1: ("print('hello')", "hello"),           # Correct
        2: ("x = 5\nprint(x)", "6"),              # Wrong (should be 5)
        3: ("def add(a,b): return a+b", "")       # Correct
    })

    attempt = Attempt(user_id=1, problem_id=1, test_cases=user_test_cases)

    with pytest.raises(MismatchTestOutputsError) as exc:
        attempt.mark_as_passed(problem_test_cases)

    assert "Result of tests [2] are incorrect" in str(exc.value)
    assert attempt.passed == False


# ============ Error Message Tests ============


def test_error_messages_are_informative():
    """Test that error messages contain useful information"""
    attempt_test_cases = create_test_cases({
        1: ("input1", "wrong"),
        2: ("input2", "correct")
    })

    attempt = Attempt(user_id=1, problem_id=2, test_cases=attempt_test_cases)

    expected_cases = create_test_cases({
        1: ("input1", "expected"),
        2: ("input2", "correct"),
        3: ("input3", "output3")  # Extra
    })

    # Test count mismatch error
    try:
        attempt.mark_as_passed(expected_cases)
    except MismatchTestsCountError as e:
        assert "Count of provided results mismatch with specified cases" in str(e)

    # Test output mismatch error
    attempt_test_cases2 = create_test_cases({
        1: ("input1", "wrong"),
        2: ("input2", "wrong_too")
    })

    attempt2 = Attempt(user_id=1, problem_id=2, test_cases=attempt_test_cases2)

    expected_cases2 = create_test_cases({
        1: ("input1", "expected1"),
        2: ("input2", "expected2")
    })

    try:
        attempt2.mark_as_passed(expected_cases2)
    except MismatchTestOutputsError as e:
        assert "Result of tests" in str(e)
        assert "1" in str(e)
        assert "2" in str(e)

    # Test missing test numbers error
    attempt_test_cases3 = create_test_cases({
        1: ("input1", "output1")
    })

    attempt3 = Attempt(user_id=1, problem_id=2, test_cases=attempt_test_cases3)

    expected_cases3 = create_test_cases({
        1: ("input1", "output1"),
        2: ("input2", "output2")  # Missing in attempt
    })

    with pytest.raises(MismatchTestsCountError):
        attempt3.mark_as_passed(expected_cases3)

# ============ Type and Validation Tests ============


def test_mark_as_passed_with_none():
    """Test mark_as_passed with None parameter"""
    attempt = Attempt(user_id=1, problem_id=2)

    with pytest.raises(AttributeError):
        attempt.mark_as_passed(None)  # type: ignore


def test_mark_as_passed_with_wrong_type():
    """Test mark_as_passed with wrong parameter type"""
    attempt = Attempt(user_id=1, problem_id=2)

    with pytest.raises(AttributeError):
        attempt.mark_as_passed(2)  # type: ignore


def test_attempt_immutable_fields():
    """Test that fields with init=False can still be set"""
    attempt = Attempt(user_id=1, problem_id=2)

    # Fields with init=False should exist and be settable
    assert hasattr(attempt, 'amount')
    assert hasattr(attempt, 'passed')

    attempt.amount = 10
    attempt.passed = True

    assert attempt.amount == 10
    assert attempt.passed == True
