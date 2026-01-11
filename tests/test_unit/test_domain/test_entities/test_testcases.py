import pytest
from src.domain.value_objects.exceptions import DuplicateTestCaseInput, ValidationTestCaseError
from src.domain.value_objects import TestCase, TestCases


# ============ TestCases Tests ============

def test_testcases_empty_creation():
    """Test creating empty TestCases collection"""
    tcs = TestCases()

    assert tcs.count == 0
    assert list(tcs) == []
    assert tcs.as_dict() == {}


def test_testcases_creation_with_initial_data():
    """Test creating TestCases with initial data"""
    tc1 = TestCase(input="1+1", output="2")
    tc2 = TestCase(input="2+2", output="4")

    tcs = TestCases(_data={1: tc1, 2: tc2})

    assert tcs.count == 2
    assert list(tcs) == [(1, tc1), (2, tc2)]
    assert tcs.get_case(1) == tc1
    assert tcs.get_case(2) == tc2
    assert tcs.get_case(3) is None


def test_testcases_validation_on_creation():
    """Test validation happens during creation"""
    # Same input, different outputs should raise
    with pytest.raises(DuplicateTestCaseInput):
        TestCases(_data={
            1: TestCase(input="same", output="output1"),
            2: TestCase(input="same", output="output2")
        })


def test_testcases_duplicate_input_output_pairs_removed():
    """Test exact duplicate test cases are removed"""
    tc1 = TestCase(input="1+1", output="2")
    tc2 = TestCase(input="1+1", output="2")  # Exact duplicate
    tc3 = TestCase(input="2+2", output="4")

    tcs = TestCases(_data={1: tc1, 2: tc2, 3: tc3})

    # tc2 should be silently removed
    assert tcs.count == 2
    assert 1 in tcs._data
    assert 2 not in tcs._data  # Removed
    assert 3 in tcs._data


def test_testcases_as_dict():
    """Test converting TestCases to dictionary"""
    tc1 = TestCase(input="test1", output="result1")
    tc2 = TestCase(input="test2", output="result2")

    tcs = TestCases(_data={1: tc1, 2: tc2})
    result = tcs.as_dict()

    assert result == {
        1: {"input": "test1", "output": "result1"},
        2: {"input": "test2", "output": "result2"}
    }

    # Empty collection
    empty_tcs = TestCases()
    assert empty_tcs.as_dict() == {}


def test_testcases_from_dict_with_missing_output():
    """Test from_dict handles missing output (uses default)"""
    data = {
        1: {"input": "1+1", "output": "2"},
        2: {"input": "2+2", "output": "4"},
        3: {"input": "print('hi')"}  # Missing output, should use default ""
    }

    # Это ДОЛЖНО РАБОТАТЬ!
    tcs = TestCases.from_dict(data)

    assert tcs.count == 3
    assert tcs.get_case(3).input == "print('hi')"
    assert tcs.get_case(3).output == ""  # Default value


def test_testcases_from_dict_valid():
    """Test from_dict with valid complete data"""
    data = {
        1: {"input": "1+1", "output": "2"},
        2: {"input": "2+2", "output": "4"}
    }

    tcs = TestCases.from_dict(data)

    assert tcs.count == 2
    assert tcs.get_case(1).input == "1+1"
    assert tcs.get_case(1).output == "2"
    assert tcs.get_case(2).input == "2+2"
    assert tcs.get_case(2).output == "4"


def test_testcases_update_test_cases():
    """Test updating test cases"""
    tcs = TestCases()

    tc1 = TestCase(input="1", output="1")
    tc2 = TestCase(input="2", output="2")

    tcs.update_test_cases({1: tc1, 2: tc2})

    assert tcs.count == 2
    assert tcs.get_case(1) == tc1
    assert tcs.get_case(2) == tc2

    # Update existing and add new
    tc3 = TestCase(input="3", output="3")
    tc1_updated = TestCase(input="1_updated", output="1")

    tcs.update_test_cases({1: tc1_updated, 3: tc3})

    assert tcs.count == 3
    assert tcs.get_case(1).input == "1_updated"  # Updated
    assert tcs.get_case(2).input == "2"  # Unchanged
    assert tcs.get_case(3).input == "3"  # New


def test_testcases_update_with_duplicates_fails():
    """Test update fails when introducing duplicate inputs"""
    tc1 = TestCase(input="unique", output="1")
    tcs = TestCases(_data={1: tc1})

    # Try to add test case with same input as existing
    tc2 = TestCase(input="unique", output="2")

    with pytest.raises(DuplicateTestCaseInput):
        tcs.update_test_cases({2: tc2})


def test_testcases_update_removes_exact_duplicates():
    """Test update silently removes exact duplicates"""
    tc1 = TestCase(input="test", output="result")
    tcs = TestCases(_data={1: tc1})

    # Exact same test case
    tc2 = TestCase(input="test", output="result")

    # Should not raise, should silently ignore duplicate
    tcs.update_test_cases({2: tc2})
    assert tcs.count == 1
    assert tcs.get_case(1) == tc1

    # The duplicate might be removed or not added
    # Current implementation would remove it in _validate_io_duplicates


def test_testcases_delete_test_cases():
    """Test deleting test cases"""
    tc1 = TestCase(input="1", output="1")
    tc2 = TestCase(input="2", output="2")
    tc3 = TestCase(input="3", output="3")

    tcs = TestCases(_data={1: tc1, 2: tc2, 3: tc3})

    # Delete single
    tcs.delete_test_cases([2])

    assert tcs.count == 2
    assert tcs.get_case(1) == tc1
    assert tcs.get_case(2) is None
    assert tcs.get_case(3) == tc3

    # Delete multiple
    tcs.delete_test_cases([1, 3])

    assert tcs.count == 0
    assert list(tcs) == []


def test_testcases_delete_nonexistent():
    """Test deleting non-existent test cases"""
    tc1 = TestCase(input="test", output="result")
    tcs = TestCases(_data={1: tc1})

    # Should not raise when deleting non-existent
    tcs.delete_test_cases([999, 1000])

    assert tcs.count == 1
    assert tcs.get_case(1) == tc1


def test_testcases_iteration():
    """Test iteration over TestCases"""
    tc1 = TestCase(input="1", output="1")
    tc2 = TestCase(input="2", output="2")
    tc3 = TestCase(input="3", output="3")

    tcs = TestCases(_data={1: tc1, 2: tc2, 3: tc3})

    # Test iteration
    items = list(tcs)
    assert len(items) == 3
    assert items[0] == (1, tc1)
    assert items[1] == (2, tc2)
    assert items[2] == (3, tc3)

    # Test iteration order (should match insertion order in Python 3.7+)
    tcs2 = TestCases(_data={3: tc3, 1: tc1, 2: tc2})
    order = [num for num, _ in tcs2]
    assert order == [3, 1, 2]


def test_testcases_count_property():
    """Test count property updates correctly"""
    tcs = TestCases()
    assert tcs.count == 0

    tc1 = TestCase(input="1", output="1")
    tcs.update_test_cases({1: tc1})
    assert tcs.count == 1

    tc2 = TestCase(input="2", output="2")
    tcs.update_test_cases({2: tc2})
    assert tcs.count == 2

    tcs.delete_test_cases([1])
    assert tcs.count == 1

    tcs.delete_test_cases([2])
    assert tcs.count == 0

# ===================== Edge Cases =====================


def test_testcases_with_empty_inputs():
    """Test handling of empty input strings"""
    # Multiple empty inputs should be considered duplicates
    with pytest.raises(DuplicateTestCaseInput):
        TestCases(_data={
            1: TestCase(input="", output="result1"),
            2: TestCase(input="", output="result2")  # Same empty input
        })


def test_testcases_with_special_characters():
    """Test with special/unicode characters"""
    special = TestCase(input="print('café')", output="café")
    emoji = TestCase(input="print('🎉')", output="🎉")

    tcs = TestCases(_data={1: special, 2: emoji})

    assert tcs.get_case(1).input == "print('café')"
    assert tcs.get_case(2).output == "🎉"

    # Roundtrip through dict
    as_dict = tcs.as_dict()
    assert as_dict[1]["input"] == "print('café')"
    assert as_dict[2]["output"] == "🎉"


def test_testcases_negative_and_zero_keys():
    """Test with non-positive integer keys"""
    tc = TestCase(input="test", output="result")

    # Negative key
    with pytest.raises(ValidationTestCaseError):
        tcs1 = TestCases(_data={-1: tc})

    # Zero key
    with pytest.raises(ValidationTestCaseError):
        tcs2 = TestCases(_data={0: tc})

    # Mixed
    tc2 = TestCase(input="test2", output="result2")
    with pytest.raises(ValidationTestCaseError):
        tcs3 = TestCases(_data={-10: tc, 0: tc2, 10: TestCase(input="3", output="3")})


def test_testcases_large_number_of_cases():
    """Test with many test cases"""
    # Create 1000 test cases
    data = {
        i: TestCase(input=f"input_{i}", output=f"output_{i}")
        for i in range(1, 1000)
    }

    tcs = TestCases(_data=data)

    assert tcs.count == 999

    # Verify random samples
    assert tcs.get_case(0) == None
    assert tcs.get_case(500).input == "input_500"
    assert tcs.get_case(999).input == "input_999"


def test_testcases_string_keys_in_dict():
    """Test behavior with string keys (type hint violation)"""
    # Type hints say keys should be int, but Python doesn't enforce
    data = {
        "1": {"input": "test1", "output": "result1"},  # string key
        "2": {"input": "test2", "output": "result2"}
    }

    with pytest.raises(ValidationTestCaseError):
        tcs = TestCases.from_dict(data)  # type: ignore


# ===================== Error Scenarios =====================


def test_testcases_atomicity_of_update():
    """Test that failed update doesn't partially modify data"""
    tc1 = TestCase(input="original", output="1")
    tcs = TestCases(_data={1: tc1})

    # Try to update with valid and invalid data
    tc2 = TestCase(input="new", output="2")
    tc3 = TestCase(input="original", output="different")  # Will cause duplicate error

    try:
        tcs.update_test_cases({2: tc2, 3: tc3})
    except DuplicateTestCaseInput:
        pass

    # Original data should be unchanged
    assert tcs.count == 1
    assert tcs.get_case(1) == tc1
    assert tcs.get_case(2) is None  # Should not have been added
    assert tcs.get_case(3) is None


def test_testcases_modify_case_after_adding():
    """Test that modifying a TestCase affects the collection"""
    tc = TestCase(input="original", output="result")
    tcs = TestCases(_data={1: tc})

    # Modify the TestCase object directly
    tc.input = "modified"

    # The change is reflected in the collection
    assert tcs.get_case(1).input == "modified"

    # This shows TestCases holds references, not copies
    # This might be desired or not depending on use case


def test_testcases_shared_references():
    """Test that TestCases can share TestCase objects"""
    tc = TestCase(input="shared", output="result")

    # Same object in multiple slots
    tcs = TestCases(_data={1: tc, 2: tc})

    assert tcs.count == 1  # Duplicate removed!
    # Because _validate_io_duplicates removes exact duplicates

    # Or if not removed, they're the same object
    if 2 in tcs._data:
        assert tcs.get_case(1) is tcs.get_case(2)  # Same object

# ===================== Property-based Style Tests =====================


def test_testcases_roundtrip_consistency():
    """Test that to_dict and from_dict are inverses"""
    original = TestCases(_data={
        1: TestCase(input="a = 1", output=""),
        2: TestCase(input="print(a)", output="1"),
        3: TestCase(input="", output="empty")
    })

    # Convert to dict and back
    as_dict = original.as_dict()
    reconstructed = TestCases.from_dict(as_dict)

    # Should have same data
    assert reconstructed.count == original.count

    for num, case in original:
        recon_case = reconstructed.get_case(num)
        assert recon_case is not None
        assert recon_case.input == case.input
        assert recon_case.output == case.output

    # Dict representation should match
    assert reconstructed.as_dict() == as_dict


def test_testcases_idempotent_updates():
    """Test that updating with same data doesn't change anything"""
    tc1 = TestCase(input="test1", output="result1")
    tc2 = TestCase(input="test2", output="result2")

    tcs = TestCases(_data={1: tc1, 2: tc2})

    original_data = tcs._data.copy()

    # Update with same data
    tcs.update_test_cases({1: tc1, 2: tc2})

    # Should be unchanged
    assert tcs._data == original_data

    # Update with exact duplicates
    tc1_dup = TestCase(input="test1", output="result1")
    tcs.update_test_cases({1: tc1_dup})

    # Might be different object but same value
    assert tcs.get_case(1).input == "test1"
    assert tcs.get_case(1).output == "result1"
