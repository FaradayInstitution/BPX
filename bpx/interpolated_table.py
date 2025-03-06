from __future__ import annotations

from pydantic import BaseModel, ValidationInfo, field_validator


class InterpolatedTable(BaseModel):
    """
    A table of values that can be interpolated to give a function. The table is defined
    by two lists of floats, x and y. The function is defined by interpolation.
    """

    x: list[float]
    y: list[float]

    @field_validator("y")
    @classmethod
    def same_length(cls, v: list, info: ValidationInfo) -> list:
        if "x" in info.data and len(v) != len(info.data["x"]):
            error_msg = "x & y should be same length"
            raise ValueError(error_msg)
        return v
