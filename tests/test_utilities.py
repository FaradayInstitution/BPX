import copy
import unittest

import pytest
from pydantic import TypeAdapter

from bpx import BPX, get_electrode_concentrations, get_electrode_stoichiometries

adapter = TypeAdapter(BPX)


class TestUtlilities(unittest.TestCase):
    def setUp(self) -> None:
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
                    "Particle radius [m]": 5.22e-6,
                    "Thickness [m]": 75.6e-6,
                    "Diffusivity [m2.s-1]": 4.0e-15,
                    "OCP [V]": {"x": [0, 0.1, 1], "y": [1.72, 1.2, 0.06]},
                    "Conductivity [S.m-1]": 0.18,
                    "Surface area per unit volume [m-1]": 382184,
                    "Porosity": 0.335,
                    "Transport efficiency": 0.1939,
                    "Reaction rate constant [mol.m-2.s-1]": 1e-10,
                    "Maximum concentration [mol.m-3]": 63104.0,
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

    def test_get_init_sto(self) -> None:
        test = copy.copy(self.base)
        obj = adapter.validate_python(test)
        x, y = get_electrode_stoichiometries(0.3, obj)
        assert x == pytest.approx(0.304)
        assert y == pytest.approx(0.66)

    def test_get_init_conc(self) -> None:
        test = copy.copy(self.base)
        obj = adapter.validate_python(test)
        x, y = get_electrode_concentrations(0.7, obj)
        assert x == pytest.approx(23060.568)
        assert y == pytest.approx(21455.36)

    def test_get_init_sto_negative_target_soc(self) -> None:
        test = copy.copy(self.base)
        obj = adapter.validate_python(test)
        with self.assertWarnsRegex(
            UserWarning,
            "Target SOC should be between 0 and 1",
        ):
            get_electrode_stoichiometries(-0.1, obj)

    def test_get_init_sto_bad_target_soc(self) -> None:
        test = copy.copy(self.base)
        obj = adapter.validate_python(test)
        with self.assertWarnsRegex(
            UserWarning,
            "Target SOC should be between 0 and 1",
        ):
            get_electrode_stoichiometries(1.1, obj)

    def test_get_init_conc_negative_target_soc(self) -> None:
        test = copy.copy(self.base)
        obj = adapter.validate_python(test)
        with self.assertWarnsRegex(
            UserWarning,
            "Target SOC should be between 0 and 1",
        ):
            get_electrode_concentrations(-0.5, obj)

    def test_get_init_conc_bad_target_soc(self) -> None:
        test = copy.copy(self.base)
        obj = adapter.validate_python(test)
        with self.assertWarnsRegex(
            UserWarning,
            "Target SOC should be between 0 and 1",
        ):
            get_electrode_concentrations(1.05, obj)


if __name__ == "__main__":
    unittest.main()
