# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases import ParamsType



def _shift_points_and_passes(
    _params: ParamsType,
    _pass: int,
    _total_passes_is_hard: bool
) -> ParamsType:
    """Replicate the points from the last pass into the next pass.

    Truncate points (the list in the 2nd slot of a param's dict value)
    if `total_passes` is hard.

    Parameters
    ----------
    _params : ParamsType
        Grid-building instructions for all parameters.
    _pass : int
        The zero-indexed number of the current GridSearch pass.
    _total_passes_is_hard : bool
        If True, do not increment `total_passes` for a shift pass; if
        False, increment `total_passes` each time a shift pass is made.

    Returns
    -------
    _params : ParamsType
        Updated grid-building instructions.

    """


    for _param in _params:

        # for all params:
        # replicate the previous points into the next pass and push the
        # next values over to the right;
        # e.g., [10, 5, 4, 3] on edge on pass 0 (needs a shift),
        #   becomes [10, 10, 5, 4, 3] on pass 1
        # if total_passes_is_hard, drop last value
        # e.g., [10, 5, 4, 3] on edge on pass 0,
        #   becomes [10, 10, 5, 4] on pass 1

        _params[_param][1].insert(_pass, _params[_param][1][_pass - 1])

        if _total_passes_is_hard:
            _params[_param][1] = _params[_param][1][:-1]


    return _params






