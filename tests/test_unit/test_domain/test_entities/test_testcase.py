import pytest
from src.domain.entities import TestCase
from src.domain.entities.exceptions import ValidationTestCaseError

# TestCase tests


def test_testcase_initialization_valid():
    """Test TestCase initialization with valid data"""
    tc = TestCase(input="test_input", output="expected_output")
    assert tc.input == "test_input"
    assert tc.output == "expected_output"


def test_testcase_initialization_default():
    """Test TestCase initialization with defaults"""
    tc = TestCase()
    assert tc.input == ""
    assert tc.output == ""


def test_testcase_initialization_invalid_input():
    """Test TestCase initialization with invalid input"""
    with pytest.raises(ValidationTestCaseError):
        TestCase(input=None, output="output")

    with pytest.raises(ValidationTestCaseError):
        TestCase(input=123, output="output")


def test_testcase_initialization_invalid_output():
    """Test TestCase initialization with invalid output"""
    with pytest.raises(ValidationTestCaseError):
        TestCase(input="input", output=None)

    with pytest.raises(ValidationTestCaseError):
        TestCase(input="input", output=456)


def test_testcase_to_dict():
    """Test conversion to dictionary"""
    tc = TestCase(input="input_data", output="output_data")
    result = tc.to_dict()
    assert result == {"input": "input_data", "output": "output_data"}


def test_testcase_from_dict_valid():
    """Test loading from valid dictionary"""
    tc = TestCase()
    tc.from_dict({"input": "new_input", "output": "new_output"})
    assert tc.input == "new_input"
    assert tc.output == "new_output"


def test_testcase_from_dict_missing_input():
    """Test loading from dictionary with missing input"""
    tc = TestCase()
    with pytest.raises(ValidationTestCaseError):
        tc.from_dict({"output": "some_output"})


def test_testcase_from_dict_missing_output():
    """Test loading from dictionary with missing output"""
    tc = TestCase()
    with pytest.raises(ValidationTestCaseError):
        tc.from_dict({"input": "some_input"})


def test_testcase_from_dict_wrong_type():
    """Test loading from dictionary with wrong types"""
    tc = TestCase()
    with pytest.raises(ValidationTestCaseError):
        tc.from_dict({"input": 123, "output": "output"})

    with pytest.raises(ValidationTestCaseError):
        tc.from_dict({"input": "input", "output": 456})

    with pytest.raises(ValidationTestCaseError):
        tc.from_dict({"input": None, "output": "output"})
