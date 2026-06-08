"""
Best-effort conversion of legacy BPX v0.x objects to the BPX v1.x schema.

BPX v1.0 added a top-level ``State`` block and moved the initial/ambient
temperature and initial electrolyte concentration out of ``Parameterisation``,
so v0.x files no longer validate against the current schema. These helpers
detect a v0.x object and repack it into the v1.x layout so older files keep
loading.

Adapted from the v0.x -> v1.x converter shared by Edmund Dickinson
(@ejfdickinson) in https://github.com/pybamm-team/PyBaMM/issues/5571.
"""

from __future__ import annotations

import copy
import re


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
    entries: initial SOC is set to ``1``; the ambient and initial temperatures are
    resolved from whichever of ambient/initial/reference temperature the file
    provides (defaulting to ``298.15`` K only if none are present); and the initial
    electrolyte concentration is carried across when present (the lumped
    ``Thermal conductivity`` has no v1.x equivalent and is dropped). Fields that are
    optional in v1.x and have no v0.x equivalent (initial hysteresis state, heat
    transfer coefficient, and the electrolyte concentration for SPM files with no
    ``Electrolyte`` section) are omitted rather than synthesised, leaving simulators
    to apply their own defaults. Cross-version semantic changes are not adjusted.
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

    # Optional in v1.x, but renamed and moved out of Electrolyte, so carry across
    # any value the v0.x file provides. SPM files have no Electrolyte section and
    # the field is simply omitted (simulators supply their own default).
    # See https://github.com/FaradayInstitution/BPX/issues/127.
    initial_electrolyte_concentration = electrolyte.pop(
        "Initial concentration [mol.m-3]",
        None,
    )
    if initial_electrolyte_concentration is not None:
        initial_conditions["Initial electrolyte concentration [mol.m-3]"] = initial_electrolyte_concentration

    # Initial hysteresis state and heat transfer coefficient are optional in v1.x
    # and have no v0.x equivalent, so they are left for the simulator to default
    # rather than synthesised here. See
    # https://github.com/FaradayInstitution/BPX/issues/126.
    thermal_environment: dict = {
        "Ambient temperature [K]": ambient_temperature,
    }

    params["State"] = {
        "Initial conditions": initial_conditions,
        "Thermal environment": thermal_environment,
    }

    params.setdefault("Header", {})["BPX"] = "1.0.0"

    return params
