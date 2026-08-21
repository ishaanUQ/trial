"""Metric assembly for the /sort endpoint.

This module never measures time itself. The API layer is responsible for
timing the sort call with time.perf_counter and handing the elapsed
milliseconds in here, so the timed region stays exactly the sort and
nothing else.

is_sorted is a real verification pass over the result, not an assumption
that the engine got it right. If the engine ever regresses, this is the
check that catches it before a broken result reaches the client.
"""

import math

from app.engine.merge_sort import Counters


def build_metrics(
    original: list[float],
    result: list[float],
    counters: Counters,
    elapsed_ms: float,
) -> dict:
    """Assemble the metrics block for a completed sort.

    original: the input array, used only for its length.
    result: the sorted output, verified here for ascending order.
    counters: comparisons and writes recorded by the engine.
    elapsed_ms: wall-clock duration of the sort call, measured by the
        caller.
    """
    n = len(original)
    is_sorted = all(result[i] <= result[i + 1] for i in range(len(result) - 1))
    ref = n * math.log2(n) if n > 1 else 0.0
    return {
        "element_count": n,
        "comparisons": counters.comparisons,
        "writes": counters.writes,
        "time_ms": round(elapsed_ms, 4),
        "is_sorted": is_sorted,
        # Merge sort needs a full extra array to merge into at every level,
        # so the auxiliary space is on the order of n element-slots. Using
        # n directly is a simple, honest estimate rather than a precise
        # accounting of every intermediate list the recursion allocates.
        "aux_space_estimate": n,
        "reference_n_log_n": round(ref, 2),
    }
