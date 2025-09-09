# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy.typing as npt
from ..._type_aliases import LogspaceType

import numpy as np

from ._int_logspace_gap_gt_1_soft import _int_logspace_gap_gt_1_soft



def _int_logspace_gap_gt_1_hard(
    _LOG_SINGLE_GRID: npt.NDArray[np.float64],
    _is_logspace: LogspaceType,
    _posn: int,
    _log_hard_min: np.float64,
    _log_hard_max: np.float64
) -> tuple[np.float64, np.float64]:
    """Use :func:`_int_logspace_gap_gt_1_soft` to determine the left and
    right bounds then truncate left and right as necessary based on
    `_hard_min` and `_hard_max`. Interstitial values are determined by
    another module.

    Parameters
    ----------
    _LOG_SINGLE_GRID : npt.NDArray[np.float64]
        The last round's search grid for a single integer parameter that
        is in logspace. `_SINGLE_GRID` must be sorted ascending, and is
        presumed to be by :func:`_param_conditioning._params` (at least
        initially).
    _is_logspace : LogspaceType
        For numerical params, if the space is linear, or some other
        non-standard interval, it is False. If it is logspace, the
        'truth' of being a logspace is represented by a number indicating
        the interval of the logspace. E.g., np.logspace(-5, 5, 11) would
        be represented by 1.0, and np.logspace(-20, 20, 9) would be
        represented by 5.0.
    _posn : int
        The index position in the previous round's grid where the best
        value fell.
    _log_hard_min : np.float64
        The minimum value in the first round's search grid. Ignored if
        not hard.
    _log_hard_max : np.float64
        The maximum value in the first round's search grid. Ignored if
        not hard.

    Returns
    -------
    __ : tuple[np.float64, np.float64]
        _left : np.float64
            The minimum value for the next search grid after application
            of the hard minimum.
        _right : np.float64
            The maximum value for the next search grid after application
            of the hard maximum.

    """


    # _hard_min < 1 handled by _validate_int_float_linlogspace, but do it
    # here again.... remember in logspace!
    if _log_hard_min < 0:
        raise ValueError(f"log hard_min < 0")

    if (_LOG_SINGLE_GRID < _log_hard_min).any():
        raise ValueError(f"grid < log hard min")

    if (_LOG_SINGLE_GRID > _log_hard_max).any():
        raise ValueError(f"grid > log hard max")


    # _left & _right are returned in logspace
    _left, _right = _int_logspace_gap_gt_1_soft(
        _LOG_SINGLE_GRID,
        _is_logspace,
        _posn
    )

    _left: np.float64
    _right: np.float64

    # apply hard min and max

    _left = max(_log_hard_min, _left)
    _right = min(_log_hard_max, _right)


    return _left, _right





