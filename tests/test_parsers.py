import copy
import unittest
import warnings

import pytest

from bpx import parse_bpx_file, parse_bpx_obj, parse_bpx_str


class TestParsers(unittest.TestCase):
    def setUp(self) -> None:
        base = """
            {
                "Header": {
                        "BPX": 0.1,
                        "Title": "Parameterisation example of an NMC111|graphite 12.5 Ah pouch cell",
                        "Model": "DFN"
                },
                "Parameterisation": {
                        "Cell": {
                            "Ambient temperature [K]": 298.15,
                            "Initial temperature [K]": 298.15,
                            "Reference temperature [K]": 298.15,
                            "Lower voltage cut-off [V]": 2.7,
                            "Upper voltage cut-off [V]": 4.2,
                            "Nominal cell capacity [A.h]": 12.5,
                            "Specific heat capacity [J.K-1.kg-1]": 913,
                            "Thermal conductivity [W.m-1.K-1]": 2.04,
                            "Density [kg.m-3]": 1847,
                            "Electrode area [m2]": 0.016808,
                            "Number of electrode pairs connected in parallel to make a cell": 34,
                            "External surface area [m2]": 0.0379,
                            "Volume [m3]": 0.000128
                        },
                        "Electrolyte": {
                            "Initial concentration [mol.m-3]": 1000,
                            "Cation transference number": 0.2594,
                            "Conductivity [S.m-1]":
                                "0.1297 * (x / 1000) ** 3 - 2.51 * (x / 1000) ** 1.5 + 3.329 * (x / 1000)",
                            "Diffusivity [m2.s-1]": "8.794e-11 * (x / 1000) ** 2 - 3.972e-10 * (x / 1000) + 4.862e-10",
                            "Conductivity activation energy [J.mol-1]": 17100,
                            "Diffusivity activation energy [J.mol-1]": 17100
                        },
                        "Negative electrode": {
                            "Particle radius [m]": 4.12e-06,
                            "Thickness [m]": 5.62e-05,
                            "Diffusivity [m2.s-1]": 2.728e-14,
                            "OCP [V]":
                                "9.47057878e-01 * exp(-1.59418743e+02  * x) - 3.50928033e+04 +
                                1.64230269e-01 * tanh(-4.55509094e+01 * (x - 3.24116012e-02 )) +
                                3.69968491e-02 * tanh(-1.96718868e+01 * (x - 1.68334476e-01)) +
                                1.91517003e+04 * tanh(3.19648312e+00 * (x - 1.85139824e+00)) +
                                5.42448511e+04 * tanh(-3.19009848e+00 * (x - 2.01660395e+00))",
                            "Entropic change coefficient [V.K-1]":
                                "(-0.1112 * x + 0.02914 + 0.3561 * exp(-((x - 0.08309) ** 2) / 0.004616)) / 1000",
                            "Conductivity [S.m-1]": 0.222,
                            "Surface area per unit volume [m-1]": 499522,
                            "Porosity": 0.253991,
                            "Transport efficiency": 0.128,
                            "Reaction rate constant [mol.m-2.s-1]": 5.199e-06,
                            "Minimum stoichiometry": 0.005504,
                            "Maximum stoichiometry": 0.75668,
                            "Maximum concentration [mol.m-3]": 29730,
                            "Diffusivity activation energy [J.mol-1]": 30000,
                            "Reaction rate constant activation energy [J.mol-1]": 55000
                        },
                        "Positive electrode": {
                            "Particle radius [m]": 4.6e-06,
                            "Thickness [m]": 5.23e-05,
                            "Diffusivity [m2.s-1]": 3.2e-14,
                            "OCP [V]":
                                "-3.04420906 * x + 10.04892207 -
                                0.65637536 * tanh(-4.02134095 * (x - 0.80063948)) +
                                4.24678547 * tanh(12.17805062 * (x - 7.57659337)) -
                                0.3757068 * tanh(59.33067782 * (x - 0.99784492))",
                            "Entropic change coefficient [V.K-1]": -1e-4,
                            "Conductivity [S.m-1]": 0.789,
                            "Surface area per unit volume [m-1]": 432072,
                            "Porosity": 0.277493,
                            "Transport efficiency": 0.1462,
                            "Reaction rate constant [mol.m-2.s-1]": 2.305e-05,
                            "Minimum stoichiometry": 0.42424,
                            "Maximum stoichiometry": 0.96210,
                            "Maximum concentration [mol.m-3]": 46200,
                            "Diffusivity activation energy [J.mol-1]": 15000,
                            "Reaction rate constant activation energy [J.mol-1]": 35000
                        },
                        "Separator": {
                            "Thickness [m]": 2e-05,
                            "Porosity": 0.47,
                            "Transport efficiency": 0.3222
                        }
                }
            }
            """
        self.base = base.replace("\n", "")

    @pytest.fixture(autouse=True)
    def _temp_bpx_file(self, tmp_path: str, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        tmp_path.joinpath("test.json").write_text("{}")

    def test_negative_v_tol_file(self) -> None:
        with pytest.raises(
            ValueError,
            match="v_tol should not be negative",
        ):
            parse_bpx_file("test.json", v_tol=-0.001)

    def test_negative_v_tol_object(self) -> None:
        bpx_obj = {"BPX": 1.0}
        with pytest.raises(
            ValueError,
            match="v_tol should not be negative",
        ):
            parse_bpx_obj(bpx_obj, v_tol=-0.001)

    def test_negative_v_tol_string(self) -> None:
        with pytest.raises(
            ValueError,
            match="v_tol should not be negative",
        ):
            parse_bpx_str('{"BPX": 1.0}', v_tol=-0.001)

    def test_parse_string(self) -> None:
        test = copy.copy(self.base)
        with pytest.warns(UserWarning):
            parse_bpx_str(test)

    def test_parse_string_tolerance(self) -> None:
        warnings.filterwarnings("error")  # Treat warnings as errors
        test = copy.copy(self.base)
        parse_bpx_str(test, v_tol=0.002)
