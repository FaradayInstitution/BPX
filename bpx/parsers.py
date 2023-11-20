from bpx import BPX


def parse_bpx_file(filename: str, v_tol: float = 0.001) -> BPX:
    """
    A convenience function to parse a bpx file into a BPX model.

    Parameters
    ----------
    filename: str
        a filepath to a bpx file
    v_tol: float
        absolute tolerance in [V] to validate the voltage limits, 1 mV by default

    Returns
    -------
    BPX: :class:`bpx.BPX`
        a parsed BPX model
    """
    if v_tol < 0:
        raise ValueError("v_tol should not be negative")

    BPX.settings.tolerances["Voltage [V]"] = v_tol

    return BPX.parse_file(filename)


def parse_bpx_obj(bpx: dict, v_tol: float = 0.001) -> BPX:
    """
    A convenience function to parse a bpx dict into a BPX model.

    Parameters
    ----------
    bpx: dict
        a dict object in bpx format
    v_tol: float
        absolute tolerance in [V] to validate the voltage limits, 1 mV by default

    Returns
    -------
    BPX: :class:`bpx.BPX`
        a parsed BPX model
    """
    if v_tol < 0:
        raise ValueError("v_tol should not be negative")

    BPX.settings.tolerances["Voltage [V]"] = v_tol

    return BPX.parse_obj(bpx)


def parse_bpx_str(bpx: str, v_tol: float = 0.001) -> BPX:
    """
    A convenience function to parse a json formatted string in bpx format into a BPX
    model.

    Parameters
    ----------
    bpx: str
        a json formatted string in bpx format
    v_tol: float
        absolute tolerance in [V] to validate the voltage limits, 1 mV by default

    Returns
    -------
    BPX:
        a parsed BPX model
    """
    if v_tol < 0:
        raise ValueError("v_tol should not be negative")

    BPX.settings.tolerances["Voltage [V]"] = v_tol

    return BPX.parse_raw(bpx)
