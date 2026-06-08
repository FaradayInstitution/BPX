import contextlib
import copy
import json
import re
import unittest
import warnings
from collections.abc import Iterator
from pathlib import Path

import pytest

from bpx import (
    convert_v0_to_v1,
    is_legacy_bpx,
    parse_bpx_file,
    parse_bpx_obj,
    parse_bpx_str,
)

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


@contextlib.contextmanager
def _recorded_warnings() -> Iterator[list[warnings.WarningMessage]]:
    """
    Record warnings into a list rather than using ``pytest.warns``: parsing a
    legacy file also emits an incidental STO voltage warning, which the suite's
    ``filterwarnings=error`` config would raise as an error inside a
    ``pytest.warns`` block.
    """
    with warnings.catch_warnings(record=True) as records:
        warnings.simplefilter("always")
        yield records


class TestParsers(unittest.TestCase):
    def setUp(self) -> None:
        base = """
            {
                "Header": {
                        "BPX": "1.0.0",
                        "Title": "Parameterisation example of an NMC111|graphite 12.5 Ah pouch cell",
                        "Model": "DFN"
                },
                "Parameterisation": {
                        "Cell": {
                            "Reference temperature [K]": 298.15,
                            "Lower voltage cut-off [V]": 2.7,
                            "Upper voltage cut-off [V]": 4.2,
                            "Nominal cell capacity [A.h]": 12.5,
                            "Specific heat capacity [J.K-1.kg-1]": 913,
                            "Density [kg.m-3]": 1847,
                            "Electrode area [m2]": 0.016808,
                            "Number of electrode pairs connected in parallel to make a cell": 34,
                            "External surface area [m2]": 0.0379,
                            "Volume [m3]": 0.000128
                        },
                        "Electrolyte": {
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
                        },
                        "State": {
                            "Initial conditions": {
                                "Initial state-of-charge": 100,
                                "Initial electrolyte concentration [mol.m-3]": 1000,
                                "Initial temperature [K]": 299,
                                "Initial hysteresis state: Negative electrode": 5,
                                "Initial hysteresis state: Positive electrode": 10
                            },
                            "Thermal environment": {
                                "Ambient temperature [K]": 299,
                                "Heat transfer coefficient [W.m-2.K-1]": 10.0
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
        with pytest.warns(
            UserWarning,
            match="The maximum voltage computed from the STO limits",
        ):
            parse_bpx_str(test)

    def test_parse_string_tolerance(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("error")  # Treat warnings as errors
            test = copy.copy(self.base)
            parse_bpx_str(test, v_tol=0.002)

    def test_thermal_conductivity_error(self) -> None:
        """Test that providing thermal_conductivity in Cell section raises an error."""
        test = copy.copy(self.base)
        # Add thermal conductivity to the Cell section
        test = test.replace(
            '"Specific heat capacity [J.K-1.kg-1]": 913,',
            '"Specific heat capacity [J.K-1.kg-1]": 913, "Thermal conductivity [W.m-1.K-1]": 2.04,',
        )

        with pytest.raises(
            ValueError,
            match="The 'Thermal conductivity \\[W\\.m-1\\.K-1\\]' field is not part of the BPX schema",
        ):
            parse_bpx_str(test)

    def test_temps_in_cell_error(self) -> None:
        """Test that providing initial temperature in Cell section raises an error."""
        test = copy.copy(self.base)
        # Add initial temperature to the Cell section
        test = test.replace(
            '"Reference temperature [K]": 298.15,',
            '"Reference temperature [K]": 298.15, "Initial temperature [K]": 299,',
        )

        with pytest.raises(
            ValueError,
            match=re.escape("The 'Initial temperature [K]' and 'Ambient temperature [K]' fields have been moved."),
        ):
            parse_bpx_str(test)

    def test_initial_concentration_error(self) -> None:
        """Test that providing initial concentration in Electrolyte section raises an error."""
        test = copy.copy(self.base)
        # Add initial concentration to the Electrolyte section
        test = test.replace(
            '"Cation transference number": 0.2594,',
            '"Cation transference number": 0.2594, "Initial concentration [mol.m-3]": 1000,',
        )

        with pytest.raises(
            ValueError,
            match=re.escape("'Initial concentration [mol.m-3]' has been renamed and moved."),
        ):
            parse_bpx_str(test)

    # Legacy BPX v0.x backward-compatibility conversion
    def _make_v0_obj(self) -> dict:
        """Recast the v1.x ``self.base`` object into the legacy v0.x layout."""
        obj = json.loads(self.base)
        state = obj.pop("State")
        # v0.x used a numeric version field
        obj["Header"]["BPX"] = 0.4
        cell = obj["Parameterisation"]["Cell"]
        ic = state["Initial conditions"]
        te = state["Thermal environment"]
        cell["Initial temperature [K]"] = ic["Initial temperature [K]"]
        cell["Ambient temperature [K]"] = te["Ambient temperature [K]"]
        # v0.x described thermal behaviour via a lumped thermal conductivity
        cell["Thermal conductivity [W.m-1.K-1]"] = 1.5
        obj["Parameterisation"]["Electrolyte"]["Initial concentration [mol.m-3]"] = ic[
            "Initial electrolyte concentration [mol.m-3]"
        ]
        return obj

    @staticmethod
    def _legacy_warned(records: list[warnings.WarningMessage]) -> bool:
        return any("legacy BPX v0" in str(r.message) for r in records)

    def test_v0_obj_is_converted_with_warning(self) -> None:
        v0_obj = self._make_v0_obj()
        with _recorded_warnings() as records:
            bpx = parse_bpx_obj(v0_obj)
        assert self._legacy_warned(records)
        # moved fields are preserved
        assert bpx.state.thermal_environment.ambient_temperature == 299
        assert bpx.state.initial_conditions.initial_temperature == 299
        # heat transfer coefficient is the placeholder (0), not carried from v0.x
        assert bpx.state.thermal_environment.heat_transfer_coefficient == 0

    def test_v0_str_is_converted_with_warning(self) -> None:
        with _recorded_warnings() as records:
            bpx = parse_bpx_str(json.dumps(self._make_v0_obj()))
        assert self._legacy_warned(records)
        assert bpx.state.thermal_environment.ambient_temperature == 299

    def test_v0_file_is_converted_with_warning(self) -> None:
        # the autouse _temp_bpx_file fixture chdirs into a tmp directory
        temp_file = Path("v0.json")
        temp_file.write_text(json.dumps(self._make_v0_obj()))
        with _recorded_warnings() as records:
            bpx = parse_bpx_file(temp_file)
        assert self._legacy_warned(records)
        assert bpx.state.thermal_environment.ambient_temperature == 299

    def test_v0_missing_initial_temperature_falls_back_to_ambient(self) -> None:
        v0_obj = self._make_v0_obj()
        del v0_obj["Parameterisation"]["Cell"]["Initial temperature [K]"]
        with _recorded_warnings() as records:
            bpx = parse_bpx_obj(v0_obj)
        assert self._legacy_warned(records)
        assert bpx.state.initial_conditions.initial_temperature == bpx.state.thermal_environment.ambient_temperature

    def test_v0_missing_ambient_temperature_falls_back_to_reference(self) -> None:
        # ambient temperature is required in v1.x State but optional in v0.x;
        # converting a file without it must still validate (falls back to the
        # reference temperature), not raise a ValidationError.
        v0_obj = self._make_v0_obj()
        del v0_obj["Parameterisation"]["Cell"]["Ambient temperature [K]"]
        reference = v0_obj["Parameterisation"]["Cell"]["Reference temperature [K]"]
        with _recorded_warnings() as records:
            bpx = parse_bpx_obj(v0_obj)
        assert self._legacy_warned(records)
        assert bpx.state.thermal_environment.ambient_temperature == reference

    def test_convert_legacy_false_does_not_convert(self) -> None:
        v0_obj = self._make_v0_obj()
        # without conversion the misplaced v0.x fields fail v1.x validation
        with pytest.raises(ValueError, match="have been moved"):
            parse_bpx_obj(v0_obj, convert_legacy=False)

    def test_v1_object_not_converted(self) -> None:
        # self.base is a v1.x object: it must not trigger the conversion path
        with _recorded_warnings() as records:
            parse_bpx_str(self.base)
        assert not self._legacy_warned(records)

    def test_conversion_does_not_mutate_input(self) -> None:
        v0_obj = self._make_v0_obj()
        original = copy.deepcopy(v0_obj)
        converted = convert_v0_to_v1(v0_obj)
        # input untouched
        assert v0_obj == original
        assert "State" not in v0_obj
        # output is converted
        assert is_legacy_bpx(v0_obj)
        assert not is_legacy_bpx(converted)
        assert "State" in converted
        assert "Thermal conductivity [W.m-1.K-1]" not in converted["Parameterisation"]["Cell"]

    def test_is_legacy_bpx_version_detection(self) -> None:
        cases = [(0.4, True), ("0.4.0", True), (1.0, False), ("1.1.0", False), (2, False)]
        for version, is_v0 in cases:
            with self.subTest(version=version):
                assert is_legacy_bpx({"Header": {"BPX": version}}) is is_v0

    def test_invalid_header_raises(self) -> None:
        with pytest.raises(ValueError, match="Header"):
            is_legacy_bpx({"Parameterisation": {}})

    def test_legacy_example_files_are_converted(self) -> None:
        # the bundled examples are genuine v0.x files (no State block)
        examples = sorted(EXAMPLES_DIR.glob("*.json"))
        assert examples, f"no example files found in {EXAMPLES_DIR}"
        for path in examples:
            with self.subTest(example=path.name), _recorded_warnings() as records:
                bpx = parse_bpx_file(path)
                assert self._legacy_warned(records)
                assert bpx.state is not None
