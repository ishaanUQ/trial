"""Tests for metrics assembly only.

No FastAPI, no HTTP, no timing. build_metrics is exercised directly with
hand-built Counters and elapsed times, so these tests prove the metrics
block is assembled correctly regardless of how the API layer wires it up.
"""

import math

from app.engine.merge_sort import Counters, merge_sort
from app.metrics import build_metrics


def test_element_count_matches_input_length():
    original = [5, 3, 8, 1, 9]
    result, counters = merge_sort(original)
    metrics = build_metrics(original, result, counters, 1.0)
    assert metrics["element_count"] == 5


def test_element_count_empty():
    metrics = build_metrics([], [], Counters(), 0.0)
    assert metrics["element_count"] == 0


def test_comparisons_and_writes_pass_through():
    counters = Counters(comparisons=7, writes=11)
    metrics = build_metrics([1, 2, 3], [1, 2, 3], counters, 2.5)
    assert metrics["comparisons"] == 7
    assert metrics["writes"] == 11


def test_comparisons_and_writes_from_real_sort():
    original = [5, 3, 8, 1]
    result, counters = merge_sort(original)
    metrics = build_metrics(original, result, counters, 1.0)
    assert metrics["comparisons"] == counters.comparisons
    assert metrics["writes"] == counters.writes


def test_is_sorted_true_for_sorted_output():
    metrics = build_metrics([3, 1, 2], [1, 2, 3], Counters(), 1.0)
    assert metrics["is_sorted"] is True


def test_is_sorted_false_for_unsorted_output():
    # Deliberately hand build_metrics a result that is not actually
    # sorted. This proves the function performs a real verification pass
    # rather than assuming whatever it is given is correct.
    metrics = build_metrics([3, 1, 2], [3, 1, 2], Counters(), 1.0)
    assert metrics["is_sorted"] is False


def test_is_sorted_true_for_empty_result():
    metrics = build_metrics([], [], Counters(), 0.0)
    assert metrics["is_sorted"] is True


def test_is_sorted_true_for_single_element():
    metrics = build_metrics([42], [42], Counters(), 0.0)
    assert metrics["is_sorted"] is True


def test_is_sorted_true_with_duplicates():
    metrics = build_metrics([2, 2, 1], [1, 2, 2], Counters(), 1.0)
    assert metrics["is_sorted"] is True


def test_reference_n_log_n_zero_for_empty():
    metrics = build_metrics([], [], Counters(), 0.0)
    assert metrics["reference_n_log_n"] == 0.0


def test_reference_n_log_n_zero_for_single_element():
    metrics = build_metrics([1], [1], Counters(), 0.0)
    assert metrics["reference_n_log_n"] == 0.0


def test_reference_n_log_n_known_value():
    original = [0] * 8
    metrics = build_metrics(original, original, Counters(), 0.0)
    # 8 * log2(8) = 8 * 3 = 24
    assert metrics["reference_n_log_n"] == 24.0


def test_reference_n_log_n_matches_formula():
    original = list(range(100))
    metrics = build_metrics(original, original, Counters(), 0.0)
    expected = round(100 * math.log2(100), 2)
    assert metrics["reference_n_log_n"] == expected


def test_time_ms_passed_through():
    metrics = build_metrics([1, 2], [1, 2], Counters(), 3.14159)
    assert metrics["time_ms"] == round(3.14159, 4)


def test_time_ms_zero():
    metrics = build_metrics([], [], Counters(), 0.0)
    assert metrics["time_ms"] == 0.0


def test_aux_space_estimate_equals_element_count():
    original = [4, 2, 7, 1, 9, 3]
    metrics = build_metrics(original, sorted(original), Counters(), 1.0)
    assert metrics["aux_space_estimate"] == len(original)


def test_full_metrics_block_keys():
    original = [5, 3, 8, 1]
    result, counters = merge_sort(original)
    metrics = build_metrics(original, result, counters, 1.0)
    assert set(metrics.keys()) == {
        "element_count",
        "comparisons",
        "writes",
        "time_ms",
        "is_sorted",
        "aux_space_estimate",
        "reference_n_log_n",
    }
