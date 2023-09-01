from bpx import BPX


def parse_bpx_file(filename: str) -> BPX:
    """
    A convenience function to parse a bpx file into a BPX model.

    Parameters
    ----------
    filename: str
        a filepath to a bpx file

    Returns
    -------
    BPX: :class:`bpx.BPX`
        a parsed BPX model
    """
    return BPX.parse_file(filename)


def parse_bpx_obj(bpx: dict) -> BPX:
    """
    A convenience function to parse a bpx dict into a BPX model.

    Parameters
    ----------
    bpx: dict
        a dict object in bpx format

    Returns
    -------
    BPX: :class:`bpx.BPX`
        a parsed BPX model
    """
    return BPX.parse_obj(bpx)


def parse_bpx_str(bpx: str) -> BPX:
    """
    A convenience function to parse a json formatted string in bpx format into a BPX
    model.

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
