"""FastAPI app and routes.

Two endpoints: a liveness check and the sort endpoint itself.
"""

import time

from fastapi import FastAPI

from app.engine.merge_sort import merge_sort
from app.metrics import build_metrics
from app.schemas import SortRequest

app = FastAPI(title="Merge Sort Demo API")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/sort")
def sort(req: SortRequest) -> dict:
    start = time.perf_counter()
    result, counters = merge_sort(req.array)
    metrics = build_metrics(req.array, result, counters, 0.0)
    elapsed_ms = (time.perf_counter() - start) * 1000
    metrics["time_ms"] = round(elapsed_ms, 4)
    return {"result": result, "metrics": metrics}
