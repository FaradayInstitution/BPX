import copy
import re
import unittest
import warnings
from typing import Any

import pytest
from pydantic import TypeAdapter, ValidationError

from bpx import BPX

adapter = TypeAdapter(BPX)


class TestSchema(unittest.TestCase):
    def setUp(self) -> None:
        self.base: dict[str, Any] = {
            "Header": {
                "BPX": "1.0.0",
                "Model": "DFN",
            },
            "Parameterisation": {
                "Cell": {
                    "Ambient temperature [K]": 299.0,
                    "Initial temperature [K]": 299.0,
                    "Reference temperature [K]": 299.0,
                    "Electrode area [m2]": 2.0,
                    "External surface area [m2]": 2.2,
                    "Volume [m3]": 1.0,
                    "Number of electrode pairs connected in parallel to make a cell": 1,
                    "Nominal cell capacity [A.h]": 5.0,
                    "Lower voltage cut-off [V]": 2.0,
                    "Upper voltage cut-off [V]": 4.0,
                },
                "Electrolyte": {
                    "Initial concentration [mol.m-3]": 1000,
                    "Cation transference number": 0.259,
                    "Conductivity [S.m-1]": 1.0,
                    "Diffusivity [m2.s-1]": ("8.794e-7 * x * x - 3.972e-6 * x + 4.862e-6"),
                },
                "Negative electrode": {
                    "Particle radius [m]": 5.86e-6,
                    "Thickness [m]": 85.2e-6,
                    "Diffusivity [m2.s-1]": 3.3e-14,
                    "OCP [V]": {"x": [0, 0.1, 1], "y": [1.72, 1.2, 0.06]},
                    "Conductivity [S.m-1]": 215.0,
                    "Surface area per unit volume [m-1]": 383959,
                    "Porosity": 0.25,
                    "Transport efficiency": 0.125,
                    "Reaction rate constant [mol.m-2.s-1]": 1e-10,
                    "Maximum concentration [mol.m-3]": 33133,
                    "Minimum stoichiometry": 0.01,
                    "Maximum stoichiometry": 0.99,
                },
                "Positive electrode": {
                    "Thickness [m]": 75.6e-6,
                    "Conductivity [S.m-1]": 0.18,
                    "Porosity": 0.335,
                    "Transport efficiency": 0.1939,
                    "Particle": {
                        "Primary": {
                            "Particle radius [m]": 5.22e-6,
                            "Diffusivity [m2.s-1]": 4.0e-15,
                            "OCP [V]": {"x": [0, 0.1, 1], "y": [1.72, 1.2, 0.06]},
                            "Surface area per unit volume [m-1]": 382184,
                            "Reaction rate constant [mol.m-2.s-1]": 1e-10,
                            "Maximum concentration [mol.m-3]": 63104.0,
                            "Minimum stoichiometry": 0.1,
                            "Maximum stoichiometry": 0.9,
                        },
                        "Secondary": {
                            "Particle radius [m]": 10.0e-6,
                            "Diffusivity [m2.s-1]": 4.0e-15,
                            "OCP [V]": {"x": [0, 0.1, 1], "y": [1.72, 1.2, 0.06]},
                            "Surface area per unit volume [m-1]": 382184,
                            "Reaction rate constant [mol.m-2.s-1]": 1e-10,
                            "Maximum concentration [mol.m-3]": 63104.0,
                            "Minimum stoichiometry": 0.1,
                            "Maximum stoichiometry": 0.9,
                        },
                    },
                },
                "Separator": {
                    "Thickness [m]": 1.2e-5,
                    "Porosity": 0.47,
                    "Transport efficiency": 0.3222,
                },
            },
        }

        # SPM parameter set
        self.base_spm = {
            "Header": {
                "BPX": "1.0.0",
                "Model": "SPM",
            },
            "Parameterisation": {
                "Cell": {
                    "Ambient temperature [K]": 299.0,
                    "Initial temperature [K]": 299.0,
                    "Reference temperature [K]": 299.0,
                    "Electrode area [m2]": 2,
                    "External surface area [m2]": 2.2,
                    "Volume [m3]": 1,
                    "Number of electrode pairs connected in parallel to make a cell": 1,
                    "Nominal cell capacity [A.h]": 5,
                    "Lower voltage cut-off [V]": 2,
                    "Upper voltage cut-off [V]": 4,
                },
                "Negative electrode": {
                    "Particle radius [m]": 5.86e-6,
                    "Thickness [m]": 85.2e-6,
                    "Diffusivity [m2.s-1]": 3.3e-14,
                    "OCP [V]": {"x": [0, 0.1, 1], "y": [1.72, 1.2, 0.06]},
                    "Surface area per unit volume [m-1]": 383959,
                    "Reaction rate constant [mol.m-2.s-1]": 1e-10,
                    "Maximum concentration [mol.m-3]": 33133,
                    "Minimum stoichiometry": 0.01,
                    "Maximum stoichiometry": 0.99,
                },
                "Positive electrode": {
                    "Thickness [m]": 75.6e-6,
                    "Particle": {
                        "Primary": {
                            "Particle radius [m]": 5.22e-6,
                            "Diffusivity [m2.s-1]": 4.0e-15,
                            "OCP [V]": {"x": [0, 0.1, 1], "y": [1.72, 1.2, 0.06]},
                            "Surface area per unit volume [m-1]": 382184,
                            "Reaction rate constant [mol.m-2.s-1]": 1e-10,
                            "Maximum concentration [mol.m-3]": 63104.0,
                            "Minimum stoichiometry": 0.1,
                            "Maximum stoichiometry": 0.9,
                        },
                        "Secondary": {
                            "Particle radius [m]": 10.0e-6,
                            "Diffusivity [m2.s-1]": 4.0e-15,
                            "OCP [V]": {"x": [0, 0.1, 1], "y": [1.72, 1.2, 0.06]},
                            "Surface area per unit volume [m-1]": 382184,
                            "Reaction rate constant [mol.m-2.s-1]": 1e-10,
                            "Maximum concentration [mol.m-3]": 63104.0,
                            "Minimum stoichiometry": 0.1,
                            "Maximum stoichiometry": 0.9,
                        },
                    },
                },
            },
        }

        # Non-blended electrodes
        self.base_non_blended = {
            "Header": {
                "BPX": "1.0.0",
                "Model": "SPM",
            },
            "Parameterisation": {
                "Cell": {
                    "Ambient temperature [K]": 299.0,
                    "Initial temperature [K]": 299.0,
                    "Reference temperature [K]": 299.0,
                    "Electrode area [m2]": 2.0,
                    "External surface area [m2]": 2.2,
                    "Volume [m3]": 1.0,
                    "Number of electrode pairs connected in parallel to make a cell": 1,
                    "Nominal cell capacity [A.h]": 5.0,
                    "Lower voltage cut-off [V]": 2.0,
                    "Upper voltage cut-off [V]": 4.0,
                },
                "Negative electrode": {
                    "Particle radius [m]": 5.86e-6,
                    "Thickness [m]": 85.2e-6,
                    "Diffusivity [m2.s-1]": 3.3e-14,
                    "OCP [V]": (
                        "9.47057878e-01 * exp(-1.59418743e+02  * x) - 3.50928033e+04 + "
                        "1.64230269e-01 * tanh(-4.55509094e+01 * (x - 3.24116012e-02 )) + "
                        "3.69968491e-02 * tanh(-1.96718868e+01 * (x - 1.68334476e-01)) + "
                        "1.91517003e+04 * tanh(3.19648312e+00 * (x - 1.85139824e+00)) + "
                        "5.42448511e+04 * tanh(-3.19009848e+00 * (x - 2.01660395e+00))"
                    ),
                    "Surface area per unit volume [m-1]": 383959,
                    "Reaction rate constant [mol.m-2.s-1]": 1e-10,
                    "Maximum concentration [mol.m-3]": 33133,
                    "Minimum stoichiometry": 0.005504,
                    "Maximum stoichiometry": 0.75668,
                },
                "Positive electrode": {
                    "Particle radius [m]": 5.22e-6,
                    "Thickness [m]": 75.6e-6,
                    "Diffusivity [m2.s-1]": 4.0e-15,
                    "OCP [V]": (
                        "-3.04420906 * x + 10.04892207 - "
                        "0.65637536 * tanh(-4.02134095 * (x - 0.80063948)) + "
                        "4.24678547 * tanh(12.17805062 * (x - 7.57659337)) - "
                        "0.3757068 * tanh(59.33067782 * (x - 0.99784492))"
                    ),
                    "Surface area per unit volume [m-1]": 382184,
                    "Reaction rate constant [mol.m-2.s-1]": 1e-10,
                    "Maximum concentration [mol.m-3]": 63104.0,
                    "Minimum stoichiometry": 0.42424,
                    "Maximum stoichiometry": 0.96210,
                },
            },
        }

    def test_simple(self) -> None:
        test = copy.deepcopy(self.base)
        adapter.validate_python(test)

    def test_simple_spme(self) -> None:
        test = copy.deepcopy(self.base)
        test["Header"]["Model"] = "SPMe"
        adapter.validate_python(test)

    def test_simple_spm(self) -> None:
        test = copy.deepcopy(self.base_spm)
        adapter.validate_python(test)

    def test_missing_model(self) -> None:
        test = copy.deepcopy(self.base)
        del test["Header"]["Model"]
        with pytest.raises(ValidationError, match=re.escape("Model\n  Field required")):
            adapter.validate_python(test)

    def test_bad_model(self) -> None:
        test = copy.deepcopy(self.base)
        test["Header"]["Model"] = "Wrong model type"
        with pytest.raises(ValidationError, match="Input should be 'SPM', 'SPMe' or 'DFN'"):
            adapter.validate_python(test)

    def test_bad_dfn(self) -> None:
        test = copy.deepcopy(self.base_spm)
        test["Header"]["Model"] = "DFN"
        with pytest.raises(ValueError, match="Valid SPM parameter set does not correspond with"):
            adapter.validate_python(test)

    def test_bad_spme(self) -> None:
        test = copy.deepcopy(self.base_spm)
        test["Header"]["Model"] = "SPMe"
        with pytest.raises(ValueError, match="Valid SPM parameter set does not correspond with"):
            adapter.validate_python(test)

    def test_bad_spm(self) -> None:
        test = copy.deepcopy(self.base)
        test["Header"]["Model"] = "SPM"
        with pytest.raises(ValueError, match="Valid parameter set does not correspond with"):
            adapter.validate_python(test)

    def test_table(self) -> None:
        test = copy.deepcopy(self.base)
        test["Parameterisation"]["Electrolyte"]["Conductivity [S.m-1]"] = {
            "x": [1.0, 2.0],
            "y": [2.3, 4.5],
        }
        adapter.validate_python(test)

    def test_bad_table(self) -> None:
        test = copy.deepcopy(self.base)
        test["Parameterisation"]["Electrolyte"]["Conductivity [S.m-1]"] = {
            "x": [1.0, 2.0],
            "y": [2.3],
        }
        with pytest.raises(
            ValidationError,
            match="x & y should be same length",
        ):
            adapter.validate_python(test)

    def test_function(self) -> None:
        test = copy.deepcopy(self.base)
        test["Parameterisation"]["Electrolyte"]["Conductivity [S.m-1]"] = "1.0 * x + 3"
        adapter.validate_python(test)

    def test_function_with_exp(self) -> None:
        test = copy.deepcopy(self.base)
        test["Parameterisation"]["Electrolyte"]["Conductivity [S.m-1]"] = "1.0 * exp(x) + 3"
        adapter.validate_python(test)

    def test_bad_function(self) -> None:
        test = copy.deepcopy(self.base)
        test["Parameterisation"]["Electrolyte"]["Conductivity [S.m-1]"] = "this is not a function"
        with pytest.raises(ValidationError):
            adapter.validate_python(test)

    def test_to_python_function(self) -> None:
        test = copy.deepcopy(self.base)
        test["Parameterisation"]["Electrolyte"]["Conductivity [S.m-1]"] = "2.0 * x"
        obj = adapter.validate_python(test)
        funct = obj.parameterisation.electrolyte.conductivity
        pyfunct = funct.to_python_function()
        assert pyfunct(2.0) == 4.0

    def test_bad_input(self) -> None:
        test = copy.deepcopy(self.base)
        test["Parameterisation"]["Electrolyte"]["bad"] = "this shouldn't be here"
        with pytest.raises(
            ValidationError,
            match=re.escape("Electrolyte.bad\n  Extra inputs are not permitted"),
        ) as excinfo:
            adapter.validate_python(test)

        # checks that only the relevent error is raised, not a cascade of unreleated errors
        errors = excinfo.value.errors()
        assert len(errors) == 1, f"Expected 1 error, got {len(errors)}: {errors}"

    def test_ints_preserved(self) -> None:
        test = copy.deepcopy(self.base_spm)
        obj = adapter.validate_python(test)
        assert isinstance(obj.parameterisation.cell.electrode_area, int)
        assert obj.parameterisation.cell.electrode_area == 2

    def test_validation_data(self) -> None:
        test = copy.deepcopy(self.base)
        test["Validation"] = {
            "Experiment 1": {
                "Time [s]": [0, 1000, 2000],
                "Current [A]": [-0.625, -0.625, -0.625],
                "Voltage [V]": [4.19367569, 4.1677888, 4.14976386],
                "Temperature [K]": [298.15, 298.15, 298.15],
            },
            "Experiment 2": {
                "Time [s]": [0, 1000],
                "Current [A]": [-0.625, -0.625],
                "Voltage [V]": [4.19367569, 4.1677888],
                "Temperature [K]": [298.15, 298.15],
            },
        }
        adapter.validate_python(test)

    def test_check_sto_limits_validator(self) -> None:
        warnings.filterwarnings("error")  # Treat warnings as errors
        test = copy.deepcopy(self.base_non_blended)
        test["Parameterisation"]["Cell"]["Upper voltage cut-off [V]"] = 4.3
        test["Parameterisation"]["Cell"]["Lower voltage cut-off [V]"] = 2.5
        adapter.validate_python(test)

    def test_check_sto_limits_validator_high_voltage(self) -> None:
        test = copy.deepcopy(self.base_non_blended)
        test["Parameterisation"]["Cell"]["Upper voltage cut-off [V]"] = 4.0
        with pytest.warns(UserWarning, match="maximum voltage computed from the STO limits"):
            adapter.validate_python(test)

    def test_check_sto_limits_validator_high_voltage_tolerance(self) -> None:
        warnings.filterwarnings("error")  # Treat warnings as errors
        test = copy.deepcopy(self.base_non_blended)
        test["Parameterisation"]["Cell"]["Upper voltage cut-off [V]"] = 4.0
        BPX.Settings.tolerances["Voltage [V]"] = 0.25
        adapter.validate_python(test)

    def test_check_sto_limits_validator_low_voltage(self) -> None:
        test = copy.deepcopy(self.base_non_blended)
        test["Parameterisation"]["Cell"]["Upper voltage cut-off [V]"] = 4.3
        test["Parameterisation"]["Cell"]["Lower voltage cut-off [V]"] = 3.0
        with pytest.warns(UserWarning, match="minimum voltage computed from the STO limits"):
            adapter.validate_python(test)

    def test_check_sto_limits_validator_low_voltage_tolerance(self) -> None:
        warnings.filterwarnings("error")  # Treat warnings as errors
        test = copy.deepcopy(self.base_non_blended)
        test["Parameterisation"]["Cell"]["Lower voltage cut-off [V]"] = 3.0
        BPX.Settings.tolerances["Voltage [V]"] = 0.35
        adapter.validate_python(test)

    def test_user_defined(self) -> None:
        test = copy.deepcopy(self.base)
        test["Parameterisation"]["User-defined"] = {
            "a": 1.0,
            "b": 2.0,
            "c": 3.0,
        }
        obj = adapter.validate_python(test)
        assert obj.parameterisation.user_defined.a == 1
        assert obj.parameterisation.user_defined.b == 2
        assert obj.parameterisation.user_defined.c == 3

    def test_user_defined_table(self) -> None:
        test = copy.deepcopy(self.base)
        test["Parameterisation"]["User-defined"] = {
            "a": {
                "x": [1.0, 2.0],
                "y": [2.3, 4.5],
            },
        }
        adapter.validate_python(test)

    def test_user_defined_bad_table(self) -> None:
        test = copy.deepcopy(self.base)
        test["Parameterisation"]["User-defined"] = {
            "a": {
                "a": [1.0, 2.0],
                "b": [2.3, 4.5],
            },
        }
        with pytest.raises(ValidationError):
            adapter.validate_python(test)

    def test_user_defined_function(self) -> None:
        test = copy.deepcopy(self.base)
        test["Parameterisation"]["User-defined"] = {"a": "2.0 * x"}
        adapter.validate_python(test)

    def test_user_defined_bad_function(self) -> None:
        test = copy.deepcopy(self.base)
        test["Parameterisation"]["User-defined"] = {"a": "this is not a function"}
        with pytest.raises(ValidationError):
            adapter.validate_python(test)

    def test_bad_user_defined(self) -> None:
        test = copy.deepcopy(self.base)
        # bool not allowed type
        test["Parameterisation"]["User-defined"] = {
            "bad": True,
        }
        with pytest.raises(TypeError):
            adapter.validate_python(test)

    def test_user_defined_int(self) -> None:
        test = copy.deepcopy(self.base)
        test["Parameterisation"]["User-defined"] = {"foobar": 10}
        adapter.validate_python(test)

    def test_deprecated_bpx_version(self) -> None:
        test = copy.deepcopy(self.base)
        test["Header"]["BPX"] = 0.4
        with pytest.warns(DeprecationWarning, match="The 'bpx' field now expects the BPX semantic version as a string"):
            adapter.validate_python(test)

    def test_bad_bpx_version(self) -> None:
        test = copy.deepcopy(self.base)
        test["Header"]["BPX"] = "1.2.3.4"  # Invalid version format
        with pytest.raises(ValidationError, match="String should match pattern"):
            adapter.validate_python(test)

    def test_valid_nested_user_defined(self) -> None:
        test = copy.deepcopy(self.base)
        # Allow any arbitrary JSON as long as all the leaves are valid
        # FloatFunctionTable
        test["Parameterisation"]["User-defined"] = {
            "description": "My model",
            "My model 1": {
                "Function 1": "2.0 * x",
                "Parameter 1": 0.1,
                "coefficients": {
                    "x": [1.0, 2.0],
                    "y": [2.3, 4.5],
                },
            },
            "My model 2": {
                "Function 1": "4.0 * x",
                "Parameter 1": 0.5,
                "Parameter 2": 2,
                "coefficients": {
                    "x": [10.0, 20.0],
                    "y": [20.3, 40.5],
                },
            },
        }
        obj = adapter.validate_python(test)

        assert obj.model_dump(by_alias=True)["Parameterisation"]["User-defined"]["My model 2"]["Parameter 2"] == 2

    def test_invalid_nested_string_user_defined(self) -> None:
        test = copy.deepcopy(self.base)
        # Don't allow non-function strings within the user-defined structure
        test["Parameterisation"]["User-defined"] = {
            "My model 2": {
                "submodel": "Type 1",
            },
        }
        with pytest.raises(ValidationError, match="Invalid Function: "):
            adapter.validate_python(test)

    def test_invalid_nested_table_user_defined(self) -> None:
        test = copy.deepcopy(self.base)
        # Catch invalid tables under user-defined structure
        test["Parameterisation"]["User-defined"] = {
            "My model 2": {
                "coefficients": {
                    "a": [1.0, 2.0],
                    "b": [2.3, 4.5],
                },
            },
        }

        with pytest.raises(ValidationError, match="Field required"):
            adapter.validate_python(test)

    def test_invalid_type_nested_user_defined(self) -> None:
        test = copy.deepcopy(self.base)
        # Don't allow other leaf types within the user-defined structure
        test["Parameterisation"]["User-defined"] = {
            "My model 2": {
                "Is a good model": True,
            },
        }

        with pytest.raises(TypeError, match="must be of type 'FloatFunctionTable'"):
            adapter.validate_python(test)

    def test_invalid_key_user_defined(self) -> None:
        test = copy.deepcopy(self.base)
        # Don't allow non-string keys in user-defined
        test["Parameterisation"]["User-defined"] = {
            4: {
                "Function 1": "2.0 * x",
            },
        }

        with pytest.raises(ValidationError, match="Keys should be strings"):
            adapter.validate_python(test)

    def test_invalid_description_user_defined(self) -> None:
        test = copy.deepcopy(self.base)
        # Don't allow non-string keys in user-defined
        test["Parameterisation"]["User-defined"] = {
            "description": 5.0,
        }

        with pytest.raises(ValidationError, match="Input should be a valid string"):
            adapter.validate_python(test)


if __name__ == "__main__":
    unittest.main()
