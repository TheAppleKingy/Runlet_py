import pytest

from src.domain.entities import Attempt, TestCases, TestCase
from src.domain.exceptions.entities import MismatchTestNumsError, MismatchTestOutputsError, MismatchTestsCountError


def test_attempt_initialization():
    """Test Attempt initialization"""
    attempt = Attempt(student_id=123, problem_id=456)
    assert attempt.student_id == 123
    assert attempt.problem_id == 456
    assert attempt.amount == 0
    assert attempt.passed is False
    assert attempt._test_cases_data == {}
    assert attempt._result_cases_data == {}


def test_attempt_test_cases_property_setter():
    """Test test_cases property setter"""
    attempt = Attempt(student_id=1, problem_id=1)

    test_cases = TestCases(_data={
        1: TestCase(input="t1", output="r1"),
        2: TestCase(input="t2", output="r2")
    })

    attempt.test_cases = test_cases
    assert attempt.test_cases.count == 2
    assert attempt._test_cases_data == test_cases.as_dict()


def test_attempt_test_cases_property_getter():
    """Test test_cases property getter"""
    attempt = Attempt(student_id=1, problem_id=1)

    test_cases = TestCases(_data={
        1: TestCase(input="input1", output="output1")
    })

    attempt.test_cases = test_cases
    retrieved = attempt.test_cases
    assert isinstance(retrieved, TestCases)
    assert retrieved.count == 1
    assert retrieved.get_case(1).input == "input1"


def test_attempt_result_cases_property_valid():
    """Test result_cases property with valid data"""
    attempt = Attempt(student_id=1, problem_id=1)

    # Set test cases first
    test_cases = TestCases(_data={
        1: TestCase(input="t1", output="r1"),
        2: TestCase(input="t2", output="r2")
    })
    attempt.test_cases = test_cases

    # Set matching result cases
    result_cases = TestCases(_data={
        1: TestCase(input="t1", output="r1"),
        2: TestCase(input="t2", output="r2")
    })

    attempt.result_cases = result_cases
    assert attempt.result_cases.count == 2
    assert attempt._result_cases_data == result_cases.as_dict()


def test_attempt_result_cases_mismatch_count():
    """Test result_cases with mismatched count"""
    attempt = Attempt(student_id=1, problem_id=1)

    test_cases = TestCases(_data={
        1: TestCase(input="t1", output="r1"),
        2: TestCase(input="t2", output="r2")
    })
    attempt.test_cases = test_cases

    result_cases = TestCases(_data={
        1: TestCase(input="t1", output="r1")
        # Missing second test case
    })

    with pytest.raises(MismatchTestsCountError) as exc_info:
        attempt.result_cases = result_cases
    assert "Count of provided results mismatch with spcified cases" in str(exc_info.value)


def test_attempt_result_cases_excess_count():
    """Test result_cases with too many results"""
    attempt = Attempt(student_id=1, problem_id=1)

    test_cases = TestCases(_data={
        1: TestCase(input="t1", output="r1")
    })
    attempt.test_cases = test_cases

    result_cases = TestCases(_data={
        1: TestCase(input="t1", output="r1"),
        2: TestCase(input="t2", output="r2")  # Extra result
    })

    with pytest.raises(MismatchTestsCountError):
        attempt.result_cases = result_cases


def test_attempt_result_cases_mismatch_nums():
    """Test result_cases with mismatched test numbers"""
    attempt = Attempt(student_id=1, problem_id=1)

    test_cases = TestCases(_data={
        1: TestCase(input="t1", output="r1"),
        2: TestCase(input="t2", output="r2")
    })
    attempt.test_cases = test_cases

    result_cases = TestCases(_data={
        1: TestCase(input="t1", output="r1"),
        3: TestCase(input="t3", output="r3")  # Wrong test number
    })

    with pytest.raises(MismatchTestNumsError) as exc_info:
        attempt.result_cases = result_cases
    assert "Provided result test num 3 does not exist" in str(exc_info.value)


def test_attempt_result_cases_before_test_cases():
    """Test setting result cases before test cases"""
    attempt = Attempt(student_id=1, problem_id=1)

    result_cases = TestCases(_data={
        1: TestCase(input="t1", output="r1")
    })

    # Should raise error because test_cases.count is 0
    with pytest.raises(MismatchTestsCountError):
        attempt.result_cases = result_cases


def test_attempt_mark_as_passed_success():
    """Test successful mark_as_passed"""
    attempt = Attempt(student_id=100, problem_id=200)

    # Set test cases
    test_cases = TestCases(_data={
        1: TestCase(input="1+1", output="2"),
        2: TestCase(input="2*2", output="4"),
        3: TestCase(input="10/2", output="5")
    })
    attempt.test_cases = test_cases

    # Set matching result cases
    result_cases = TestCases(_data={
        1: TestCase(input="1+1", output="2"),
        2: TestCase(input="2*2", output="4"),
        3: TestCase(input="10/2", output="5")
    })
    attempt.result_cases = result_cases

    # Mark as passed
    attempt.mark_as_passed()

    assert attempt.passed is True
    assert attempt.student_id == 100
    assert attempt.problem_id == 200


def test_attempt_mark_as_passed_unexistent_result_case():
    """Test mark_as_passed with no test cases"""
    attempt = Attempt(student_id=1, problem_id=1)
    attempt.test_cases = TestCases({
        1: TestCase(input="t1", output="r1")
    }
    )

    result_cases = TestCases(_data={
        1: TestCase(input="t1", output="r1")
    })
    attempt.result_cases = result_cases
    attempt.result_cases.update_test_cases({2: TestCase(input="t2", output="r2")})
    with pytest.raises(MismatchTestsCountError):
        attempt.mark_as_passed()


def test_attempt_mark_as_passed_no_result_cases():
    """Test mark_as_passed with no result cases"""
    attempt = Attempt(student_id=1, problem_id=1)

    test_cases = TestCases(_data={
        1: TestCase(input="t1", output="r1")
    })
    attempt.test_cases = test_cases

    # No result cases set
    with pytest.raises(MismatchTestsCountError):
        attempt.mark_as_passed()


def test_attempt_mark_as_passed_empty_test_cases():
    """Test mark_as_passed with empty test cases"""
    attempt = Attempt(student_id=1, problem_id=1)

    test_cases = TestCases(_data={})
    attempt.test_cases = test_cases

    result_cases = TestCases(_data={})
    attempt.result_cases = result_cases

    attempt.mark_as_passed()
    assert attempt.passed


def test_attempt_mark_as_passed_mismatching_output():
    """Test mark_as_passed with mismatching output"""
    attempt = Attempt(student_id=1, problem_id=1)

    test_cases = TestCases(_data={
        1: TestCase(input="1+1", output="2"),
        2: TestCase(input="2*2", output="4")
    })
    attempt.test_cases = test_cases

    result_cases = TestCases(_data={
        1: TestCase(input="1+1", output="2"),
        2: TestCase(input="2*2", output="5")  # Wrong output
    })
    attempt.result_cases = result_cases

    with pytest.raises(MismatchTestOutputsError) as exc_info:
        attempt.mark_as_passed()
    assert "Result of tests [2] are incorrect" in str(exc_info.value)


def test_attempt_mark_as_passed_multiple_mismatching_outputs():
    """Test mark_as_passed with multiple mismatching outputs"""
    attempt = Attempt(student_id=1, problem_id=1)

    test_cases = TestCases(_data={
        1: TestCase(input="a", output="A"),
        2: TestCase(input="b", output="B"),
        3: TestCase(input="c", output="C"),
        4: TestCase(input="d", output="D")
    })
    attempt.test_cases = test_cases

    result_cases = TestCases(_data={
        1: TestCase(input="a", output="A"),  # Correct
        2: TestCase(input="b", output="X"),  # Wrong
        3: TestCase(input="c", output="C"),  # Correct
        4: TestCase(input="d", output="Y")   # Wrong
    })
    attempt.result_cases = result_cases

    with pytest.raises(MismatchTestOutputsError) as exc_info:
        attempt.mark_as_passed()
    error_msg = str(exc_info.value)
    assert "Result of tests" in error_msg
    assert "2" in error_msg
    assert "4" in error_msg


def test_attempt_mark_as_passed_missing_test_num():
    """Test mark_as_passed with missing test number in results"""
    attempt = Attempt(student_id=1, problem_id=1)

    test_cases = TestCases(_data={
        1: TestCase(input="t1", output="r1"),
        2: TestCase(input="t2", output="r2")
    })
    attempt.test_cases = test_cases

    result_cases = TestCases(_data={
        1: TestCase(input="t1", output="r1")
        # Missing test 2
    })

    # Set result_cases should fail due to count mismatch
    with pytest.raises(MismatchTestsCountError):
        attempt.result_cases = result_cases


def test_attempt_mark_as_passed_extra_test_num():
    """Test mark_as_passed with extra test number in results"""
    attempt = Attempt(student_id=1, problem_id=1)

    test_cases = TestCases(_data={
        1: TestCase(input="t1", output="r1")
    })
    attempt.test_cases = test_cases

    result_cases = TestCases(_data={
        1: TestCase(input="t1", output="r1"),
        2: TestCase(input="t2", output="r2")  # Extra test
    })

    # Set result_cases should fail due to count mismatch
    with pytest.raises(MismatchTestsCountError):
        attempt.result_cases = result_cases


def test_attempt_mark_as_passed_wrong_test_num_in_middle():
    """Test mark_as_passed with wrong test number discovered during validation"""
    attempt = Attempt(student_id=1, problem_id=1)

    test_cases = TestCases(_data={
        1: TestCase(input="t1", output="r1"),
        2: TestCase(input="t2", output="r2")
    })
    attempt.test_cases = test_cases

    # Create result_cases with wrong test number that somehow passed setter
    # (This would require manipulating the internal state)
    result_cases = TestCases(_data={
        1: TestCase(input="t1", output="r1"),
        3: TestCase(input="t3", output="r3")  # Wrong test number
    })

    # Manually set to bypass setter validation
    attempt._result_cases = result_cases
    attempt._result_cases_data = result_cases.as_dict()

    with pytest.raises(MismatchTestNumsError):
        attempt.mark_as_passed()


def test_attempt_mark_as_passed_all_mismatching():
    """Test mark_as_passed when all outputs are wrong"""
    attempt = Attempt(student_id=1, problem_id=1)

    test_cases = TestCases(_data={
        1: TestCase(input="q1", output="a1"),
        2: TestCase(input="q2", output="a2"),
        3: TestCase(input="q3", output="a3")
    })
    attempt.test_cases = test_cases

    result_cases = TestCases(_data={
        1: TestCase(input="q1", output="wrong1"),
        2: TestCase(input="q2", output="wrong2"),
        3: TestCase(input="q3", output="wrong3")
    })
    attempt.result_cases = result_cases

    with pytest.raises(MismatchTestOutputsError) as exc_info:
        attempt.mark_as_passed()
    error_msg = str(exc_info.value)
    assert "Result of tests [1, 2, 3] are incorrect" in error_msg


def test_attempt_result_cases_property_empty_but_valid():
    """Test mark_as_passed with empty but valid test cases"""
    attempt = Attempt(student_id=1, problem_id=1)

    # Empty test cases
    test_cases = TestCases(_data={})
    attempt.test_cases = test_cases

    # Empty result cases
    result_cases = TestCases(_data={})

    attempt.result_cases = result_cases


def test_attempt_state_persistence():
    """Test that attempt state persists after operations"""
    attempt = Attempt(student_id=42, problem_id=99)

    # Set test cases
    test_cases = TestCases(_data={
        1: TestCase(input="test", output="result")
    })
    attempt.test_cases = test_cases

    # Set results
    result_cases = TestCases(_data={
        1: TestCase(input="test", output="result")
    })
    attempt.result_cases = result_cases

    # Mark as passed
    attempt.mark_as_passed()

    # Verify all states are preserved
    assert attempt.passed is True
    assert attempt.student_id == 42
    assert attempt.problem_id == 99
    assert attempt.amount == 0
    assert attempt.test_cases.count == 1
    assert attempt.result_cases.count == 1
    assert attempt._test_cases_data == {1: {"input": "test", "output": "result"}}
    assert attempt._result_cases_data == {1: {"input": "test", "output": "result"}}


def test_attempt_amount_field():
    """Test that amount field exists and has default value"""
    attempt = Attempt(student_id=1, problem_id=1)
    assert hasattr(attempt, 'amount')
    assert attempt.amount == 0
    # Note: amount is never modified in the current implementation


def test_attempt_repeated_mark_as_passed():
    """Test calling mark_as_passed multiple times"""
    attempt = Attempt(student_id=1, problem_id=1)

    test_cases = TestCases(_data={
        1: TestCase(input="t", output="r")
    })
    attempt.test_cases = test_cases

    result_cases = TestCases(_data={
        1: TestCase(input="t", output="r")
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
    attempt = Attempt(student_id=1, problem_id=1)

    # Create 1000 test cases
    test_data = {
        i: TestCase(input=f"input_{i}", output=f"output_{i}")
        for i in range(1000)
    }
    test_cases = TestCases(_data=test_data)
    attempt.test_cases = test_cases

    # Create matching results
    result_data = {
        i: TestCase(input=f"input_{i}", output=f"output_{i}")
        for i in range(1000)
    }
    result_cases = TestCases(_data=result_data)
    attempt.result_cases = result_cases

    # Should pass
    attempt.mark_as_passed()
    assert attempt.passed is True


def test_attempt_with_special_characters():
    """Test Attempt with special characters in inputs/outputs"""
    attempt = Attempt(student_id=1, problem_id=1)

    test_cases = TestCases(_data={
        1: TestCase(input="a\nb\nc", output="x\ty\tz"),
        2: TestCase(input="test with spaces", output="result with spaces"),
        3: TestCase(input="unicode: café", output="emoji: 🚀"),
        4: TestCase(input="", output="empty input"),
        5: TestCase(input="empty output", output="")
    })
    attempt.test_cases = test_cases

    result_cases = TestCases(_data={
        1: TestCase(input="a\nb\nc", output="x\ty\tz"),
        2: TestCase(input="test with spaces", output="result with spaces"),
        3: TestCase(input="unicode: café", output="emoji: 🚀"),
        4: TestCase(input="", output="empty input"),
        5: TestCase(input="empty output", output="")
    })
    attempt.result_cases = result_cases

    attempt.mark_as_passed()
    assert attempt.passed is True
