"""Pydantic request models for the /sort endpoint.

Validation lives here so a bad payload never reaches the engine. The engine
trusts its input completely, so this module is where every edge case gets
caught.
"""

from pydantic import BaseModel


class SortRequest(BaseModel):
    array: list[float]
