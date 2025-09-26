from collections.abc import Iterable
from typing import Any, Union

from .base_extra_model import ExtraBaseModel

FloatInt = Union[float, int]


class BPXSchemaError(ValueError):
    """Custom exception for schema validation errors."""


def get_materials_in_electrode(e: dict) -> set[str] | None:
    """
    Returns a set of material keys from 'particle' in an electrode dict, or None if
    electrode is a single-material.
    """
    part = getattr(e, "particle", None)
    if isinstance(part, dict) and part:
        return set(part.keys())
    return None


def _find_tagged_fields(model: ExtraBaseModel) -> Iterable[tuple[str, Any, str]]:
    """
    Yields (alias, value, tag) for fields in a single class tagged with 'material_check'
    in `json_schema_extra`.
    """
    for name, f in model.__class__.model_fields.items():
        tag = None
        jsx = f.json_schema_extra
        if jsx:
            tag = jsx.get("material_check")
        if tag:
            yield f.alias, getattr(model, name), str(tag)


def _validate_value_against_keys(
    value: FloatInt | dict[str, FloatInt],
    expected_keys: set[str] | None,
    field_path: str,
) -> None:
    """
    Checks the contents of a single field against the expected material keys from the
    electrode parameterisation.

    `expected_keys` is None for single-material electrodes (`value` must be scalar),
    or a set[str] for blended electrodes (`value` must be dict with `expected_keys`).
    """
    if expected_keys is None:
        # single-material: require scalar
        if isinstance(value, dict):
            msg = f"{field_path!r} must be a float. Electrode is a single material."
            raise BPXSchemaError(msg)
        return

    # blended: require dict with same keys
    if not isinstance(value, dict):
        msg = f"{field_path!r} must be a dict with keys {sorted(expected_keys)}. Electrode is blended."
        raise BPXSchemaError(msg)

    value_keys = set(value.keys())
    if value_keys != expected_keys:
        missing = sorted(expected_keys - value_keys)
        extra = sorted(value_keys - expected_keys)
        parts = []
        if missing:
            parts.append(f"missing keys: {missing}")
        if extra:
            parts.append(f"unexpected keys: {extra}")
        raise BPXSchemaError(f"{field_path!r} keys must exactly match {sorted(expected_keys)}; " + ", ".join(parts))


def validate_section_against_electrodes(
    section_model: ExtraBaseModel,
    section_label: str,
    electrode_materials: dict[str, set[str] | None],
) -> None:
    """
    Validates all fields in a pydantic class against the appropriate electrode materials.

    Assumes that fields which need to be checked are tagged with 'material_check' in their
    json_schema_extra metadata, with value 'negative_electrode' or 'positive_electrode'.

    E.g. for a single field:

    lam_positive: FloatInt | dict[str, FloatInt] = Field(
        alias="LAM: Positive electrode",
        json_schema_extra={"material_check": "positive_electrode"},
    )
    """
    for alias, value, tag in _find_tagged_fields(section_model):
        _validate_value_against_keys(
            value,
            electrode_materials.get(tag),
            f"State.{section_label}.{alias}",
        )
