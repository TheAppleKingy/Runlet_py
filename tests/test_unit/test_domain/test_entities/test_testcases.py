import pytest

from src.domain.entities import TestCase, TestCases
from src.domain.entities.exceptions import DuplicateTestCaseInput

# TestCases tests


def test_testcases_empty_initialization():
    """Test TestCases with empty initialization"""
    tc = TestCases()
    assert tc.count == 0
    assert tc.data == {}
    assert list(tc) == []


def test_testcases_with_data():
    """Test TestCases initialization with data"""
    data = {
        1: TestCase(input="in1", output="out1"),
        2: TestCase(input="in2", output="out2")
    }
    tc = TestCases(_data=data)
    assert tc.count == 2
    assert tc.get_case(1).input == "in1"
    assert tc.get_case(2).output == "out2"


def test_testcases_iteration():
    """Test iteration over TestCases"""
    data = {
        1: TestCase(input="a", output="b"),
        2: TestCase(input="c", output="d")
    }
    tc = TestCases(_data=data)

    items = list(tc)
    assert len(items) == 2
    assert items[0] == (1, data[1])
    assert items[1] == (2, data[2])


def test_testcases_duplicate_inputs():
    """Test validation for duplicate inputs"""
    data = {
        1: TestCase(input="same", output="out1"),
        2: TestCase(input="same", output="out2")
    }
    with pytest.raises(DuplicateTestCaseInput):
        TestCases(_data=data)


def test_testcases_io_duplicates_removal():
    """Test IO duplicate validation removes duplicates"""
    data = {
        1: TestCase(input="in1", output="out1"),
        2: TestCase(input="in1", output="out1"),  # Duplicate input/output
        3: TestCase(input="in2", output="out2")
    }
    tc = TestCases(_data=data)
    # Should deduplicate, keeping only one of the duplicates
    assert tc.count == 2
    # Verify which ones were kept (implementation detail)
    remaining_inputs = [case.input for case in tc.data.values()]
    assert "in1" in remaining_inputs
    assert "in2" in remaining_inputs


def test_testcases_io_duplicates_different_outputs():
    """Test IO duplicates with different outputs are not removed"""
    data = {
        1: TestCase(input="same_input", output="out1"),
        2: TestCase(input="same_input", output="out2")  # Same input, different output
    }
    # Should raise DuplicateTestCaseInput due to same inputs
    with pytest.raises(DuplicateTestCaseInput):
        TestCases(_data=data)


def test_testcases_get_case():
    """Test get_case method"""
    data = {
        1: TestCase(input="test1", output="result1"),
        2: TestCase(input="test2", output="result2")
    }
    tc = TestCases(_data=data)

    case1 = tc.get_case(1)
    assert case1.input == "test1"
    assert case1.output == "result1"

    case_nonexistent = tc.get_case(99)
    assert case_nonexistent is None


def test_testcases_as_dict():
    """Test as_dict method"""
    data = {
        1: TestCase(input="i1", output="o1"),
        2: TestCase(input="i2", output="o2")
    }
    tc = TestCases(_data=data)
    result = tc.as_dict()

    assert result == {
        1: {"input": "i1", "output": "o1"},
        2: {"input": "i2", "output": "o2"}
    }


def test_testcases_data_property_getter():
    """Test data property getter"""
    data = {
        1: TestCase(input="x", output="y")
    }
    tc = TestCases(_data=data)

    retrieved_data = tc.data
    assert retrieved_data == data
    assert retrieved_data[1].input == "x"


def test_testcases_data_property_setter():
    """Test data property setter"""
    tc = TestCases()

    data = {
        1: TestCase(input="x", output="y")
    }
    tc.data = data

    assert tc.count == 1
    assert tc.get_case(1).input == "x"


def test_testcases_data_property_setter_with_validation():
    """Test data property setter triggers validation"""
    tc = TestCases()

    data = {
        1: TestCase(input="same", output="out1"),
        2: TestCase(input="same", output="out2")  # Duplicate input
    }

    with pytest.raises(DuplicateTestCaseInput):
        tc.data = data


def test_testcases_update_test_cases():
    """Test update_test_cases method"""
    initial_data = {
        1: TestCase(input="in1", output="out1"),
        2: TestCase(input="in2", output="out2")
    }
    tc = TestCases(_data=initial_data)

    update_data = {
        3: TestCase(input="in3", output="out3"),
        4: TestCase(input="in4", output="out4")
    }

    tc.update_test_cases(update_data)
    assert tc.count == 4
    assert tc.get_case(3).input == "in3"
    assert tc.get_case(4).output == "out4"


def test_testcases_update_with_duplicate_input():
    """Test update with duplicate input should fail"""
    initial_data = {
        1: TestCase(input="in1", output="out1")
    }
    tc = TestCases(_data=initial_data)

    update_data = {
        2: TestCase(input="in1", output="out2")  # Same input
    }

    with pytest.raises(DuplicateTestCaseInput):
        tc.update_test_cases(update_data)


def test_testcases_update_with_empty_dict():
    """Test updating with empty dictionary"""
    data = {1: TestCase(input="a", output="b")}
    tc = TestCases(_data=data)

    tc.update_test_cases({})
    assert tc.count == 1
    assert tc.get_case(1).input == "a"


def test_testcases_delete_test_cases():
    """Test delete_test_cases method"""
    data = {
        1: TestCase(input="a", output="b"),
        2: TestCase(input="c", output="d"),
        3: TestCase(input="e", output="f")
    }
    tc = TestCases(_data=data)

    tc.delete_test_cases([1, 3])
    assert tc.count == 1
    assert tc.get_case(2) is not None
    assert tc.get_case(1) is None
    assert tc.get_case(3) is None


def test_testcases_delete_nonexistent():
    """Test deleting nonexistent test cases"""
    data = {
        1: TestCase(input="a", output="b")
    }
    tc = TestCases(_data=data)

    # Should not raise error for nonexistent keys
    tc.delete_test_cases([99, 100])
    assert tc.count == 1


def test_testcases_delete_empty_list():
    """Test deleting with empty list"""
    data = {1: TestCase(input="a", output="b")}
    tc = TestCases(_data=data)

    tc.delete_test_cases([])
    assert tc.count == 1


def test_testcases_count_property():
    """Test count property"""
    data = {
        1: TestCase(input="a", output="b"),
        2: TestCase(input="c", output="d"),
        3: TestCase(input="e", output="f")
    }
    tc = TestCases(_data=data)
    assert tc.count == 3

    tc.delete_test_cases([1])
    assert tc.count == 2

    tc.update_test_cases({4: TestCase(input="g", output="h")})
    assert tc.count == 3


def test_testcases_with_single_case():
    """Test TestCases with single test case"""
    tc = TestCases(_data={1: TestCase(input="single", output="case")})
    assert tc.count == 1
    assert tc.get_case(1).input == "single"
    assert list(tc) == [(1, tc.get_case(1))]


def test_testcases_empty_dict_initialization():
    """Test TestCases with empty dict initialization"""
    tc = TestCases(_data={})
    assert tc.count == 0
    assert tc.as_dict() == {}


def test_testcases_from_dict_with_validation():
    """Test that as_dict and reconstruction maintains validation"""
    original_data = {
        1: TestCase(input="test1", output="result1"),
        2: TestCase(input="test2", output="result2")
    }
    tc = TestCases(_data=original_data)

    # Convert to dict and back
    dict_repr = tc.as_dict()
    new_tc = TestCases(_data={
        num: TestCase(**case_dict)
        for num, case_dict in dict_repr.items()
    })

    assert new_tc.count == tc.count
    assert new_tc.as_dict() == dict_repr


def test_testcases_mixed_case_validations():
    """Test mixed validation scenarios"""
    # This should pass - all unique inputs
    data = {
        1: TestCase(input="a", output="1"),
        2: TestCase(input="b", output="2"),
        3: TestCase(input="c", output="3")
    }
    tc = TestCases(_data=data)
    assert tc.count == 3

    # Add a duplicate input - should fail
    with pytest.raises(DuplicateTestCaseInput):
        tc.update_test_cases({4: TestCase(input="a", output="4")})


def test_testcases_duplicate_input_output_pairs():
    """Test exact duplicate input/output pairs"""
    # These should be deduplicated by _validate_io_duplicates
    data = {
        1: TestCase(input="same", output="same"),
        2: TestCase(input="same", output="same"),  # Exact duplicate
        3: TestCase(input="different", output="output")
    }
    tc = TestCases(_data=data)
    # Should have 2 (one "same,same" pair and "different,output")
    assert tc.count == 2


def test_testcases_edge_case_empty_strings():
    """Test with empty strings as valid input/output"""
    data = {
        1: TestCase(input="", output=""),
        2: TestCase(input=" ", output=" "),
        3: TestCase(input="\t", output="\n")
    }
    tc = TestCases(_data=data)
    assert tc.count == 3
    assert tc.get_case(1).input == ""
    assert tc.get_case(2).input == " "


def test_testcases_large_number_of_cases():
    """Test with larger number of test cases"""
    data = {
        i: TestCase(input=f"input_{i}", output=f"output_{i}")
        for i in range(100)
    }
    tc = TestCases(_data=data)
    assert tc.count == 100
    assert tc.get_case(50).input == "input_50"
    assert tc.get_case(99).output == "output_99"
