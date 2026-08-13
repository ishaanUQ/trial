"""The merge sort engine.

Pure standard library. No framework imports, so this module can be tested
and trusted on its own, independent of the API and validation layers.
"""


def merge_sort(values: list[float]) -> list[float]:
    """Sort values with top-down recursive merge sort."""
    return _sort(list(values))


def _sort(a: list[float]) -> list[float]:
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = _sort(a[:mid])
    right = _sort(a[mid:])
    return _merge(left, right)


def _merge(left: list[float], right: list[float]) -> list[float]:
    merged: list[float] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    while i < len(left):
        merged.append(left[i])
        i += 1
    while j < len(right):
        merged.append(right[j])
        j += 1
    return merged
