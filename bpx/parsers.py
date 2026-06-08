from __future__ import annotations

import json
from pathlib import Path
from warnings import warn

import yaml

from ._migrations import convert_v0_to_v1, is_legacy_bpx
from .schema import BPX

_LEGACY_CONVERSION_WARNING = (
    "Detected a legacy BPX v0.x file/object; converting to the v1.x schema for "
    "backward compatibility. The conversion is approximate: the required 'State' "
    "fields are synthesised with placeholders (heat transfer coefficient and "
    "initial hysteresis state set to 0, initial electrolyte concentration "
    "defaulted to 1000 mol.m-3 when absent, lumped thermal conductivity dropped) "
    "and cross-version semantic changes are not corrected. Re-export from bpx>=1 "
    "to silence this warning, or pass convert_legacy=False to disable conversion."
)


def parse_bpx_obj(
    bpx: dict,
    v_tol: float = 0.001,
    *,
    convert_legacy: bool = True,
) -> BPX:
    """
    A convenience function to parse a bpx dict into a BPX model.

    Parameters
    ----------
    bpx: dict
        a dict object in bpx format
    v_tol: float
        absolute tolerance in [V] to validate the voltage limits, 1 mV by default
    convert_legacy: bool
        if True (default), a legacy BPX v0.x object is detected and converted to
        the v1.x schema on a best-effort basis, raising a ``UserWarning``. Set to
        False to validate the object as-is (v0.x objects then raise a
        ``ValidationError``). The passed ``bpx`` dict is not mutated.

    Returns
    -------
    BPX: :class:`bpx.BPX`
        a parsed BPX model
    """
    if v_tol < 0:
        error_msg = "v_tol should not be negative"
        raise ValueError(error_msg)

    if convert_legacy and is_legacy_bpx(bpx):
        warn(_LEGACY_CONVERSION_WARNING, UserWarning, stacklevel=2)
        bpx = convert_v0_to_v1(bpx)

    BPX.Settings.tolerances["Voltage [V]"] = v_tol

    return BPX.model_validate(bpx)


def parse_bpx_file(
    filename: str | Path,
    v_tol: float = 0.001,
    *,
    convert_legacy: bool = True,
) -> BPX:
    """
    A convenience function to parse a bpx file into a BPX model.

    Parameters
    ----------
    filename: str or Path
        a filepath to a bpx file
    v_tol: float
        absolute tolerance in [V] to validate the voltage limits, 1 mV by default
    convert_legacy: bool
        if True (default), a legacy BPX v0.x file is detected and converted to the
        v1.x schema on a best-effort basis, raising a ``UserWarning``. See
        :func:`parse_bpx_obj`.

    Returns
    -------
    BPX: :class:`bpx.BPX`
        a parsed BPX model
    """
    if str(filename).endswith((".yml", ".yaml")):
        with Path(filename).open(encoding="utf-8") as f:
            bpx = yaml.safe_load(f)
    else:
        with Path(filename).open(encoding="utf-8") as f:
            bpx = json.loads(f.read())

    return parse_bpx_obj(bpx, v_tol, convert_legacy=convert_legacy)


def parse_bpx_str(
    bpx: str,
    v_tol: float = 0.001,
    *,
    convert_legacy: bool = True,
) -> BPX:
    """
    A convenience function to parse a json formatted string in bpx format into a BPX
    model.

    Parameters
    ----------
    bpx: str
        a json formatted string in bpx format
    v_tol: float
        absolute tolerance in [V] to validate the voltage limits, 1 mV by default
    convert_legacy: bool
        if True (default), a legacy BPX v0.x object is detected and converted to
        the v1.x schema on a best-effort basis, raising a ``UserWarning``. See
        :func:`parse_bpx_obj`.

    Returns
    -------
    BPX:
        a parsed BPX model
    """
    bpx = json.loads(bpx)
    return parse_bpx_obj(bpx, v_tol, convert_legacy=convert_legacy)
