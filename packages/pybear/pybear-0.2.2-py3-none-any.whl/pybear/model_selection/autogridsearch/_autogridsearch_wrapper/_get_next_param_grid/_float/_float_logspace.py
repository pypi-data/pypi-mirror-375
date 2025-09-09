# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases_float import (
    FloatDataType,
    FloatGridType
)
from ..._type_aliases import (
    LogspaceType
)

import sys

import numpy as np

from .._validation._validate_int_float_linlogspace import \
    _validate_int_float_linlogspace
from ......utilities._get_module_name import get_module_name



def _float_logspace(
    _SINGLE_GRID: FloatGridType,
    _posn: int,
    _is_logspace: LogspaceType,
    _is_hard: bool,
    _hard_min: FloatDataType,
    _hard_max: FloatDataType,
    _points: int
) -> FloatGridType:
    """Build a new grid for a single float parameter based on the
    previous round's grid and the best value discovered by GridSearch,
    subject to constraints imposed by 'hard', universal minimum, etc.

    This should only be accessed on the first regular pass after shifts.
    Logspaces convert to linspace.

    Parameters
    ----------
    _SINGLE_GRID : FloatGridType
        The last round's search grid for a single param. `_SINGLE_GRID`
        must be sorted ascending, and is presumed to be by
        :func:`_param_conditioning._params` (at least initially).
    _posn : int
        The index position in the previous round's grid where the best
        value fell.
    _is_logspace : LogspaceType
        For numerical params, if the space is linear, or some other
        non-standard interval, it is False. If it is logspace, the
        'truth' of being a logspace is represented by a number indicating
        the interval of the logspace. E.g., np.logspace(-5, 5, 11) would
        be represented by 1.0, and np.logspace(-20, 20, 9) would be
        represented by 5.0.
    _is_hard : bool
        Whether the parameter has hard left and right boundaries. This
        field is read from the dtype/search field in `_params`. If hard,
        the left and right bounds are set from the lowest and highest
        values in the first round's search grid (the grid that was
        passed in `params` at init.)
    _hard_min : float
        If hard, the minimum value in the first round's search grid.
    _hard_max : float
        If hard, the maximum value in the first round's search grid.
    _points : int
        Number of points to use in the next search grid, subject to
        constraints of `_hard_min`, `_hard_max`, universal lower bound,
        etc.

    Returns
    -------
    _OUT_GRID : FloatGridType
        New search grid for the current pass' upcoming search.

    """

    # 24_05_17_09_13_00 this must stay here to get correct module name,
    # cannot be put in _float
    _validate_int_float_linlogspace(
        _SINGLE_GRID,
        _is_logspace,
        _posn,
        _is_hard,
        _hard_min,
        _hard_max,
        _points,
        get_module_name(str(sys.modules[__name__]))
    )


    _is_logspace = float(_is_logspace)
    _log_hard_min = np.log10(_hard_min)
    _log_hard_max = np.log10(_hard_max)
    del _hard_min, _hard_max
    _LOG_SINGLE_GRID = np.log10(_SINGLE_GRID)

    _ = np.subtract(*_LOG_SINGLE_GRID[[1,0]])
    if _ != _is_logspace:
        raise ValueError(
            f"log gap in grid ({_}) != _is_logspace ({_is_logspace})"
        )
    del _

    # CONVERT THE LOGSPACE GRID BACK TO LOGS, THIS SHOULD
    # CREATE EQUAL GAPS BETWEEN ALL THE POINTS

    if _posn == 0:      # IF ON THE LEFT EDGE OF GRID
        _left = _LOG_SINGLE_GRID[0]
        _right = _LOG_SINGLE_GRID[1]
        if _is_hard:
            if _left == _log_hard_min:
                # THIS GIVES CORRECT RANGE BUT DOESNT GUARANTEE NICE
                # DIVISIONS BECAUSE _left CANT BE JUST SET TO ZERO
                # BECAUSE OF HARD BOUND
                _left = 10 ** _left
                _right = 10 ** _right
                _OUT_GRID = np.linspace(_left, _right, _points + 1)[:-1]
            else:
                _left = max(_log_hard_min, _left - _is_logspace)
                _left = 10 ** _left
                _right = 10 ** _right
                _OUT_GRID = np.linspace(_left, _right, _points + 2)[1:-1]
        else:
            _left = 0
            _right = 10 ** _right
            _OUT_GRID = np.linspace(_left, _right, _points + 2)[1:-1]

    elif _posn == (len(_SINGLE_GRID) - 1):     # RIGHT EDGE OF GRID
        _left = _LOG_SINGLE_GRID[-2]
        _right = _LOG_SINGLE_GRID[-1]
        if _is_hard:
            if _right == _log_hard_max:
                # THIS GIVES CORRECT RANGE BUT DOESNT GUARANTEE NICE
                # DIVISIONS BECAUSE _left CANT BE JUST SET TO ZERO
                # BECAUSE OF HARD BOUND
                _left = 10 ** _left
                _right = 10 ** _right
                _OUT_GRID = np.linspace(_left, _right, _points + 1)[1:]
            else:
                _left = 10 ** _left
                _right = 10 ** min(_log_hard_max, _right + _is_logspace)
                _OUT_GRID = np.linspace(_left, _right, _points + 2)[1:-1]
        else:
            _left = 0
            _right = 10 ** (_right + _is_logspace)
            _OUT_GRID = np.linspace(_left, _right, _points + 2)[1:-1]

    else:       # SOMEWHERE IN THE MIDDLE OF THE GRID
        _left = 0
        _right = 10 ** (_LOG_SINGLE_GRID[_posn + 1])
        _OUT_GRID = np.linspace(_left, _right, _points + 2)[1:-1]


    del _is_logspace, _log_hard_min, _log_hard_max, _LOG_SINGLE_GRID
    del _left, _right

    _OUT_GRID = list(map(float, _OUT_GRID.tolist()))


    return _OUT_GRID





