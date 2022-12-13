# BPX
![tests](https://github.com/pybamm-team/BPX/actions/workflows/test.yml/badge.svg)
[![codecov](https://codecov.io/gh/pybamm-team/BPX/branch/main/graph/badge.svg?token=Krv0JW3gYZ)](https://codecov.io/gh/pybamm-team/BPX)

An implementation of the Battery Parameter eXchange (BPX) format in Pydantic. BPX, an outcome of the Faraday Institution [Multi-scale Modelling project](https://www.faraday.ac.uk/research/lithium-ion/battery-system-modelling/), is an open standard for physics-based Li-ion battery models that has been developed to reduce costs and time-to-market through a common definition of physics-based battery models that can be used widely across industry. To find out more, visit the [BPX website](https://bpxstandard.com/).

This repository features a Pydantic-based parser for JSON files in the BPX format, which validates your file against the schema.

To support the new open standard, [About:Energy](https://www.aboutenergy.io/) have supplied two parameters sets for an NMC and LFP cell. The BPX files and associated examples and information can be found on the [A:E BPX Parameterisation repository](https://github.com/About-Energy-OpenSource/About-Energy-BPX-Parameterisation/).

To see how to use BPX with [PyBaMM](https://www.pybamm.org/), check out the [BPX example repository](https://github.com/pybamm-team/bpx-example).
## Prerequisites

- Python 3+

## Installation

Create a new virtual environment, or activate an existing one (this example uses the python `venv` module, but you could use Anaconda and a `conda` environment)

```bash
python3 -m venv env
source env/bin/activate
```

Install the `BPX` module from the repository on GitHub

```bash
pip install git+https://github.com/pybamm-team/BPX.git
```

## Usage

Create a python script similar to that below

```python
import bpx

filename = 'path/to/my/file.json'
my_params = bpx.parse_bpx_file(filename)
```

`my_params` will now be of type `BPX`, which acts like a python dataclass with the same attributes as the BPX format. For example, you can print out the initial temperature of the cell using

```python
print('Initial temperature of cell:', my_params.parameterisation.cell.initial_temperature)
```

Alternatively, you can export the `BPX` object as a dictionary and use the string names (aliases) of the parameters from the standard
```python
my_params_dict = my_params.dict(by_alias=True)
print('Initial temperature of cell:', my_params_dict["Parameterisation"]["Cell"]["Initial temperature [K]"])
```

If you want to pretty print the entire object, you can use the `devtools` package to do this (remember to `pip install devtools`)

```python
from devtools import pprint
pprint(my_params)
```

You can convert any `Function` objects in `BPX` to regular callable Python functions, for example:

```python
positive_electrode_diffusivity = my_params.parameterisation.positive_electrode.diffusivity.to_python_function()
diff_at_one = positive_electrode_diffusivity(1.0)
print('positive electrode diffusivity at x = 1.0:', diff_at_one)
```

If you want to output the complete JSON schema in order to build a custom tool yourself, you can do so:

```python
print(bpx.BPX.schema_json(indent=2))
```

According to the `pydantic` docs, the generated schemas are compliant with the specifications: JSON Schema Core, JSON Schema Validation and OpenAPI.
