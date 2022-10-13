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








if __name__ == '__main__':
    unittest.main()
