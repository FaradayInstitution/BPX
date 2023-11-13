# Getting Started

To get started, first install the `BPX` following the instructions given in [](installation).

To create a BPX object from a JSON file, you can use the `parse_bpx_file` function
```python
import bpx

filename = 'path/to/my/file.json'
my_params = bpx.parse_bpx_file(filename)
```
`my_params` will now be of type `BPX`, which acts like a python dataclass with the same attributes as the BPX format. To obatin example files, see the [A:E BPX Parameterisation repository](https://github.com/About-Energy-OpenSource/About-Energy-BPX-Parameterisation/) or [BPX example repository](https://github.com/pybamm-team/bpx-example).

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
