---
name: mergesort-backend
description: Build the FastAPI backend for the merge sort demo, including the instrumented merge sort engine, Pydantic input validation, and the metrics payload. Use this skill whenever work touches the sorting engine, the /sort or /health endpoints, request validation, or performance metric collection for this project. Trigger it for anything backend, API, engine, validation, or metrics related, even if the request does not name FastAPI explicitly.
---

# Merge Sort Backend

This skill defines exactly how the backend is built. Follow the structure and the reference code closely. The engine must stay free of any web framework import so it can be tested on its own.

## Package layout

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          FastAPI app and routes
│   ├── schemas.py       Pydantic request and response models
│   ├── metrics.py       metric assembly helpers
│   └── engine/
│       ├── __init__.py
│       └── merge_sort.py   the instrumented sort, no framework imports
├── requirements.txt
└── Dockerfile           owned by the docker-ci-quality skill
```

## The engine

The engine sorts and counts. It returns the sorted list and a small counters object. It imports nothing beyond the standard library.

```python
# backend/app/engine/merge_sort.py
from dataclasses import dataclass


@dataclass
class Counters:
    comparisons: int = 0
    writes: int = 0


def merge_sort(values: list[float]) -> tuple[list[float], Counters]:
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
```

## Validation and schemas

Validation is a Pydantic model. Reject anything that is not a list of finite numbers, cap the length, allow empty. Booleans are not accepted as numbers.

```python
# backend/app/schemas.py
import math
from pydantic import BaseModel, field_validator

MAX_LEN = 100_000


class SortRequest(BaseModel):
    array: list[float]

    @field_validator("array")
    @classmethod
    def check_array(cls, v: list[float]) -> list[float]:
        if len(v) > MAX_LEN:
            raise ValueError(f"array too long, max {MAX_LEN} elements")
        for x in v:
            if isinstance(x, bool):
                raise ValueError("booleans are not valid numbers")
            if not math.isfinite(x):
                raise ValueError("array must contain only finite numbers")
        return v


class Metrics(BaseModel):
    element_count: int
    comparisons: int
    writes: int
    time_ms: float
    is_sorted: bool
    aux_space_estimate: int
    reference_n_log_n: float


class SortResponse(BaseModel):
    sorted: list[float]
    metrics: Metrics
```

## Metrics assembly

```python
# backend/app/metrics.py
import math
from app.engine.merge_sort import Counters


def build_metrics(original: list[float], result: list[float],
                  counters: Counters, elapsed_ms: float) -> dict:
    n = len(original)
    is_sorted = all(result[i] <= result[i + 1] for i in range(len(result) - 1))
    ref = n * math.log2(n) if n > 1 else 0.0
    return {
        "element_count": n,
        "comparisons": counters.comparisons,
        "writes": counters.writes,
        "time_ms": round(elapsed_ms, 4),
        "is_sorted": is_sorted,
        "aux_space_estimate": n,
        "reference_n_log_n": round(ref, 2),
    }
```

## The API

Two routes. Health for readiness checks, sort for the real work. Time only the sort call, not the request parsing.

```python
# backend/app/main.py
import time
from fastapi import FastAPI
from app.schemas import SortRequest, SortResponse
from app.engine.merge_sort import merge_sort
from app.metrics import build_metrics

app = FastAPI(title="Merge Sort Demo API")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/sort", response_model=SortResponse)
def sort(req: SortRequest) -> SortResponse:
    start = time.perf_counter()
    result, counters = merge_sort(req.array)
    elapsed_ms = (time.perf_counter() - start) * 1000
    metrics = build_metrics(req.array, result, counters, elapsed_ms)
    return SortResponse(sorted=result, metrics=metrics)
```

## requirements.txt

Pin at install time to the current stable releases. The set is fastapi, uvicorn with standard extras, and pydantic. Do not add numpy to the engine.

## Rules

The engine never imports FastAPI or Pydantic. Validation errors surface as FastAPI 422 responses automatically, so the frontend receives structured detail. Time the sort with time.perf_counter and nothing else in the timed region. Verify is_sorted on every response so a broken engine cannot pass silently.
