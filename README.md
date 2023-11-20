# 🔋 BPX
![tests](https://github.com/FaradayInstitution/BPX/actions/workflows/test.yml/badge.svg)
[![codecov](https://codecov.io/gh/FaradayInstitution/BPX/branch/main/graph/badge.svg?token=Krv0JW3gYZ)](https://codecov.io/gh/FaradayInstitution/BPX)

An implementation of the Battery Parameter eXchange (BPX) format in Pydantic. BPX, an outcome of the Faraday Institution [Multi-scale Modelling project](https://www.faraday.ac.uk/research/lithium-ion/battery-system-modelling/), is an open standard for physics-based Li-ion battery models that has been developed to reduce costs and time-to-market through a common definition of physics-based battery models that can be used widely across industry. To find out more, visit the [BPX website](https://bpxstandard.com/).

This repository features a Pydantic-based parser for JSON files in the BPX format, which validates your file against the schema.

To support the new open standard, [About:Energy](https://www.aboutenergy.io/) have supplied two parameters sets for an NMC and LFP cell. The BPX files and associated examples and information can be found on the [A:E BPX Parameterisation repository](https://github.com/About-Energy-OpenSource/About-Energy-BPX-Parameterisation/).

To see how to use BPX with [PyBaMM](https://www.pybamm.org/), check out the [BPX example repository](https://github.com/pybamm-team/bpx-example).

## 🚀 Installation
The BPX package can be installed using pip
```bash
pip install bpx
```

BPX is available on GNU/Linux, MacOS and Windows. We strongly recommend to install PyBaMM within a python [virtual environment](https://docs.python.org/3/tutorial/venv.html), in order not to alter any distribution python files.

## 💻 Usage
To create a BPX object from a JSON file, you can use the `parse_bpx_file` function
```python
import bpx

filename = 'path/to/my/file.json'
my_params = bpx.parse_bpx_file(filename)
```
`my_params` will now be of type `BPX`, which acts like a python dataclass with the same attributes as the BPX format. To obatin example files, see the `examples` folder, the [A:E BPX Parameterisation repository](https://github.com/About-Energy-OpenSource/About-Energy-BPX-Parameterisation/), or the [BPX example repository](https://github.com/pybamm-team/bpx-example).

Attributes of the class can be printed out using the standard Python dot notation, for example, you can print out the initial temperature of the cell using
```python
print('Initial temperature of cell:', my_params.parameterisation.cell.initial_temperature)
```

Alternatively, you can export the `BPX` object as a dictionary and use the string names (aliases) of the parameters from the standard
```python
my_params_dict = my_params.dict(by_alias=True)
print('Initial temperature of cell:', my_params_dict["Parameterisation"]["Cell"]["Initial temperature [K]"])
```

The entire BPX object can be pretty printed using the `devtools` package 
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

## 📖 Documentation
API documentation for the `bpx` package can be built locally using [Sphinx](https://www.sphinx-doc.org/en/master/). To build the documentation first [clone the repository](https://github.com/git-guides/git-clone), install the `bpx` package, and then run the following command:
```bash
sphinx-build docs docs/_build/html  
```
This will generate a number of html files in the `docs/_build/html` directory. To view the documentation, open the file `docs/_build/html/index.html` in a web browser, e.g. by running
```bash
open docs/_build/html/index.html
```

## 📫 Get in touch
If you have any questions please get in touch via email <bpx@faraday.ac.uk>.
