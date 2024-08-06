import json
from typing import Optional, List, Union, Literal
from pydantic import BaseModel, Field, ValidationError, Extra
from bpx import Function, InterpolatedTable, check_sto_limits

FloatFunctionTable = Union[float, Function, InterpolatedTable]


class ExtraBaseModel(BaseModel):
    """
    A base model that forbids extra fields
    """

    class Config:
        extra = Extra.forbid

    class settings:
        """
        Class with BPX-related settings.
        It might be worth moving it to a separate file if it grows bigger.
        """

        tolerances = {
            "Voltage [V]": 1e-3,  # Absolute tolerance in [V] to validate the voltage limits
        }


class Header(ExtraBaseModel):
    """
    The header of a BPX file. Contains metadata about the file (e.g. BPX version, title, description).
    """
    bpx: float = Field(
        alias="BPX",
        example=1.0,
        description="BPX format version",
    )
    title: str = Field(
        None,
        alias="Title",
        example="Parameterisation example",
        description="LGM50 battery parametrisation",
    )
    description: str = Field(
        None,
        alias="Description",
        description="May contain additional cell description such as form factor",
        example="Pouch cell (191mm x 88mm x 7.6mm)",
    )
    references: str = Field(
        None,
        alias="References",
        description="May contain any references",
        example="Chang-Hui Chen et al 2020 J. Electrochem. Soc. 167 080534",
    )
    model: Literal["SPM", "SPMe", "DFN"] = Field(
        alias="Model",
        example="DFN",
        description='Model type ("SPM", "SPMe", "DFN")',
    )
    version: str = Field(
        None,
        alias="Version",
        example="0.1.1",
        description="BPX file version",
    )

class Cell(ExtraBaseModel):
    """
    Cell-level parameters that are not specific to any individual component (electrode, separator, or electrolyte).
    """
    electrode_area: float = Field(
        alias="Electrode area [m2]",
        description="Electrode cross-sectional area",
        example=1.68e-2,
    )
    external_surface_area: float = Field(
        None,
        alias="External surface area [m2]",
        example=3.78e-2,
        description="External surface area of cell",
    )
    volume: float = Field(
        None,
        alias="Volume [m3]",
        example=1.27e-4,
        description="Volume of the cell",
    )
    number_of_electrodes: int = Field(
        alias="Number of electrode pairs connected in parallel to make a cell",
        example=1,
        description="Number of electrode pairs connected in parallel to make a cell",
    )
    lower_voltage_cutoff: float = Field(
        alias="Lower voltage cut-off [V]",
        description="Minimum allowed voltage",
        example=2.0,
    )
    upper_voltage_cutoff: float = Field(
        alias="Upper voltage cut-off [V]",
        description="Maximum allowed voltage",
        example=4.4,
    )
    nominal_cell_capacity: float = Field(
        alias="Nominal cell capacity [A.h]",
        description="Nominal cell capacity. Used to convert between current and C-rate.",
        example=5.0,
    )
    ambient_temperature: float = Field(
        alias="Ambient temperature [K]",
        example=298.15,
    )
    initial_temperature: float = Field(
        None,
        alias="Initial temperature [K]",
        example=298.15,
    )
    reference_temperature: float = Field(
        None,
        alias="Reference temperature [K]",
        description="Reference temperature for the Arrhenius temperature dependence",
        example=298.15,
    )
    density: float = Field(
        None,
        alias="Density [kg.m-3]",
        example=1000.0,
        description="Density (lumped)",
    )
    specific_heat_capacity: float = Field(
        None,
        alias="Specific heat capacity [J.K-1.kg-1]",
        example=1000.0,
        description="Specific heat capacity (lumped)",
    )
    thermal_conductivity: float = Field(
        None,
        alias="Thermal conductivity [W.m-1.K-1]",
        example=1.0,
        description="Thermal conductivity (lumped)",
    )
class Electrolyte(ExtraBaseModel):
    """
    Electrolyte parameters.
    """
    initial_concentration: float = Field(
        alias="Initial concentration [mol.m-3]",
        example=1000,
        description="Initial / rest lithium ion concentration in the electrolyte",
    )
    cation_transference_number: float = Field(
        alias="Cation transference number",
        example=0.259,
        description="Cation transference number",
    )
    diffusivity: FloatFunctionTable = Field(
        alias="Diffusivity [m2.s-1]",
        example="8.794e-7 * x * x - 3.972e-6 * x + 4.862e-6",
        description="Lithium ion diffusivity in electrolyte (constant or function of concentration)",
    )
    diffusivity_activation_energy: float = Field(
        None,
        alias="Diffusivity activation energy [J.mol-1]",
        example=17100,
        description="Activation energy for diffusivity in electrolyte",
    )
    conductivity: FloatFunctionTable = Field(
        alias="Conductivity [S.m-1]",
        example=1.0,
        description="Electrolyte conductivity (constant or function of concentration)",
    )
    conductivity_activation_energy: float = Field(
        None,
        alias="Conductivity activation energy [J.mol-1]",
        example=17100,
        description="Activation energy for conductivity in electrolyte",
    )

class NegativeElectrode(BaseModel):
    particle_radius: float = Field(..., alias="Particle radius [m]")
    thickness: float = Field(..., alias="Thickness [m]")
    diffusivity: Union[str, float] = Field(..., alias="Diffusivity [m2.s-1]")
    ocp: Union[str, float] = Field(..., alias="OCP [V]")
    entropic_change_coefficient: Union[str, float] = Field(..., alias="Entropic change coefficient [V.K-1]")
    conductivity: float = Field(..., alias="Conductivity [S.m-1]")
    surface_area_per_unit_volume: float = Field(..., alias="Surface area per unit volume [m-1]")
    porosity: float = Field(..., alias="Porosity")
    transport_efficiency: float = Field(..., alias="Transport efficiency")
    reaction_rate_constant: float = Field(..., alias="Reaction rate constant [mol.m-2.s-1]")
    minimum_stoichiometry: float = Field(..., alias="Minimum stoichiometry")
    maximum_stoichiometry: float = Field(..., alias="Maximum stoichiometry")
    maximum_concentration: float = Field(..., alias="Maximum concentration [mol.m-3]")
    diffusivity_activation_energy: float = Field(..., alias="Diffusivity activation energy [J.mol-1]")
    reaction_rate_constant_activation_energy: float = Field(..., alias="Reaction rate constant activation energy [J.mol-1]")

class PositiveElectrode(BaseModel):
    particle_radius: float = Field(..., alias="Particle radius [m]")
    thickness: float = Field(..., alias="Thickness [m]")
    diffusivity: Union[str, float] = Field(..., alias="Diffusivity [m2.s-1]")
    ocp: Union[str, float] = Field(..., alias="OCP [V]")
    entropic_change_coefficient: Union[str, float] = Field(..., alias="Entropic change coefficient [V.K-1]")
    conductivity: float = Field(..., alias="Conductivity [S.m-1]")
    surface_area_per_unit_volume: float = Field(..., alias="Surface area per unit volume [m-1]")
    porosity: float = Field(..., alias="Porosity")
    transport_efficiency: float = Field(..., alias="Transport efficiency")
    reaction_rate_constant: float = Field(..., alias="Reaction rate constant [mol.m-2.s-1]")
    minimum_stoichiometry: float = Field(..., alias="Minimum stoichiometry")
    maximum_stoichiometry: float = Field(..., alias="Maximum stoichiometry")
    maximum_concentration: float = Field(..., alias="Maximum concentration [mol.m-3]")
    diffusivity_activation_energy: float = Field(..., alias="Diffusivity activation energy [J.mol-1]")
    reaction_rate_constant_activation_energy: float = Field(..., alias="Reaction rate constant activation energy [J.mol-1]")

class Separator(BaseModel):
    thickness: float = Field(..., alias="Thickness [m]")
    porosity: float = Field(..., alias="Porosity")
    transport_efficiency: float = Field(..., alias="Transport efficiency")

class Parameterisation(BaseModel):
    cell: Cell = Field(..., alias="Cell")
    electrolyte: Electrolyte = Field(..., alias="Electrolyte")
    negative_electrode: NegativeElectrode = Field(..., alias="Negative electrode")
    positive_electrode: PositiveElectrode = Field(..., alias="Positive electrode")
    separator: Separator = Field(..., alias="Separator")

class ValidationItem(BaseModel):
    Time: List[int] = Field(..., alias="Time [s]")
    Current: List[float] = Field(..., alias="Current [A]")
    Voltage: List[float] = Field(..., alias="Voltage [V]")
    Temperature: List[float] = Field(..., alias="Temperature [K]")

class Validation(BaseModel):
    c_20_discharge: ValidationItem = Field(..., alias="C/20 discharge")
    one_c_discharge: ValidationItem = Field(..., alias="1C discharge")

class NMC_Pouch_Cell(BaseModel):
    header: Header = Field(..., alias="Header")
    parameterisation: Parameterisation = Field(..., alias="Parameterisation")
    validation: Validation = Field(..., alias="Validation")

def load_data_from_json(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def validate_data(data):
    try:
        nmc_pouch_cell = NMC_Pouch_Cell(**data)
        print("Validation successful!")
        print(nmc_pouch_cell)
    except ValidationError as e:
        print("Validation error:", e)

if __name__ == "__main__":
    # Use the full path to the JSON file
    json_file = r'C:\Users\nisha\Documents\BPX\examples\nmc_pouch_cell_BPX.json'
    data = load_data_from_json(json_file)
    validate_data(data)
