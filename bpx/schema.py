from __future__ import annotations

import re
import warnings
from typing import Any, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError, field_validator, model_validator

from bpx import Function, InterpolatedTable

from .base_extra_model import ExtraBaseModel
from .validators import check_sto_limits

FloatFunctionTable = Union[float, int, Function, InterpolatedTable]
FloatInt = Union[float, int]


class Header(ExtraBaseModel):
    """
    The header of a BPX file. Contains metadata about the file (e.g. BPX version,
    title, description).
    """

    bpx: str = Field(
        alias="BPX",
        examples=["1.0.0"],
        description="BPX format version",
        # Update this pattern to make the patch number required once the deprecation warning is removed
        pattern=r"^\d+\.\d+(?:\.\d+)?$",
    )
    title: str = Field(
        None,
        alias="Title",
        examples=["Parameterisation example"],
        description="LGM50 battery parametrisation",
    )
    description: str = Field(
        None,
        alias="Description",
        description=("May contain additional cell description such as form factor"),
        examples=["Pouch cell (191mm x 88mm x 7.6mm)"],
    )
    references: str = Field(
        None,
        alias="References",
        description=("May contain any references"),
        examples=["Chang-Hui Chen et al 2020 J. Electrochem. Soc. 167 080534"],
    )
    model: Literal["SPM", "SPMe", "DFN"] = Field(
        alias="Model",
        examples=["DFN"],
        description=('Model type ("SPM", "SPMe", "DFN")'),
    )

    @field_validator("bpx", mode="before")
    @classmethod
    def _validate_bpx_version(cls, value: str | float) -> str:
        """
        Warns users with old files that 'bpx' should now be a string.
        Temporarily converts float to string for compatibility.
        """
        if isinstance(value, float):
            value = f"{value:.1f}"
            warnings.warn(
                "The 'bpx' field now expects the BPX semantic version as a string (e.g. '0.5.0'), not a float. "
                "This format is temporarily supported but will be removed in a future version. "
                "Please update your file accordingly.",
                DeprecationWarning,
                stacklevel=2,
            )
        return value


class Cell(ExtraBaseModel):
    """
    Cell-level parameters that are not specific to any individual component (electrode,
    separator, or electrolyte).
    """

    electrode_area: FloatInt = Field(
        alias="Electrode area [m2]",
        description="Electrode cross-sectional area",
        examples=[1.68e-2],
    )
    external_surface_area: FloatInt = Field(
        None,
        alias="External surface area [m2]",
        examples=[3.78e-2],
        description="External surface area of cell",
    )
    volume: FloatInt = Field(
        None,
        alias="Volume [m3]",
        examples=[1.27e-4],
        description="Volume of the cell",
    )
    number_of_electrodes: int = Field(
        alias="Number of electrode pairs connected in parallel to make a cell",
        examples=[1],
        description=("Number of electrode pairs connected in parallel to make a cell"),
    )
    lower_voltage_cutoff: FloatInt = Field(
        alias="Lower voltage cut-off [V]",
        description="Minimum allowed voltage",
        examples=[2.0],
    )
    upper_voltage_cutoff: FloatInt = Field(
        alias="Upper voltage cut-off [V]",
        description="Maximum allowed voltage",
        examples=[4.4],
    )
    nominal_cell_capacity: FloatInt = Field(
        alias="Nominal cell capacity [A.h]",
        description=("Nominal cell capacity. Used to convert between current and C-rate."),
        examples=[5.0],
    )
    reference_temperature: FloatInt = Field(
        None,
        alias="Reference temperature [K]",
        description=("Reference temperature for the Arrhenius temperature dependence"),
        examples=[298.15],
    )
    density: FloatInt = Field(
        None,
        alias="Density [kg.m-3]",
        examples=[1000.0],
        description="Density (lumped)",
    )
    specific_heat_capacity: FloatInt = Field(
        None,
        alias="Specific heat capacity [J.K-1.kg-1]",
        examples=[1000.0],
        description="Specific heat capacity (lumped)",
    )
    thermal_conductivity: FloatInt = Field(
        None,
        alias="Thermal conductivity [W.m-1.K-1]",
        examples=[1.0],
        description="Thermal conductivity (lumped)",
    )


class Electrolyte(ExtraBaseModel):
    """
    Electrolyte parameters.
    """

    cation_transference_number: FloatInt = Field(
        alias="Cation transference number",
        examples=[0.259],
        description="Cation transference number",
    )
    diffusivity: FloatFunctionTable = Field(
        alias="Diffusivity [m2.s-1]",
        examples=["8.794e-7 * x * x - 3.972e-6 * x + 4.862e-6"],
        description=("Lithium ion diffusivity in electrolyte (constant or function of concentration)"),
    )
    diffusivity_activation_energy: FloatInt = Field(
        None,
        alias="Diffusivity activation energy [J.mol-1]",
        examples=[17100],
        description="Activation energy for diffusivity in electrolyte",
    )
    conductivity: FloatFunctionTable = Field(
        alias="Conductivity [S.m-1]",
        examples=[1.0],
        description=("Electrolyte conductivity (constant or function of concentration)"),
    )
    conductivity_activation_energy: FloatInt = Field(
        None,
        alias="Conductivity activation energy [J.mol-1]",
        examples=[17100],
        description="Activation energy for conductivity in electrolyte",
    )


class ContactBase(ExtraBaseModel):
    """
    Base class for parameters that are common to electrode and separator components.
    """

    thickness: FloatInt = Field(
        alias="Thickness [m]",
        examples=[85.2e-6],
        description="Contact thickness",
    )


class Contact(ContactBase):
    """
    Class for parameters that are common to electrode and separator components.
    """

    porosity: FloatInt = Field(
        alias="Porosity",
        examples=[0.47],
        description="Electrolyte volume fraction (porosity)",
    )
    transport_efficiency: FloatInt = Field(
        alias="Transport efficiency",
        examples=[0.3222],
        description="Transport efficiency / inverse MacMullin number",
    )


class Particle(ExtraBaseModel):
    """
    Class for particle parameters.
    """

    minimum_stoichiometry: FloatInt = Field(
        alias="Minimum stoichiometry",
        examples=[0.1],
        description="Minimum stoichiometry",
    )
    maximum_stoichiometry: FloatInt = Field(
        alias="Maximum stoichiometry",
        examples=[0.9],
        description="Maximum stoichiometry",
    )
    maximum_concentration: FloatInt = Field(
        alias="Maximum concentration [mol.m-3]",
        examples=[63104.0],
        description="Maximum concentration of lithium ions in particles",
    )
    particle_radius: FloatInt = Field(
        alias="Particle radius [m]",
        examples=[5.86e-6],
        description="Particle radius",
    )
    surface_area_per_unit_volume: FloatInt = Field(
        alias="Surface area per unit volume [m-1]",
        examples=[382184],
        description="Particle surface area per unit of volume",
    )
    diffusivity: FloatFunctionTable = Field(
        alias="Diffusivity [m2.s-1]",
        examples=["3.3e-14"],
        description=("Lithium ion diffusivity in particle (constant or function of stoichiometry)"),
    )
    diffusivity_activation_energy: FloatInt = Field(
        None,
        alias="Diffusivity activation energy [J.mol-1]",
        examples=[17800],
        description="Activation energy for diffusivity in particles",
    )
    ocp: FloatFunctionTable = Field(
        alias="OCP [V]",
        examples=[{"x": [0, 0.1, 1], "y": [1.72, 1.2, 0.06]}],
        description=("Open-circuit potential (OCP) at the reference temperature, function of particle stoichiometry"),
    )
    dudt: FloatFunctionTable = Field(
        None,
        alias="Entropic change coefficient [V.K-1]",
        examples=[{"x": [0, 0.1, 1], "y": [-9e-18, -9e-15, -1e-5]}],
        description=("Entropic change coefficient, function of particle stoichiometry"),
    )
    reaction_rate_constant: FloatInt = Field(
        alias="Reaction rate constant [mol.m-2.s-1]",
        examples=[1e-10],
        description="Normalised reaction rate K (see notes)",
    )
    reaction_rate_constant_activation_energy: FloatInt = Field(
        None,
        alias="Reaction rate constant activation energy [J.mol-1]",
        examples=[27010],
        description="Activation energy of reaction rate constant in particles",
    )


class Electrode(Contact):
    """
    Class for electrode parameters.
    """

    conductivity: FloatInt = Field(
        alias="Conductivity [S.m-1]",
        examples=[0.18],
        description=("Effective electronic conductivity of the porous electrode matrix (constant)"),
    )


class ElectrodeSingle(Electrode, Particle):
    """
    Class for electrode composed of a single active material.
    """


class ElectrodeBlended(Electrode):
    """
    Class for electrode composed of a blend of active materials.
    """

    particle: dict[str, Particle] = Field(alias="Particle")


class ElectrodeSingleSPM(ContactBase, Particle):
    """
    Class for electrode composed of a single active material, for use with Single
    Particle type models.
    """


class ElectrodeBlendedSPM(ContactBase):
    """
    Class for electrode composed of a blend of active materials, for use with Single
    Particle type models.
    """

    particle: dict[str, Particle] = Field(alias="Particle")


class UserDefined(BaseModel):
    model_config = ConfigDict(extra="allow")

    description: str | None = None

    @model_validator(mode="before")
    @classmethod
    def validate(cls, values: dict) -> dict:
        def convert_and_validate(values: dict) -> dict:
            new_values = {}
            for k, v in values.items():
                # Convert to Function or InterpolatedTable
                if k == "description":
                    new_values[k] = v
                elif isinstance(v, str):
                    new_values[k] = Function.validate(v)  # validate the string
                elif isinstance(v, dict):
                    try:
                        new_values[k] = InterpolatedTable(**v)
                    except ValidationError as e:
                        # If it fails, check if all the values are lists (probably malformed table)
                        if all(isinstance(val, list) for val in v.values()):
                            raise e from e
                        # otherwise assume nested data and recurse
                        new_values[k] = convert_and_validate(v)
                elif isinstance(v, float | int) and not isinstance(v, bool):
                    new_values[k] = v
                else:
                    error_msg = f"{k} must be of type 'FloatFunctionTable'"
                    raise TypeError(error_msg)
            return new_values

        return convert_and_validate(values)


class Experiment(ExtraBaseModel):
    """
    A class to store experimental data (time, current, voltage, temperature).
    """

    time: list[FloatInt] = Field(
        alias="Time [s]",
        examples=[[0, 0.1, 0.2, 0.3, 0.4]],
        description="Time in seconds (list of FloatInts)",
    )
    current: list[FloatInt] = Field(
        alias="Current [A]",
        examples=[[-5, -5, -5, -5, -5]],
        description="Current vs time",
    )
    voltage: list[FloatInt] = Field(
        alias="Voltage [V]",
        examples=[[4.2, 4.1, 4.0, 3.9, 3.8]],
        description="Voltage vs time",
    )
    temperature: list[FloatInt] = Field(
        None,
        alias="Temperature [K]",
        examples=[[298, 298, 298, 298, 298]],
        description="Temperature vs time",
    )


class Parameterisation(ExtraBaseModel):
    """
    A class to store parameterisation data for a cell. Consists of parameters for the
    cell, electrolyte, negative electrode, positive electrode, and separator.
    """

    cell: Cell = Field(
        alias="Cell",
    )
    electrolyte: Electrolyte = Field(
        alias="Electrolyte",
    )
    negative_electrode: Union[ElectrodeSingle, ElectrodeBlended] = Field(
        alias="Negative electrode",
    )
    positive_electrode: Union[ElectrodeSingle, ElectrodeBlended] = Field(
        alias="Positive electrode",
    )
    separator: Contact = Field(
        alias="Separator",
    )
    user_defined: UserDefined = Field(
        None,
        alias="User-defined",
    )

    @field_validator("negative_electrode", "positive_electrode", mode="before")
    @classmethod
    def _choose_electrode_type(cls, data: dict) -> dict:
        if data.get("Particle"):
            return ElectrodeBlended.model_validate(data)
        return ElectrodeSingle.model_validate(data)

    @model_validator(mode="after")
    def _sto_limit_validation(self) -> Parameterisation:
        return check_sto_limits(self)


class ParameterisationSPM(ExtraBaseModel):
    """
    A class to store parameterisation data for a cell. Consists of parameters for the
    cell, electrolyte, negative electrode, and positive electrode. This class stores the
    parameters needed for Single Particle type models.
    """

    cell: Cell = Field(
        alias="Cell",
    )
    negative_electrode: Union[ElectrodeSingleSPM, ElectrodeBlendedSPM] = Field(
        alias="Negative electrode",
    )
    positive_electrode: Union[ElectrodeSingleSPM, ElectrodeBlendedSPM] = Field(
        alias="Positive electrode",
    )
    user_defined: UserDefined = Field(
        None,
        alias="User-defined",
    )

    @field_validator("negative_electrode", "positive_electrode", mode="before")
    @classmethod
    def _choose_electrode_type(cls, data: dict) -> dict:
        if data.get("Particle"):
            return ElectrodeBlendedSPM.model_validate(data)
        return ElectrodeSingleSPM.model_validate(data)

    @model_validator(mode="after")
    def _sto_limit_validation(self) -> ParameterisationSPM:
        return check_sto_limits(self)


class InitialConditions(ExtraBaseModel):
    """
    A class to store the initial state of a battery (e.g. initial state of charge).
    """

    model_config = ConfigDict(extra="allow")

    initial_soc: FloatInt = Field(
        alias="Initial state-of-charge",
        examples=[0.5],
        description=("Initial state of charge of the battery (between 0 and 1)"),
    )

    initial_temperature: FloatInt = Field(
        None,
        alias="Initial temperature [K]",
        examples=[298.15],
    )

    initial_electrolyte_concentration: FloatInt = Field(
        alias="Initial electrolyte concentration [mol.m-3]",
        examples=[1000],
        description=("Initial / rest lithium ion concentration in the electrolyte"),
    )

    @model_validator(mode="before")
    @classmethod
    def _validate_hysteresis_key_names(cls, data: dict) -> dict:
        _hyst_key_re = re.compile(r"^Initial hysteresis state:\s*([^:]+?)(?:\s*:\s*([^:]+?))?\s*$")
        _floatint_adapter = TypeAdapter(FloatInt)

        if not isinstance(data, dict):
            return data

        out = dict(data)

        for k, v in data.items():
            if k in [
                "Initial state-of-charge",
                "Initial temperature [K]",
                "Initial electrolyte concentration [mol.m-3]",
            ]:
                continue
            if not (isinstance(k, str) and k.startswith("Initial hysteresis state:")):
                msg = f'Unexpected key in "InitialConditions": {k!r}.'
                raise ValueError(msg)

            if not re.match(_hyst_key_re, k):
                msg = (
                    f'Invalid key in "InitialConditions": {k!r}. '
                    'Expected "Initial hysteresis state: <Electrode>" or '
                    '"Initial hysteresis state: <Electrode>: <Material>".'
                )
                raise ValueError(msg)

            try:
                out[k] = _floatint_adapter.validate_python(v)
            except ValidationError as e:
                msg = f'Invalid value in "InitialConditions" ({k!r}: {v!r}). Expected FloatInt.'
                raise ValueError(msg) from e

        return data


class ThermalState(ExtraBaseModel):
    """
    A class to store the thermal state of a battery (e.g. initial temperature).
    """

    ambient_temperature: FloatInt = Field(
        alias="Ambient temperature [K]",
        examples=[298.15],
    )


class Degradation(ExtraBaseModel):
    """
    A class to store the degradation state of a battery.
    """

    model_config = ConfigDict(extra="allow")

    lli: FloatInt = Field(
        alias="LLI",
    )

    @model_validator(mode="before")
    @classmethod
    def _validate_lam_key_names(cls, data: dict) -> dict:
        _lam_key_re = re.compile(r"^LAM\s*:\s*([^:]+?)(?:\s*:\s*([^:]+?))?\s*$")
        _floatint_adapter = TypeAdapter(FloatInt)

        if not isinstance(data, dict):
            return data

        out = dict(data)

        for k, v in data.items():
            if k == "LLI":
                continue
            if not (isinstance(k, str) and k.startswith("LAM:")):
                msg = f'Unexpected key in "Degradation": {k!r}. Only "LLI" and keys starting with "LAM:" are allowed.'
                raise ValueError(msg)

            if not re.match(_lam_key_re, k):
                msg = (
                    f'Invalid key in "Degradation": {k!r}. '
                    'Expected "LAM: <Electrode>" or "LAM: <Electrode>: <Material>".'
                )
                raise ValueError(msg)

            try:
                out[k] = _floatint_adapter.validate_python(v)
            except ValidationError as e:
                msg = f'Invalid value in "Degradation" ({k!r}: {v!r}). Expected FloatInt.'
                raise ValueError(msg) from e

        return data


class State(ExtraBaseModel):
    """
    A class to store a battery state (e.g. initial state of charge).
    """

    initial_conditions: InitialConditions = Field(
        alias="Initial conditions",
    )

    thermal_state: ThermalState = Field(
        alias="Thermal state",
    )

    degradation: Degradation = Field(
        None,
        alias="Degradation",
    )


class BPX(ExtraBaseModel):
    """
    A class to store a BPX model. Consists of a header, parameterisation, and optional
    validation data.
    """

    header: Header = Field(alias="Header")
    parameterisation: Union[ParameterisationSPM, Parameterisation] = Field(alias="Parameterisation")
    state: State = Field(alias="State")
    validation: dict[str, Experiment] = Field(None, alias="Validation")

    @model_validator(mode="before")
    @classmethod
    def _dispatch_param_subclasses(cls, data: Any) -> Any:  # noqa:ANN401
        if isinstance(data, dict):
            # validate header first, checks that the model type is valid
            header = Header.model_validate(data.get("Header"))
            model_type = header.model

            # Choose the expected class based on model type
            if model_type == "SPM":
                expected_cls, fallback_cls = ParameterisationSPM, Parameterisation
                error_msg = f"Valid parameter set does not correspond with the model type {model_type}"
            else:
                expected_cls, fallback_cls = Parameterisation, ParameterisationSPM
                error_msg = f"Valid SPM parameter set does not correspond with the model type {model_type}"

            try:
                parameterisation = expected_cls.model_validate(data["Parameterisation"])
            except ValidationError as e:
                try:
                    fallback_cls.model_validate(data["Parameterisation"])
                    raise ValueError(error_msg) from e
                except ValidationError:
                    raise e from None

            # return validated data to stop double validation
            data["Header"] = header
            data["Parameterisation"] = parameterisation
        return data

    @model_validator(mode="after")
    def _validate_state_against_electrodes(self) -> BPX:
        """
        Enforce that for state variables which identify an electrode and optionally a
        material:
          * For blended electrodes, 'x: Electrode: Material' is required and
            'Material' must be a key in `ElectrodeBlended.particle`.
          * For single-material electrodes, 'x: Electrode' must omit material.
        """
        # If 'State' is missing, nothing to do
        state = getattr(self, "State", None)
        params = getattr(self, "Parameterisation", None)
        if state is None:
            return self

        def materials_for_electrode(e: dict) -> set[str] | None:
            # blended types have a 'particle' dict[str, Particle]
            part = getattr(e, "particle", None)
            if isinstance(part, dict) and part:
                return set(part.keys())  # blended electrode
            return None  # single material

        elec_map = {
            "Negative electrode": materials_for_electrode(params.negative_electrode),
            "Positive electrode": materials_for_electrode(params.positive_electrode),
        }
        # flatten this and turn into a set of names to check all keys match.

        deg_keys = state.degradation.model_extra.keys() if state.degradation.model_extra else []
        init_keys = state.initial_conditions.model_extra.keys() if state.initial_conditions.model_extra else []

        extras = deg_keys | init_keys

        for raw_key in extras:
            electrode, material = (raw_key.group(1).strip(), (raw_key.group(2) or None))
            if electrode not in elec_map:
                msg = (
                    f"Key '{raw_key!r}' refers to unknown electrode '{electrode}'. "
                    f"Expected one of {list(elec_map.keys())}."
                )
                raise ValueError(msg)

            allowed_materials = elec_map[electrode]

            if allowed_materials is None:
                # Single-material electrode: material must be omitted
                if material is not None:
                    msg = (
                        f"Key '{raw_key!r}' must omit ': {material}' because '{electrode}' "
                        "is a single-material electrode."
                    )
                    raise ValueError(msg)
            else:
                # Blended electrode: material is required and must match particle keys
                if material is None:
                    msg = f"Key '{raw_key!r}' must include ': material' because '{electrode}' has multiple materials."
                    raise ValueError(msg)
                if material not in allowed_materials:
                    msg = (
                        f'LAM key {raw_key!r} uses unknown material "{material}" for "{electrode}". '
                        f"Allowed materials: {sorted(allowed_materials)}."
                    )
                    raise ValueError(msg)

        return self
