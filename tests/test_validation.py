"""Tests for the SortRequest validation model only.

No FastAPI, no HTTP. These tests instantiate the pydantic model directly
and check that it accepts good input and rejects every bad shape the
/sort endpoint could be handed: wrong types, booleans, non-finite
numbers, and over-length arrays.
"""

import math

import pytest
from app.schemas import MAX_LEN, SortRequest
from pydantic import ValidationError


def test_valid_array_of_ints():
    req = SortRequest(array=[5, 3, 8, 1])
    assert req.array == [5.0, 3.0, 8.0, 1.0]


def test_valid_array_of_floats():
    req = SortRequest(array=[3.14, -1.5, 0.0])
    assert req.array == [3.14, -1.5, 0.0]


def test_empty_array_is_allowed():
    req = SortRequest(array=[])
    assert req.array == []


def test_rejects_string_entry():
    with pytest.raises(ValidationError):
        SortRequest(array=[1, "two", 3])


def test_rejects_nested_list_entry():
    with pytest.raises(ValidationError):
        SortRequest(array=[1, [2, 3], 4])


def test_rejects_none_entry():
    with pytest.raises(ValidationError):
        SortRequest(array=[1, None, 3])


def test_rejects_boolean_entries():
    with pytest.raises(ValidationError):
        SortRequest(array=[1, True, 3])


def test_rejects_all_boolean_array():
    with pytest.raises(ValidationError):
        SortRequest(array=[True, False])


def test_rejects_infinity():
    with pytest.raises(ValidationError):
        SortRequest(array=[1, math.inf, 3])


def test_rejects_negative_infinity():
    with pytest.raises(ValidationError):
        SortRequest(array=[1, -math.inf, 3])


def test_rejects_nan():
    with pytest.raises(ValidationError):
        SortRequest(array=[1, math.nan, 3])


def test_rejects_over_length_array():
    with pytest.raises(ValidationError):
        SortRequest(array=[1.0] * (MAX_LEN + 1))


def test_accepts_array_at_max_length():
    req = SortRequest(array=[1.0] * MAX_LEN)
    assert len(req.array) == MAX_LEN


def test_rejects_non_list_array():
    with pytest.raises(ValidationError):
        SortRequest(array="not a list")


def test_rejects_missing_array_field():
    with pytest.raises(ValidationError):
        SortRequest()
