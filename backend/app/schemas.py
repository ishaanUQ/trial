"""Pydantic request models for the /sort endpoint.

Validation lives here so a bad payload never reaches the engine. The engine
trusts its input completely, so this module is where every edge case gets
caught: wrong types, booleans disguised as numbers, non-finite values, and
arrays that are just too long to sort in a single request.
"""

import math
from typing import Any

from pydantic import BaseModel, field_validator

MAX_LEN = 100_000


class SortRequest(BaseModel):
    array: list[float]

    @field_validator("array", mode="before")
    @classmethod
    def check_array(cls, v: Any) -> Any:
        # mode="before" runs on the raw input, ahead of pydantic's own
        # coercion. That matters here: by the time a "list[float]" field
        # has been coerced, True and False already look like 1.0 and 0.0,
        # and bool is a subclass of int so isinstance checks after
        # coercion can't tell them apart from real numbers anymore. Doing
        # the check first, on the raw values, is what makes rejecting
        # booleans actually work.
        # pydantic only converts ValueError (or AssertionError) raised here
        # into a proper ValidationError, so these stay ValueError even
        # where the failure is really a type mismatch.
        if not isinstance(v, list):
            raise ValueError("array must be a list of numbers")  # noqa: TRY004
        if len(v) > MAX_LEN:
            raise ValueError(f"array too long, max {MAX_LEN} elements")
        for x in v:
            if isinstance(x, bool):
                raise ValueError("booleans are not valid numbers")  # noqa: TRY004
            if not isinstance(x, (int, float)):
                raise ValueError("array must contain only numbers")  # noqa: TRY004
            if not math.isfinite(x):
                raise ValueError("array must contain only finite numbers")
        return v
