from typing import List

from pydantic import BaseModel, validator


class InterpolatedTable(BaseModel):
    """
    A table of values that can be interpolated to give a function. The table is defined
    by two lists of floats, x and y. The function is defined by interpolation.
    """

    x: List[float]
    y: List[float]

    @validator("y")
    def same_length(cls, v: list, values: dict) -> list:
        if "x" in values and len(v) != len(values["x"]):
            raise ValueError("x & y should be same length")
        return v
