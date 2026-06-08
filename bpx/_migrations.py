"""
Best-effort conversion of legacy BPX v0.x objects to the BPX v1.x schema.

BPX v1.0 added a top-level ``State`` block and moved the initial/ambient
temperature and initial electrolyte concentration out of ``Parameterisation``,
so v0.x files no longer validate against the current schema. These helpers
detect a v0.x object and repack it into the v1.x layout so older files keep
loading.
"""

from __future__ import annotations

import copy
import re

# Electrode prefixes for the synthesised hysteresis state.
_ELECTRODES = ("Negative", "Positive")


def _first_not_none(*values: float | None, default: float) -> float:
    """Return the first value that is not ``None``, or ``default`` if all are."""
    return next((value for value in values if value is not None), default)


def _bpx_major_version(bpx_obj: dict) -> int:
    """
    Return the major version of a raw BPX object's ``Header.BPX`` field.

    The version may be encoded as a number (e.g. ``0.4`` or ``1.0`` in older
    files) or as a string (e.g. ``"0.4.0"`` or ``"1.1.0"``). Both forms are
    accepted; ``bpx`` itself coerces a float version to a string for backward
    compatibility, so a float does not by itself indicate a v0.x file.
    """
    try:
        version = bpx_obj["Header"]["BPX"]
    except (KeyError, TypeError) as err:
        msg = "Invalid BPX object: missing 'Header' -> 'BPX' version field."
        raise ValueError(msg) from err

    if isinstance(version, str):
        match = re.match(r"^\s*(\d+)", version)
        if match is not None:
            return int(match.group(1))
    # bool is a subclass of int but is never a valid version
    elif isinstance(version, (int, float)) and not isinstance(version, bool):
        return int(version)

    msg = f"Invalid BPX version field: {version!r}."
    raise ValueError(msg)


def is_legacy_bpx(bpx_obj: dict) -> bool:
    """
    Return ``True`` if ``bpx_obj`` is a legacy BPX v0.x object (major version
    ``< 1``), and ``False`` for v1.x and later.

    Raises ``ValueError`` if the version field is missing or malformed.
    """
    return _bpx_major_version(bpx_obj) < 1


def convert_v0_to_v1(bpx_obj: dict) -> dict:
    """
    Return a new dict repacking a legacy BPX v0.x object into the v1.x schema
    (the input is not mutated).

    The v1.x ``State`` block is synthesised from the v0.x ``Parameterisation``
    entries, with placeholders for the required fields v0.x lacks: initial SOC
    set to ``1``, heat transfer coefficient and initial hysteresis state set to
    ``0`` (the lumped ``Thermal conductivity`` has no v1.x equivalent and is
    dropped), the ambient and initial temperatures resolved from whichever of
    ambient/initial/reference temperature the file provides (defaulting to
    ``298.15`` K only if none are present), and initial electrolyte concentration
    falling back to ``1000`` mol.m-3 (1 M) when absent (e.g. SPM files that have
    no ``Electrolyte`` section). Cross-version semantic changes are not adjusted.
    """
    params = copy.deepcopy(bpx_obj)
    parameterisation = params.get("Parameterisation", {})
    cell = parameterisation.get("Cell", {})
    electrolyte = parameterisation.get("Electrolyte", {})

    # Reference temperature stays in Cell under v1.x, so read it without popping.
    ambient_temperature = cell.pop("Ambient temperature [K]", None)
    reference_temperature = cell.get("Reference temperature [K]")
    initial_temperature = cell.pop("Initial temperature [K]", None)

    # v1.x requires both an ambient and an initial temperature in State. Resolve
    # each through the temperatures a v0.x file does provide, defaulting to
    # 298.15 K only if none are present (reference temperature is itself optional
    # in v1.x). ``is not None`` rather than truthiness so a literal 0 is kept.
    ambient_temperature = _first_not_none(ambient_temperature, reference_temperature, default=298.15)
    initial_temperature = _first_not_none(initial_temperature, ambient_temperature, default=298.15)

    # Drop the deprecated lumped thermal conductivity (no v1.x equivalent).
    cell.pop("Thermal conductivity [W.m-1.K-1]", None)

    initial_conditions: dict = {
        "Initial state-of-charge": 1,
        "Initial temperature [K]": initial_temperature,
    }

    # Required in v1.x; fall back to 1 M when absent (e.g. SPM files with no
    # Electrolyte section). See https://github.com/FaradayInstitution/BPX/issues/127.
    initial_electrolyte_concentration = electrolyte.pop(
        "Initial concentration [mol.m-3]",
        None,
    )
    initial_conditions["Initial electrolyte concentration [mol.m-3]"] = (
        initial_electrolyte_concentration if initial_electrolyte_concentration is not None else 1000
    )

    # Placeholder hysteresis state; blended electrodes need a per-phase dict.
    for electrode in _ELECTRODES:
        electrode_params = parameterisation.get(f"{electrode} electrode", {})
        key = f"Initial hysteresis state: {electrode} electrode"
        if "Particle" in electrode_params:
            initial_conditions[key] = dict.fromkeys(electrode_params["Particle"], 0)
        else:
            initial_conditions[key] = 0

    thermal_environment: dict = {
        "Heat transfer coefficient [W.m-2.K-1]": 0,
        "Ambient temperature [K]": ambient_temperature,
    }

    params["State"] = {
        "Initial conditions": initial_conditions,
        "Thermal environment": thermal_environment,
    }

    params.setdefault("Header", {})["BPX"] = "1.0.0"

    return params
