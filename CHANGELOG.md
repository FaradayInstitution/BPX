# Unreleased

- Added validation based on models: SPM, SPMe, DFN ([#34](https://github.com/pybamm-team/BPX/pull/34)). A warning will be produced if the user-defined model type does not match the parameter set (e.g., if the model is `SPM`, but the full DFN model parameters are provided).
- Added support for well-mixed, blended electrodes that contain more than one active material ([#33](https://github.com/pybamm-team/BPX/pull/33))
- Added five parametrisation examples (two DFN parametrisation examples from About:Energy open-source release, blended electrode definition, user-defined 0th-order hysteresis, and SPM parametrisation).

# [v0.3.1](https://github.com/pybamm-team/BPX/releases/tag/v0.3.1)

- Temporarily pin Pydantic version ([#35](https://github.com/pybamm-team/BPX/pull/35))

# [v0.3.0](https://github.com/pybamm-team/BPX/releases/tag/v0.3.0)

- Added a missing factor of 2 in the definition of the interfacial current, see the Butler-Volmer equation (2a) in the associated BPX standard document. The interfacial current is now given by $j=2j_0\sinh(F\eta/2/R/T)$ instead of $j=j_0\sinh(F\eta/2/R/T)$.

# [v0.2.0](https://github.com/pybamm-team/BPX/releases/tag/v0.2.0)

- Parsing a BPX json file with additional (unexpected) fields now raises a `ValidationError` ([#16](https://github.com/pybamm-team/BPX/pull/16))
- Fixed a bug in the experiment schema ([#13](https://github.com/pybamm-team/BPX/pull/13))

# [v0.1.0](https://github.com/pybamm-team/BPX/releases/tag/v0.1.0)

Initial release of the Battery Parameter eXchange (BPX) format.
