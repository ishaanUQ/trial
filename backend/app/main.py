"""FastAPI app and routes.

Two endpoints: a liveness check and the sort endpoint itself. The sort
endpoint times only the call into the engine, not request validation
(handled by pydantic before the route body ever runs) and not the metrics
assembly or response serialization that happen afterward.
"""

import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.engine.merge_sort import merge_sort
from app.metrics import build_metrics
from app.schemas import SortRequest

app = FastAPI(title="Merge Sort Demo API")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # FastAPI's default handler echoes the raw rejected input back into the
    # error detail, and that input can itself be a non-finite float (inf,
    # -inf, nan) when the client sends JSON's Infinity/NaN literals. Those
    # values parse fine in Python but aren't valid JSON on the way back out,
    # so Starlette's JSONResponse.render (json.dumps with allow_nan=False)
    # blows up mid-response and turns a clean 422 into a 500. Rebuilding the
    # detail from only "type", "loc", and "msg" avoids ever re-serializing
    # the offending value.
    detail = [
        {"type": err["type"], "loc": err["loc"], "msg": err["msg"]}
        for err in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": detail})


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
