# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    InParamsType,
    ParamsType
)

from ._total_passes import _cond_total_passes
from ._params import _cond_params
from ._max_shifts import _cond_max_shifts



def _conditioning(
    _params: InParamsType,
    _total_passes: int,
    _max_shifts: int,
    _inf_max_shifts: int
) -> tuple[ParamsType, int, int]:
    """Centralized hub for conditioning parameters.

    Condition given `max_shifts`, `params`, and `total_passes` into
    internal processing containers, types, and values.

    Parameters
    ----------
    _params : InParamsType
        `params` as passed to agscv.
    _total_passes : int
        `total_passes` as passed agscv.
    _max_shifts : int
        `max_shifts` as passed to agscv.
    _inf_max_shifts : int
        The built-in number used when `max_shifts` is *unlimited*.

    Returns
    -------
    __ : tuple[ParamsType, int, int]
        _params : ParamsType
            The conditioned params. All sequences converted to Python
            list. Any integers in the points slots for numeric params
            converted to lists.
        _total_passes : int
            The conditioned `total_passes`, a Python integer.
        _max_shifts : int
            The conditioned `max_shifts`; set to a large integer if
            passed as None.

    """


    _total_passes = _cond_total_passes(_total_passes)

    _params = _cond_params(_params, _total_passes)

    _max_shifts = _cond_max_shifts(_max_shifts, _inf_max_shifts)


    return _params, _total_passes, _max_shifts



