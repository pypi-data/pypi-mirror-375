# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy.typing as npt
from ..._type_aliases import LogspaceType

import numpy as np



def _int_logspace_gap_gt_1_soft(
    _LOG_SINGLE_GRID: npt.NDArray[np.float64],
    _is_logspace: LogspaceType,
    _posn: int
) -> tuple[np.float64, np.float64]:
    """Determine the left and right bounds for a soft logspace integer
    based on whether the best result from `GridSearchCV` landed on a
    left or right edge or in the middle of last round's search grid.

    Apply the universal integer lower bound of 1 (10**0) to the left
    bound. Interstitial values are determined by another module.

    This should only be accessed on the first regular pass after shifts.
    Logspaces convert to linspace.

    Parameters
    ----------
    _LOG_SINGLE_GRID : npt.NDArray[np.float64]
        The last round's search grid for a single soft integer parameter
        in logspace. `_LOG_SINGLE_GRID` must be sorted ascending, and is
        presumed to be by :func:`_param_conditioning._params` (at least
        initially).
    _is_logspace : LogspaceType
        For numerical params, if the space is linear, or some other
        non-standard interval, it is False. If it is logspace, the
        'truth' of being a logspace is represented by a number indicating
        the interval of the logspace. E.g.,np.logspace(-5, 5, 11) would
        be represented by 1.0, and np.logspace(-20, 20, 9) would be
        represented by 5.0.
    _posn : int
        The index position in the previous round's grid where the best
        value fell.

    Returns
    -------
    __ : :tuple[np.float64, np.float64]
        _left : np.float64
            The minimum value for the next search grid (may be changed
            by another algorithm later)
        _right: np.float64
            The maximum value for the next search grid (may be changed
            by another algorithm later)

    """


    if not isinstance(_LOG_SINGLE_GRID, np.ndarray):
        raise TypeError(
            f"_LOG_SINGLE_GRID must be an ndarray (_SINGLE_GRID "
            f"should have been converted to log10 using np.log10)"
        )


    # 24_05_18_10_08_00 redundant with _validate_int_float_linlogspace in
    # _int_logspace_gap_gt_1, but keep it for testing this module
    if any(_LOG_SINGLE_GRID < 0):
        raise ValueError(f"_LOG_SINGLE_GRID cannot contain negative values")


    _ = np.subtract(*_LOG_SINGLE_GRID[[1,0]])
    if _ != _is_logspace:
        raise ValueError(
            f"log gap in grid ({_}) != _is_logspace ({_is_logspace})"
        )
    del _

    # remember this is being done in logspace!

    if _posn == 0:
        _left = 0
        _right = _LOG_SINGLE_GRID[1]

    elif _posn == len(_LOG_SINGLE_GRID) - 1:
        _left = 0
        _right = _LOG_SINGLE_GRID[-1] + _is_logspace

    else:
        _left = 0
        _right = _LOG_SINGLE_GRID[_posn + 1]


    return _left, _right




