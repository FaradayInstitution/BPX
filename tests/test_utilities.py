import unittest
import copy
from pydantic import parse_obj_as

from bpx import BPX, get_initial_stoichiometries, get_initial_concentrations


class TestUtlilities(unittest.TestCase):
    def setUp(self):
        self.base = {
            "Header": {
                "BPX": 1.0,
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
                    "Diffusivity [m2.s-1]": (
                        "8.794e-7 * x * x - 3.972e-6 * x + 4.862e-6"
                    ),
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
                    "Particle radius [m]": 5.22e-6,
                    "Thickness [m]": 75.6e-6,
                    "Diffusivity [m2.s-1]": 4.0e-15,
                    "OCP [V]": {"x": [0, 0.1, 1], "y": [1.72, 1.2, 0.06]},
                    "Conductivity [S.m-1]": 0.18,
                    "Surface area per unit volume [m-1]": 382184,
                    "Porosity": 0.335,
                    "Transport efficiency": 0.1939,
                    "Reaction rate constant [mol.m-2.s-1]": 1e-10,
                    "Maximum concentration [mol.m-3]": 631040,
                    "Minimum stoichiometry": 0.1,
                    "Maximum stoichiometry": 0.9,
                },
                "Separator": {
                    "Thickness [m]": 1.2e-5,
                    "Porosity": 0.47,
                    "Transport efficiency": 0.3222,
                },
            },
        }

    def test_get_init_sto(self):
        test = copy.copy(self.base)
        obj = parse_obj_as(BPX, test)
        x, y = get_initial_stoichiometries(0.3, obj)
        self.assertAlmostEqual(x, 0.304)
        self.assertAlmostEqual(y, 0.66)

    def test_get_init_conc(self):
        test = copy.copy(self.base)
        obj = parse_obj_as(BPX, test)
        x, y = get_initial_concentrations(0.7, obj)
        self.assertAlmostEqual(x, 23060.568)
        self.assertAlmostEqual(y, 214553.6)


if __name__ == "__main__":
    unittest.main()
