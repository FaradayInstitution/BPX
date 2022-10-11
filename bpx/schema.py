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
        alias='Title',
        example='Parameterisation example',
        description='LGM50 battery parametrisation',
    )
    description: str = Field(
        alias='Description',
        description=(
            'May contain additional description such as references, authors, etc.'
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
            'Model type (e.g. "Newman", "Newman with degradation", "3D Pouch", "SPMe", etc.)'
        )
    )

class Cell(BaseModel):
    initial_temperature: float = Field(
        alias='Initial temperature [K]',
        example=298.15,
    )
    reference_temperature: float = Field(
        alias='Reference temperature [K]',
        description='Reference temperature for the Arrhenius temperature dependence',
        example=298.15,
    )
    electrode_area: float = Field(
        alias='Electrode area [m2]',
        description='Electrode cross-sectional area',
        example=1.027
    )

class Electrolyte(BaseModel):
    conductivity: FloatFunctionTable = Field(
        alias='Conductivity [S.m-1]',
        description='Electrolyte conductivity (constant or function of concentration)',
    )

class Parameterisation(BaseModel):
    cell: Cell = Field(
        alias='Cell',
    )
    electrolyte: Electrolyte = Field(
        alias='Electrolyte',
    )

class BPX(BaseModel):
    header: Header = Field(
        alias='Header',
    )
    parameterisation: Parameterisation = Field(
        alias='Parameterisation'
    )



