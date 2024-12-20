# [v0.5.0](https://github.com/FaradayInstitution/BPX/releases/tag/v0.5.0)

- Bug fixes for Pydantic ([#81](https://github.com/FaradayInstitution/BPX/pull/81))
- Updated to Pydantic V2 and the hatch build system ([#79](https://github.com/FaradayInstitution/BPX/pull/79))

# [v0.4.0](https://github.com/FaradayInstitution/BPX/releases/tag/v0.4.0)

- Added five parametrisation examples (two DFN parametrisation examples from About:Energy open-source release, blended electrode definition, user-defined 0th-order hysteresis, and SPM parametrisation). ([#45](https://github.com/FaradayInstitution/BPX/pull/45))
- Allow user-defined parameters to be added using the field ["Parameterisation"]["User-defined"] ([#44](https://github.com/FaradayInstitution/BPX/pull/44))
- Added basic API documentation ([#43](https://github.com/FaradayInstitution/BPX/pull/43))
- Added validation based on models: SPM, SPMe, DFN ([#34](https://github.com/FaradayInstitution/BPX/pull/34)). A warning will be produced if the user-defined model type does not match the parameter set (e.g., if the model is `SPM`, but the full DFN model parameters are provided).
- Added support for well-mixed, blended electrodes that contain more than one active material ([#33](https://github.com/FaradayInstitution/BPX/pull/33))
- Added validation of the STO limits subbed into the OCPs vs the upper/lower cut-off voltage limits for non-blended electrodes with the OCPs defined as functions ([#32](https://github.com/FaradayInstitution/BPX/pull/32)). The user can provide a tolerance by updating the settings variable `BPX.settings.tolerances["Voltage [V]"]` or by passing extra option `v_tol` to `parse_bpx_file()`, `parse_bpx_obj()` or `parse_bpx_str()` functions. Default value of the tolerance is 1 mV. The tolerance cannot be negative.
- Added the target SOC check in `get_electrode_concentrations()` function. Raise a warning if the SOC is outside of [0,1] interval.

# [v0.3.1](https://github.com/FaradayInstitution/BPX/releases/tag/v0.3.1)

- Temporarily pin Pydantic version ([#35](https://github.com/FaradayInstitution/BPX/pull/35))

# [v0.3.0](https://github.com/FaradayInstitution/BPX/releases/tag/v0.3.0)

- Added a missing factor of 2 in the definition of the interfacial current, see the Butler-Volmer equation (2a) in the associated BPX standard document. The interfacial current is now given by $j=2j_0\sinh(F\eta/2/R/T)$ instead of $j=j_0\sinh(F\eta/2/R/T)$.

# [v0.2.0](https://github.com/FaradayInstitution/BPX/releases/tag/v0.2.0)

- Parsing a BPX json file with additional (unexpected) fields now raises a `ValidationError` ([#16](https://github.com/FaradayInstitution/BPX/pull/16))
- Fixed a bug in the experiment schema ([#13](https://github.com/FaradayInstitution/BPX/pull/13))

# [v0.1.0](https://github.com/FaradayInstitution/BPX/releases/tag/v0.1.0)

Initial release of the Battery Parameter eXchange (BPX) format.
