from bpx import BPX


def parse_bpx_file(filename: str, v_tol: float = 0.001) -> BPX:
    """
    Parameters
    ----------

    filename: str
        a filepath to a bpx file
    v_tol: float
        absolute tolerance in [V] to validate the voltage limits, 1 mV by default

    Returns
    -------
    BPX:
        a parsed BPX model
    """
    if v_tol < 0:
        raise ValueError("v_tol should not be negative")

    return BPX.parse_file(BPX, filename, v_tol=v_tol)


def parse_bpx_obj(bpx: dict) -> BPX:
    """
    Parameters
    ----------

    bpx: dict
        a dict object in bpx format

    Returns
    -------
    BPX:
        a parsed BPX model
    """
    return BPX.parse_obj(bpx)


def parse_bpx_str(bpx: str) -> BPX:
    """
    Parameters
    ----------

    bpx: str
        a json formatted string in bpx format

    Returns
    -------
    BPX:
        a parsed BPX model
    """
    return BPX.parse_raw(bpx)
