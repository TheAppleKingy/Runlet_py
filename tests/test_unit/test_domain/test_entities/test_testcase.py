import pytest

from src.domain.value_objects import TestCase
from src.domain.value_objects.exceptions import ValidationTestCaseError

# ===================== TestCase Tests =====================


def test_testcase_creation_valid():
    """Test basic valid TestCase creation"""
    # With both input and output
    tc = TestCase(input="1+1", output="2")
    assert tc.input == "1+1"
    assert tc.output == "2"

    # With default output
    tc2 = TestCase(input="test")
    assert tc2.input == "test"
    assert tc2.output == ""

    # Empty strings allowed
    tc3 = TestCase(input="", output="")
    assert tc3.input == ""
    assert tc3.output == ""


def test_testcase_validation_raises_on_non_string():
    """Test validation raises for non-string values"""
    # Invalid input types
    with pytest.raises(ValidationTestCaseError):
        TestCase(input=None, output="test")  # type: ignore

    with pytest.raises(ValidationTestCaseError):
        TestCase(input=123, output="test")  # type: ignore

    with pytest.raises(ValidationTestCaseError):
        TestCase(input=["list"], output="test")  # type: ignore

    # Invalid output types
    with pytest.raises(ValidationTestCaseError):
        TestCase(input="test", output=None)  # type: ignore

    with pytest.raises(ValidationTestCaseError):
        TestCase(input="test", output=456)  # type: ignore


def test_testcase_to_dict():
    """Test to_dict method returns correct structure"""
    tc = TestCase(input="print('hello')", output="hello")
    result = tc.to_dict()

    assert isinstance(result, dict)
    assert result == {"input": "print('hello')", "output": "hello"}

    # With default output
    tc2 = TestCase(input="test")
    assert tc2.to_dict() == {"input": "test", "output": ""}


def test_testcase_from_dict():
    """Test from_dict factory method"""
    # Complete data
    data = {"input": "test input", "output": "test output"}
    tc = TestCase.from_dict(data)
    assert tc.input == "test input"
    assert tc.output == "test output"

    # Data with only input (should fail with current implementation)
    data2 = {"input": "test only"}
    tc = TestCase.from_dict(data2)  # Missing 'output' key
    assert tc.input == "test only"
    assert tc.output == ""

    # Extra keys in dict (should be ignored or cause error?)
    data3 = {"input": "test", "output": "result", "extra": "field"}
    with pytest.raises(TypeError):
        TestCase.from_dict(data3)


def test_testcase_equality():
    """Test TestCase equality comparison"""
    tc1 = TestCase(input="test", output="result")
    tc2 = TestCase(input="test", output="result")
    tc3 = TestCase(input="different", output="result")
    tc4 = TestCase(input="test", output="different")

    assert tc1 == tc2  # Same values
    assert tc1 != tc3  # Different input
    assert tc1 != tc4  # Different output


def test_testcase_is_mutable():
    """Test that TestCase objects are mutable"""
    tc = TestCase(input="original", output="result")

    # Can modify attributes directly
    tc.input = "modified"
    tc.output = "changed"

    assert tc.input == "modified"
    assert tc.output == "changed"

    # Modification bypasses validation!
    # This is a potential issue
    tc.input = 123  # type: ignore # Should fail but doesn't
    assert tc.input == 123
