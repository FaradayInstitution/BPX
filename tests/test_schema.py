import unittest
import copy
from pydantic import parse_obj_as, ValidationError

from bpx import BPX


class TestSchema(unittest.TestCase):
    def setUp(self):
        self.base = {
            "Header": {
                "BPX": 1.0,
                "Model": "Newman",
            },
            "Parameterisation": {
                "Cell": {
                    "Initial temperature [K]": 299.0,
                    "Reference temperature [K]": 299.0,
                    "Electrode area [m2]": 2.0,
                    "Number of electrodes connected in parallel to make a cell": 1,
                },
                "Electrolyte": {
                    "Initial concentration [mol.m-3]": 1000,
                    "Cation transference number": 0.259,
                    "Conductivity [S.m-1]": 1.0,
                    "Diffusivity [m2.s-1]": (
                        "8.794e-7 * x * x - 3.972e-6 * x + 4.862e-6"
                    ),
                },
                "Anode": {
                    "Particle radius [m]": 5.86e-6,
                    "Thickness [m]": 85.2e-6,
                    "Diffusivity [m2.s-1]": 3.3e-14,
                    "OCP [V]": {"x": [0, 0.1, 1], "y": [1.72, 1.2, 0.06]},
                    "Conductivity [S.m-1]": 215.0,
                    "Surface area per unit volume": 383959,
                    "Porosity": 0.25,
                    "Transport efficiency": 0.125,
                    "Reaction rate [mol.m-2.s-1]": 1e-10,
                    "Initial concentration [mol.m-3]": 29866.1,
                    "Maximum concentration [mol.m-3]": 33133,
                },
                "Cathode": {
                    "Particle radius [m]": 5.22e-6,
                    "Thickness [m]": 75.6e-6,
                    "Diffusivity [m2.s-1]": 4.0e-15,
                    "OCP [V]": {"x": [0, 0.1, 1], "y": [1.72, 1.2, 0.06]},
                    "Conductivity [S.m-1]": 0.18,
                    "Surface area per unit volume": 382184,
                    "Porosity": 0.335,
                    "Transport efficiency": 0.1939,
                    "Reaction rate [mol.m-2.s-1]": 1e-10,
                    "Initial concentration [mol.m-3]": 167920,
                    "Maximum concentration [mol.m-3]": 631040,
                },
                "Separator": {
                    "Thickness [m]": 1.2e-5,
                    "Porosity": 0.47,
                    "Transport efficiency": 0.3222,
                },
            },
        }

    def test_simple(self):
        test = copy.copy(self.base)
        parse_obj_as(BPX, test)

    def test_table(self):
        test = copy.copy(self.base)
        test["Parameterisation"]["Electrolyte"][
            "Conductivity [S.m-1]"
        ] = {
            "x": [1.0, 2.0],
            "y": [2.3, 4.5],
        }
        parse_obj_as(BPX, test)

    def test_bad_table(self):
        test = copy.copy(self.base)
        test["Parameterisation"]["Electrolyte"][
            "Conductivity [S.m-1]"
        ] = {
            "x": [1.0, 2.0],
            "y": [2.3],
        }
        with self.assertRaisesRegex(
                ValidationError,
                "x & y should be same length",
        ):
            parse_obj_as(BPX, test)

    def test_function(self):
        test = copy.copy(self.base)
        test["Parameterisation"]["Electrolyte"][
            "Conductivity [S.m-1]"
        ] = "1.0 * x + 3"
        parse_obj_as(BPX, test)

    def test_bad_function(self):
        test = copy.copy(self.base)
        test["Parameterisation"]["Electrolyte"][
            "Conductivity [S.m-1]"
        ] = "this is not a function"
        with self.assertRaises(ValidationError):
            parse_obj_as(BPX, test)

    def test_to_python_function(self):
        test = copy.copy(self.base)
        test["Parameterisation"]["Electrolyte"][
            "Conductivity [S.m-1]"
        ] = "2.0 * x"
        obj = parse_obj_as(BPX, test)
        funct = obj.parameterisation.electrolyte.conductivity
        pyfunct = funct.to_python_function()
        self.assertEqual(pyfunct(2.0), 4.0)


if __name__ == '__main__':
    unittest.main()
