from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field, validator

from bpx import Function, InterpolatedTable

FloatFunctionTable = Union[float, Function, InterpolatedTable]


class Header(BaseModel):
    bpx: float = Field(
        alias='BPX',
        example=1.0,
        description='BPX format version',
    )
    title: str = Field(
        None,
        alias='Title',
        example='Parameterisation example',
        description='LGM50 battery parametrisation',
    )
    description: str = Field(
        None,
        alias='Description',
        description=(
            'May contain additional description such as '
            'references, authors, etc.'
        ),
        example='Chang-Hui Chen et al 2020 J. Electrochem. Soc. 167 080534',
    )
    model: Literal[
        'Newman',
        'Newman with degradation',
        '3D Pouch',
        'SPMe',
    ] = Field(
        alias='Model',
        example='Newman',
        description=(
            'Model type (e.g. "Newman", "Newman with degradation", '
            '"3D Pouch", "SPMe", etc.)'
        )
    )


class Cell(BaseModel):
    initial_temperature: float = Field(
        alias='Initial temperature [K]',
        example=298.15,
    )
    reference_temperature: float = Field(
        alias='Reference temperature [K]',
        description=(
            'Reference temperature for the Arrhenius temperature dependence'
        ),
        example=298.15,
    )
    electrode_area: float = Field(
        alias='Electrode area [m2]',
        description='Electrode cross-sectional area',
        example=1.027
    )
    lower_voltage_cutoff: float = Field(
        None,
        alias='Lower voltage cut-off [V]',
        description='Minimum allowed voltage',
        example=2.0
    )
    upper_voltage_cutoff: float = Field(
        None,
        alias='Upper voltage cut-off [V]',
        description='Maximum allowed voltage',
        example=4.4
    )
    nominal_cell_capacity: float = Field(
        None,
        alias='Nominal cell capacity [A.h]',
        description=(
            'Nominal cell capacity. '
            'Used to convert between current and C-rate.'
        ),
        example=5.0,
    )
    specific_heat_capacity: float = Field(
        None,
        alias='Specific heat capacity [J.K-1.kg-1]',
        example=1000.0,
        description='Specific heat capacity (lumped)',
    )
    themal_conductivity: float = Field(
        None,
        alias='Thermal conductivity [W.m-1.K-1]',
        example=1.0,
        description='Thermal conductivity (lumped)',
    )
    density: float = Field(
        None,
        alias='Density [kg.m-3]',
        example=1000.0,
        description='Density (lumped)',
    )
    number_of_electrodes: int = Field(
        alias='Number of electrodes connected in parallel to make a cell',
        example=1,
        description=(
            'Number of electrodes connected in parallel to make a cell'
        )
    )
    cell_height: float = Field(
        None,
        alias='Cell height [m]',
        example=0.140,
        description='Battery cell height',
    )
    cell_width: float = Field(
        None,
        alias='Cell width [m]',
        example=0.042,
        description='Battery cell width (if applicable)',
    )
    cell_thickness: float = Field(
        None,
        alias='Cell thickness [m]',
        example=0.0114,
        description='Battery cell thickness/depth (if applicable)',
    )
    cell_diameter: float = Field(
        None,
        alias='Cell diameter [m]',
        example=0.01,
        description='Battery cell diameter (if applicable)',
    )


class Electrolyte(BaseModel):
    initial_concentration: float = Field(
        alias='Initial concentration [mol.m-3]',
        example=1000,
        description=(
            'Initial / rest lithium ion concentration in the electrolyte'
        ),
    )
    cation_transference_number: float = Field(
        alias='Cation transference number',
        example=0.259,
        description='Cation transference number',
    )
    conductivity: FloatFunctionTable = Field(
        alias='Conductivity [S.m-1]',
        example=1.0,
        description=(
            'Electrolyte conductivity (constant or function of concentration)'
        ),
    )
    diffusivity: FloatFunctionTable = Field(
        alias='Diffusivity [m2.s-1]',
        example='8.794e-7 * x * x - 3.972e-6 * x + 4.862e-6',
        description=(
            'Lithium ion diffusivity in electrolyte (constant or function '
            'of concentration)'
        ),
    )
    conductivity_activation_energy: float = Field(
        None,
        alias='Conductivity activation energy [J.mol-1]',
        example=17100,
        description='Activation energy for conductivity in electrolyte',
    )
    diffusivity_activation_energy: float = Field(
        None,
        alias='Diffusivity activation energy [J.mol-1]',
        example=17100,
        description='Activation energy for diffusivity in electrolyte',
    )


class Anode(BaseModel):
    particle_radius: float = Field(
        alias='Particle radius [m]',
        example=5.86e-6,
        description='Particle radius',
    )
    thickness: float = Field(
        alias='Thickness [m]',
        example=85.2e-6,
        description='Electrode thickness',
    )
    diffusivity: FloatFunctionTable = Field(
        alias='Diffusivity [m2.s-1]',
        example='3.3e-14',
        description=(
            'Lithium ion diffusivity in particle (constant or function '
            'of concentration)'
        ),
    )
    ocp: FloatFunctionTable = Field(
        alias='OCP [V]',
        example={"x": [0, 0.1, 1], "y": [1.72, 1.2, 0.06]},
        description=(
            'Open-circuit potential (OCP), function of particle stoichiometry'
        ),
    )
    conductivity: FloatFunctionTable = Field(
        alias='Conductivity [S.m-1]',
        example=215.0,
        description=(
            'Electrolyte conductivity (constant or function of concentration)'
        ),
    )
    surface_area_per_unit_volume: float = Field(
        alias='Surface area per unit volume',
        example=383959,
        description='Particle surface area per unit of volume',
    )
    porosity: float = Field(
        alias='Porosity',
        example=0.25,
        description='Electrolyte volume fraction (porosity)',
    )
    transport_efficiency: float = Field(
        alias='Transport efficiency',
        example=0.125,
        description='Transport efficiency / inverse MacMullin number',
    )
    reaction_rate: float = Field(
        alias='Reaction rate [mol.m-2.s-1]',
        example=1e-10,
        description='Normalised reaction rate K (see notes)',
    )
    initial_concentration: float = Field(
        alias='Initial concentration [mol.m-3]',
        example=29866.1,
        description='Initial concentration of lithium ions in particles',
    )
    maximum_concentration: float = Field(
        alias='Maximum concentration [mol.m-3]',
        example=33133,
        description='Maximum concentration of lithium ions in particles',
    )
    diffusivity_activation_energy: float = Field(
        None,
        alias='Diffusivity activation energy [J.mol-1]',
        example=35000,
        description='Activation energy for diffusivity in particles',
    )
    reaction_rate_activation_energy: float = Field(
        None,
        alias='Reaction rate activation energy [J.mol-1]',
        example=53400,
        description='Activation energy of reaction rate in particles',
    )


class Cathode(BaseModel):
    particle_radius: float = Field(
        alias='Particle radius [m]',
        example=5.22e-6,
        description='Particle radius',
    )
    thickness: float = Field(
        alias='Thickness [m]',
        example=75.6e-6,
        description='Electrode thickness',
    )
    diffusivity: FloatFunctionTable = Field(
        alias='Diffusivity [m2.s-1]',
        example='4.0e-15',
        description=(
            'Lithium ion diffusivity in particle (constant or function '
            'of concentration)'
        ),
    )
    ocp: FloatFunctionTable = Field(
        alias='OCP [V]',
        example={"x": [0, 0.1, 1], "y": [1.72, 1.2, 0.06]},
        description=(
            'Open-circuit potential (OCP), '
            'function of particle stoichiometry'
        )
    )
    conductivity: FloatFunctionTable = Field(
        alias='Conductivity [S.m-1]',
        example=0.18,
        description=(
            'Electrolyte conductivity (constant or function of concentration)'
        ),
    )
    surface_area_per_unit_volume: float = Field(
        alias='Surface area per unit volume',
        example=382184,
        description='Particle surface area per unit of volume',
    )
    porosity: float = Field(
        alias='Porosity',
        example=0.335,
        description='Electrolyte volume fraction (porosity)',
    )
    transport_efficiency: float = Field(
        alias='Transport efficiency',
        example=0.1939,
        description='Transport efficiency / inverse MacMullin number',
    )
    reaction_rate: float = Field(
        alias='Reaction rate [mol.m-2.s-1]',
        example=1e-10,
        description='Normalised reaction rate K (see notes)',
    )
    initial_concentration: float = Field(
        alias='Initial concentration [mol.m-3]',
        example=167920,
        description='Initial concentration of lithium ions in particles',
    )
    maximum_concentration: float = Field(
        alias='Maximum concentration [mol.m-3]',
        example=631040,
        description='Maximum concentration of lithium ions in particles',
    )
    diffusivity_activation_energy: float = Field(
        None,
        alias='Diffusivity activation energy [J.mol-1]',
        example=17800,
        description='Activation energy for diffusivity in particles',
    )
    reaction_rate_activation_energy: float = Field(
        None,
        alias='Reaction rate activation energy [J.mol-1]',
        example=27010,
        description='Activation energy of reaction rate in particles',
    )


class Separator(BaseModel):
    thickness: float = Field(
        alias='Thickness [m]',
        example=1.2e-5,
        description='Separator thickness',
    )
    porosity: float = Field(
        alias='Porosity',
        example=0.47,
        description='Electrolyte volume fraction (porosity)',
    )
    transport_efficiency: float = Field(
        alias='Transport efficiency',
        example=0.3222,
        description='Transport efficiency / inverse MacMullin number',
    )


class Experimental(BaseModel):
    time: List[float] = Field(
        None,
        alias='Time [s]',
        example=[0, 0.1, 0.2, 0.3, 0.4],
        description='Time in seconds (list of floats)'
    )
    current: List[float] = Field(
        None,
        alias='Current [A]',
        example=[-5, -5, -5, -5, -5],
        description='Current vs time',
    )
    voltage: List[float] = Field(
        alias='Voltage [V]',
        example=[4.2, 4.1, 4.0, 3.9, 3.8],
        description='Voltage vs time',
    )
    temperature: List[float] = Field(
        alias='Temperature [K]',
        example=[298, 298, 298, 298, 298],
        description='Temperature vs time',
    )


class Parameterisation(BaseModel):
    cell: Cell = Field(
        alias='Cell',
    )
    electrolyte: Electrolyte = Field(
        alias='Electrolyte',
    )
    anode: Anode = Field(
        alias='Anode',
    )
    cathode: Anode = Field(
        alias='Cathode',
    )
    separator: Separator = Field(
        alias='Separator',
    )


class Validation(BaseModel):
    experimental: Experimental = Field(
        None,
        alias='Experimental'
    )


class BPX(BaseModel):
    header: Header = Field(
        alias='Header',
    )
    parameterisation: Parameterisation = Field(
        alias='Parameterisation'
    )
    validation: Validation = Field(
        None,
        alias='Validation'
    )
