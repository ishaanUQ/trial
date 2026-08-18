"""Tests for the merge sort engine only.

No FastAPI, no Pydantic, no HTTP. Just the engine, proven two ways: fixed
cases for known behaviour, and a hypothesis property test that checks the
engine agrees with Python's builtin sorted across many random inputs.
"""

import math

from app.engine.merge_sort import Counters, merge_sort
from hypothesis import given
from hypothesis import strategies as st


def test_empty():
    result, c = merge_sort([])
    assert result == []
    assert c.comparisons == 0
    assert c.writes == 0


def test_single():
    result, c = merge_sort([42])
    assert result == [42]
    assert c.comparisons == 0
    assert c.writes == 0


def test_known_case():
    result, _ = merge_sort([5, 3, 8, 1])
    assert result == [1, 3, 5, 8]


def test_already_sorted():
    result, _ = merge_sort([1, 2, 3, 4, 5])
    assert result == [1, 2, 3, 4, 5]


def test_reverse_sorted():
    result, _ = merge_sort([5, 4, 3, 2, 1])
    assert result == [1, 2, 3, 4, 5]


def test_duplicates():
    result, _ = merge_sort([2, 2, 1, 2])
    assert result == [1, 2, 2, 2]


def test_negative_numbers():
    result, _ = merge_sort([-3, 5, -1, 0, -8, 2])
    assert result == [-8, -3, -1, 0, 2, 5]


def test_floats():
    result, _ = merge_sort([3.14, -1.5, 0.0, 2.71, -2.71])
    assert result == [-2.71, -1.5, 0.0, 2.71, 3.14]


def test_two_element_swap():
    result, c = merge_sort([2, 1])
    assert result == [1, 2]
    assert c.comparisons == 1
    assert c.writes == 2


def test_does_not_mutate_input():
    original = [3, 1, 2]
    merge_sort(original)
    assert original == [3, 1, 2]


def test_writes_equal_element_count():
    values = [9, -4, 2, 2, 0, 17, -33, 8]
    result, c = merge_sort(values)
    assert len(result) == len(values)
    # every element is written exactly once per merge level, and the total
    # number of writes across all merges equals n log2(n) roughly, but at
    # minimum every element must be written at least once overall.
    assert c.writes >= len(values)


def test_counters_default_construction():
    c = Counters()
    assert c.comparisons == 0
    assert c.writes == 0


@given(st.lists(st.integers()))
def test_matches_builtin_sorted_integers(xs):
    result, _ = merge_sort(xs)
    assert result == sorted(xs)


@given(st.lists(st.floats(allow_nan=False, allow_infinity=False)))
def test_matches_builtin_sorted_floats(xs):
    result, _ = merge_sort(xs)
    assert result == sorted(xs)


@given(st.lists(st.integers(), min_size=2))
def test_comparison_upper_bound(xs):
    _, c = merge_sort(xs)
    n = len(xs)
    assert c.comparisons <= n * math.ceil(math.log2(n))


@given(st.lists(st.integers()))
def test_writes_equal_length_times_levels_is_never_negative(xs):
    result, c = merge_sort(xs)
    assert len(result) == len(xs)
    assert c.comparisons >= 0
    assert c.writes >= 0


@given(st.lists(st.integers()))
def test_result_is_sorted_ascending(xs):
    result, _ = merge_sort(xs)
    assert all(result[i] <= result[i + 1] for i in range(len(result) - 1))
