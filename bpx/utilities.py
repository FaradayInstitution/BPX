def get_initial_stoichiometries(target_soc, bpx):
    """
    Calculate individual electrode stoichiometries at a particular target
    state of charge, given stoichiometric limits defined by bpx

    Parameters
    ----------
    target_soc : float
        Target initial SOC. Must be between 0 and 1.
    bpx : :class:`BPX`
        A parsed BPX model

    Returns
    -------
    sto_n, sto_p
        The electrode stoichiometries that give the target state of charge
    """
    if target_soc < 0 or target_soc > 1:
        raise ValueError("Target SOC should be between 0 and 1")

    sto_n_min = bpx.parameterisation.negative_electrode.minimum_stoichiometry
    sto_n_max = bpx.parameterisation.negative_electrode.maximum_stoichiometry
    sto_p_min = bpx.parameterisation.positive_electrode.minimum_stoichiometry
    sto_p_max = bpx.parameterisation.positive_electrode.maximum_stoichiometry

    sto_n = (sto_n_max - sto_n_min) * target_soc + sto_n_min
    sto_p = sto_p_max - (sto_p_max - sto_p_min) * target_soc

    return sto_n, sto_p


def get_initial_concentrations(target_soc, bpx):
    """
    Calculate individual electrode concentrations at a particular target
    state of charge, given stoichiometric limits and maximum concentrations
    defined by bpx

    Parameters
    ----------
    target_soc : float
        Target initial SOC. Must be between 0 and 1.
    bpx : :class:`BPX`
        A parsed BPX model

    Returns
    -------
    c_n, c_p
        The electrode concentrations that give the target state of charge
    """
    c_n_max = bpx.parameterisation.negative_electrode.maximum_concentration
    c_p_max = bpx.parameterisation.positive_electrode.maximum_concentration

    sto_n_init, sto_p_init = get_initial_stoichiometries(target_soc, bpx)

    return sto_n_init * c_n_max, sto_p_init * c_p_max
