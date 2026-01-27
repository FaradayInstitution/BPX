from __future__ import annotations

import warnings
from typing import Any, Literal, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

from bpx import Function, InterpolatedTable

from .base_extra_model import ExtraBaseModel
from .schema_utils import BPXSchemaError, get_materials_in_electrode, validate_section_against_electrodes
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
    model: Literal["SPM", "SPMe", "DFN", "Partial"] = Field(
        alias="Model",
        examples=["DFN"],
        description=('Model type ("SPM", "SPMe", "DFN", "Partial")'),
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

    @model_validator(mode="before")
    @classmethod
    def _validate_thermal_conductivity(cls, data: dict) -> dict:
        """
        Validates that thermal_conductivity is not provided in the Cell section.
        If provided, raises an error directing users to the User-defined section.
        """
        if isinstance(data, dict) and "Thermal conductivity [W.m-1.K-1]" in data:
            error_message = (
                "The 'Thermal conductivity [W.m-1.K-1]' field is not part of the BPX schema. "
                "Please provide this parameter in the 'User-defined' section instead."
            )
            raise ValueError(error_message)
        return data

    @model_validator(mode="before")
    @classmethod
    def _validate_temperatures_not_in_cell(cls, data: dict) -> dict:
        """
        Validates that initial/ambient temperatures are not provided in the Cell section.
        If provided, raises an error directing users to the State section.
        """
        if isinstance(data, dict) and any(
            field in data for field in ["Initial temperature [K]", "Ambient temperature [K]"]
        ):
            error_message = (
                "The 'Initial temperature [K]' and 'Ambient temperature [K]' fields have been moved. "
                "Please provide these parameters in 'State.InitialConditions' and "
                "'State.ThermalState' sections respectively."
            )
            raise ValueError(error_message)
        return data


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

    @model_validator(mode="before")
    @classmethod
    def _validate_initial_concentration(cls, data: dict) -> dict:
        """
        Validates that initial concentration is not provided in the Electrolyte section.
        If provided, raises an error directing users to the State section.
        """
        if isinstance(data, dict) and "Initial concentration [mol.m-3]" in data:
            error_message = (
                "'Initial concentration [mol.m-3]' has been renamed and moved. "
                "Please provide this parameter as 'Initial electrolyte concentration [mol.m-3]'"
                " in the 'State.InitialConditions' section instead."
            )
            raise ValueError(error_message)
        return data


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
    ocp_delith: FloatFunctionTable = Field(
        None,
        alias="OCP (delithiation) [V]",
        examples=[{"x": [0, 0.1, 1], "y": [1.72, 1.2, 0.06]}],
        description=(
            "Open-circuit potential (OCP) of the delithiation branch at the reference temperature, "
            "function of particle stoichiometry"
        ),
    )
    ocp_lith: FloatFunctionTable = Field(
        None,
        alias="OCP (lithiation) [V]",
        examples=[{"x": [0, 0.1, 1], "y": [1.72, 1.2, 0.06]}],
        description=(
            "Open-circuit potential (OCP) of the lithiation branch at the reference temperature, "
            "function of particle stoichiometry"
        ),
    )
    gamma_hys: FloatInt = Field(
        None,
        alias="OCP hysteresis decay constant",
        examples=[0.01],
        description="OCP hysteresis decay constant in a single-state hysteresis model",
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


class ParameterisationPartial(ExtraBaseModel):
    """
    A class to store parameterisation data for a cell. Consists of parameters for the
    cell, electrolyte, negative electrode, positive electrode, and separator.
    All parameter groups are optional to allow for partial parameterisations; as such either
    SPM or full models can be represented (but not within the same instance).
    """

    cell: Cell = Field(
        None,
        alias="Cell",
    )
    electrolyte: Electrolyte = Field(
        None,
        alias="Electrolyte",
    )
    negative_electrode: Union[
        ElectrodeSingle,
        ElectrodeBlended,
        ElectrodeSingleSPM,
        ElectrodeBlendedSPM,
    ] = Field(
        None,
        alias="Negative electrode",
    )
    positive_electrode: Union[
        ElectrodeSingle,
        ElectrodeBlended,
        ElectrodeSingleSPM,
        ElectrodeBlendedSPM,
    ] = Field(
        None,
        alias="Positive electrode",
    )
    separator: Contact = Field(
        None,
        alias="Separator",
    )
    user_defined: UserDefined = Field(
        None,
        alias="User-defined",
    )

    @field_validator("negative_electrode", "positive_electrode", mode="before")
    @classmethod
    def _choose_electrode_type(cls, data: dict) -> dict:
        """Use the 'conductivity' parameter to differentiate between SPM and full electrode types."""
        if data.get("Particle") and data.get("Conductivity [S.m-1]"):
            return ElectrodeBlended.model_validate(data)
        if data.get("Particle"):
            return ElectrodeBlendedSPM.model_validate(data)
        if data.get("Conductivity [S.m-1]"):
            return ElectrodeSingle.model_validate(data)
        return ElectrodeSingleSPM.model_validate(data)

    @model_validator(mode="after")
    def _check_consistent_electrode_types(self) -> Parameterisation:
        if self.negative_electrode and self.positive_electrode:
            neg_is_spm = isinstance(
                self.negative_electrode,
                (ElectrodeSingleSPM | ElectrodeBlendedSPM),
            )
            pos_is_spm = isinstance(
                self.positive_electrode,
                (ElectrodeSingleSPM | ElectrodeBlendedSPM),
            )
            if neg_is_spm != pos_is_spm:
                error_msg = (
                    "Negative and positive electrodes must be of consistent model types. Currently types are: "
                    f"Positive electrode: {type(self.positive_electrode)}, "
                    f"Negative electrode: {type(self.negative_electrode)}"
                )
                raise ValueError(error_msg)
        return self

    @model_validator(mode="after")
    def _check_consistent_electrode_models(self) -> Parameterisation:
        """Check that if SPM electrodes are used, no full model parameters are present."""
        neg_is_spm = self.negative_electrode and isinstance(
            self.negative_electrode,
            (ElectrodeSingleSPM | ElectrodeBlendedSPM),
        )
        pos_is_spm = self.positive_electrode and isinstance(
            self.positive_electrode,
            (ElectrodeSingleSPM | ElectrodeBlendedSPM),
        )

        if any([neg_is_spm, pos_is_spm]):
            full_model_params = Parameterisation.model_fields.keys() - ParameterisationSPM.model_fields.keys()
            if any(field in self.model_fields_set for field in full_model_params):
                error_msg = (
                    f"SPM electrodes cannot be used with full model parameters {sorted(full_model_params)}. "
                    "Please ensure that either full model electrodes are used, or that "
                    "only valid SPM parameters are provided."
                )
                raise ValueError(error_msg)
        return self

    @model_validator(mode="after")
    def _sto_limit_validation(self) -> Parameterisation:
        return check_sto_limits(self)


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
    initial_soc: FloatInt = Field(
        alias="Initial state-of-charge",
        examples=[0.5],
        description=("Initial state of charge of the battery (between 0 and 1)"),
    )

    initial_temperature: FloatInt = Field(
        alias="Initial temperature [K]",
        examples=[298.15],
    )

    initial_electrolyte_concentration: FloatInt = Field(
        alias="Initial electrolyte concentration [mol.m-3]",
        examples=[1000],
        description=("Initial / rest lithium ion concentration in the electrolyte"),
    )

    initial_hysteresis_state_positive: FloatInt | dict[str, FloatInt] = Field(
        alias="Initial hysteresis state: Positive electrode",
        examples=[1.0, {"Primary": 1.0, "Secondary": 5.0}],
        description=("Initial hysteresis state for positive electrode"),
        json_schema_extra={"material_check": "positive_electrode"},
    )

    initial_hysteresis_state_negative: FloatInt | dict[str, FloatInt] = Field(
        alias="Initial hysteresis state: Negative electrode",
        examples=[1.0, {"Primary": 1.0, "Secondary": 5.0}],
        description=("Initial hysteresis state for negative electrode"),
        json_schema_extra={"material_check": "negative_electrode"},
    )


class ThermalState(ExtraBaseModel):
    ambient_temperature: FloatInt = Field(
        alias="Ambient temperature [K]",
        examples=[298.15],
    )

    heat_transfer_coefficient: FloatInt = Field(
        alias="Heat transfer coefficient [W.m-2.K-1]",
        examples=[10.0],
    )


class Degradation(ExtraBaseModel):
    lli: FloatInt = Field(
        alias="LLI",
    )

    lam_positive: FloatInt | dict[str, FloatInt] = Field(
        alias="LAM: Positive electrode",
        json_schema_extra={"material_check": "positive_electrode"},
    )

    lam_negative: FloatInt | dict[str, FloatInt] = Field(
        alias="LAM: Negative electrode",
        json_schema_extra={"material_check": "negative_electrode"},
    )


class State(ExtraBaseModel):
    initial_conditions: InitialConditions = Field(
        alias="Initial conditions",
    )

    thermal_environment: ThermalState = Field(
        alias="Thermal environment",
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

    header: Header = Field(
        alias="Header",
    )
    parameterisation: Union[ParameterisationSPM, Parameterisation, ParameterisationPartial] = Field(
        alias="Parameterisation",
    )
    state: State = Field(None, alias="State")
    validation: dict[str, Experiment] = Field(None, alias="Validation")

    @model_validator(mode="before")
    @classmethod
    def _dispatch_param_subclasses(cls, data: Any) -> Any:  # noqa:ANN401
        if isinstance(data, dict):
            # validate header first, checks that the model type is valid
            header = Header.model_validate(data.get("Header"))
            model_type = header.model

            if model_type == "Partial":
                parameterisation = ParameterisationPartial.model_validate(data["Parameterisation"])
                # return validated data to stop double validation
                data["Header"] = header
                data["Parameterisation"] = parameterisation
                return data

            # Choose the expected class based on model type
            if model_type == "SPM":
                expected_cls, fallback_cls = ParameterisationSPM, Parameterisation
                error_msg = f"Valid parameter set does not correspond with the model type {model_type}"
            else:  # DFN or SPMe
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
    def _check_state_present_if_not_partial(self) -> BPX:
        """
        Check that State is provided if not using a Partial parameterisation.
        """
        if self.state is None and self.header.model != "Partial":
            err_msg = "'State' section must be provided unless using a 'Partial' parameterisation"
            raise BPXSchemaError(err_msg)
        return self

    @model_validator(mode="after")
    def _check_state_against_blended_electrodes(self) -> BPX:
        """
        Check that if blended electrodes are used, values which require per-material
        values in State are provided as such (and vice versa).
        """

        if self.state is None:
            return self  # skip if no State provided (Partial parameterisation)

        param = self.parameterisation

        electrode_materials = {
            "negative_electrode": get_materials_in_electrode(param.negative_electrode),
            "positive_electrode": get_materials_in_electrode(param.positive_electrode),
        }

        validate_section_against_electrodes(
            self.state.initial_conditions,
            "Initial conditions",
            electrode_materials,
        )
        if self.state.degradation is not None:
            validate_section_against_electrodes(
                self.state.degradation,
                "Degradation",
                electrode_materials,
            )

        return self
