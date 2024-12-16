from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class ExtraBaseModel(BaseModel):
    """
    A base model that forbids extra fields
    """

    model_config = ConfigDict(extra="forbid")

    class Settings:
        """
        Class with BPX-related settings.
        It might be worth moving it to a separate file if it grows bigger.
        """

        tolerances: ClassVar[dict] = {
            "Voltage [V]": 1e-3,  # Absolute tolerance in [V] to validate the voltage limits
        }
