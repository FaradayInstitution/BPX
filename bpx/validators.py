from warnings import warn

from .base_extra_model import ExtraBaseModel


def check_sto_limits(param: ExtraBaseModel) -> ExtraBaseModel:
    """
    Validates that the STO limits subbed into the OCPs give the correct voltage limits.
    Works if both OCPs are defined as functions.
    Blended electrodes are not supported.
    This is a reusable validator to be used for both DFN/SPMe and SPM parameter sets.
    """

    try:
        ocp_n = param.negative_electrode.ocp.to_python_function()
        ocp_p = param.positive_electrode.ocp.to_python_function()
    except AttributeError:
        # OCPs defined as interpolated tables or one of the electrodes is blended; do nothing
        return param

    sto_n_min = param.negative_electrode.minimum_stoichiometry
    sto_n_max = param.negative_electrode.maximum_stoichiometry
    sto_p_min = param.positive_electrode.minimum_stoichiometry
    sto_p_max = param.positive_electrode.maximum_stoichiometry
    v_min = param.cell.lower_voltage_cutoff
    v_max = param.cell.upper_voltage_cutoff

    # Voltage tolerance from `settings` data class
    tol = param.Settings.tolerances["Voltage [V]"]

    # Checks the maximum voltage estimated from STO
    v_max_sto = ocp_p(sto_p_min) - ocp_n(sto_n_max)
    if v_max_sto - v_max > tol:
        warn(
            f"The maximum voltage computed from the STO limits ({v_max_sto} V) "
            f"is higher than the upper voltage cut-off ({v_max} V) "
            f"with the absolute tolerance v_tol = {tol} V",
            stacklevel=2,
        )

    # Checks the minimum voltage estimated from STO
    v_min_sto = ocp_p(sto_p_max) - ocp_n(sto_n_min)
    if v_min_sto - v_min < -tol:
        warn(
            f"The minimum voltage computed from the STO limits ({v_min_sto} V) "
            f"is less than the lower voltage cut-off ({v_min} V) "
            f"with the absolute tolerance v_tol = {tol} V",
            stacklevel=2,
        )

    return param
