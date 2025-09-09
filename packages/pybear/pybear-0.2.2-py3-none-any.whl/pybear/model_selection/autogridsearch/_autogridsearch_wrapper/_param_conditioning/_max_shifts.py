# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



def _cond_max_shifts(
    _max_shifts: int | None,
    _inf_max_shifts: int
) -> int:
    """When `max_shifts` is passed as None to agscv, this indicates
    unlimited shifts allowed. Condition `max_shifts` into a large number.

    Parameters
    ----------
    _max_shifts : int | None
        The maximum number of grid-shift passes agscv is allowed to make.
        If None, the number of shifting passes allowed is unlimited.
    _inf_max_shifts : int
        The large integer to substitute in for `max_shifts` if the user
        passed None for `max_shifts`.

    Returns
    -------
    _max_shifts : int
        A large number that should never be attainable.

    """


    # cannot use float('inf') here, validation wants numbers.Integral
    return int(_max_shifts or _inf_max_shifts)



