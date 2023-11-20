from warnings import warn


def get_electrode_stoichiometries(target_soc, bpx):
    """
    Calculate individual electrode stoichiometries at a particular target
    state of charge, given stoichiometric limits defined by bpx

    Parameters
    ----------
    target_soc : float
        Target state of charge. Must be between 0 and 1.
    bpx : :class:`BPX`
        A parsed BPX model.

    Returns
    -------
    sto_n, sto_p
        The electrode stoichiometries that give the target state of charge
    """
    if target_soc < 0 or target_soc > 1:
        warn("Target SOC should be between 0 and 1")

    sto_n_min = bpx.parameterisation.negative_electrode.minimum_stoichiometry
    sto_n_max = bpx.parameterisation.negative_electrode.maximum_stoichiometry
    sto_p_min = bpx.parameterisation.positive_electrode.minimum_stoichiometry
    sto_p_max = bpx.parameterisation.positive_electrode.maximum_stoichiometry

    sto_n = (sto_n_max - sto_n_min) * target_soc + sto_n_min
    sto_p = sto_p_max - (sto_p_max - sto_p_min) * target_soc

    return sto_n, sto_p


def get_electrode_concentrations(target_soc, bpx):
    """
    Calculate individual electrode concentrations at a particular target
    state of charge, given stoichiometric limits and maximum concentrations
    defined by bpx

    Parameters
    ----------
    target_soc : float
        Target state of charge. Must be between 0 and 1.
    bpx : :class:`BPX`
        A parsed BPX model.

    Returns
    -------
    c_n, c_p
        The electrode concentrations that give the target state of charge
    """
    if target_soc < 0 or target_soc > 1:
        warn("Target SOC should be between 0 and 1")

    c_n_max = bpx.parameterisation.negative_electrode.maximum_concentration
    c_p_max = bpx.parameterisation.positive_electrode.maximum_concentration

    sto_n, sto_p = get_electrode_stoichiometries(target_soc, bpx)

    return sto_n * c_n_max, sto_p * c_p_max
