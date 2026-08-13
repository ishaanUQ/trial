"""The instrumented merge sort engine.

Pure standard library. No framework imports, so this module can be tested
and trusted on its own, independent of the API and validation layers.
"""

from dataclasses import dataclass


@dataclass
class Counters:
    comparisons: int = 0
    writes: int = 0


def merge_sort(values: list[float]) -> tuple[list[float], Counters]:
    """Sort values with top-down recursive merge sort, counting operations.

    Returns the sorted list and a Counters object tracking every
    element-vs-element comparison and every write into a merged output.
    """
    counters = Counters()
    result = _sort(list(values), counters)
    return result, counters


def _sort(a: list[float], c: Counters) -> list[float]:
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = _sort(a[:mid], c)
    right = _sort(a[mid:], c)
    return _merge(left, right, c)


def _merge(left: list[float], right: list[float], c: Counters) -> list[float]:
    merged: list[float] = []
    i = j = 0
    while i < len(left) and j < len(right):
        c.comparisons += 1
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
        c.writes += 1
    while i < len(left):
        merged.append(left[i])
        i += 1
        c.writes += 1
    while j < len(right):
        merged.append(right[j])
        j += 1
        c.writes += 1
    return merged
