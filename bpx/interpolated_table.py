from typing import List

from pydantic import BaseModel, validator


class InterpolatedTable(BaseModel):
    x: List[float]
    y: List[float]

    @validator("y")
    def same_length(cls, v: list, values: dict) -> list:
        if "x" in values and len(v) != len(values["x"]):
            raise ValueError("x & y should be same length")
        return v
