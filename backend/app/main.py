"""FastAPI app and routes.

Two endpoints: a liveness check and the sort endpoint itself. The sort
endpoint times only the call into the engine, not request validation
(handled by pydantic before the route body ever runs) and not the metrics
assembly or response serialization that happen afterward.
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
    elapsed_ms = (time.perf_counter() - start) * 1000

    metrics = build_metrics(req.array, result, counters, elapsed_ms)
    return {"result": result, "metrics": metrics}
