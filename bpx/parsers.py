from bpx import BPX


def parse_bpx_file(filename: str) -> BPX:
    """
    Parameters
    ----------

    filename: str
        a filepath to a bpx file

    Returns
    -------
    BPX:
        a parsed BPX model
    """
    return BPX.parse_file(filename)


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
