# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases_float import (
    FloatDataType,
    FloatGridType
)

import sys

import numpy as np

from .._validation._validate_int_float_linlogspace import \
    _validate_int_float_linlogspace
from ......utilities._get_module_name import get_module_name



def _float_linspace(
    _SINGLE_GRID: FloatGridType,
    _posn: int,
    _is_hard: bool,
    _hard_min: FloatDataType,
    _hard_max: FloatDataType,
    _points: int
) -> FloatGridType:
    """Build a new grid for a single float parameter based on the
    previous round's grid and the best value discovered by the parent
    GridSearch, subject to constraints imposed by 'hard', edges, etc.

    Parameters
    ----------
    _SINGLE_GRID : FloatGridType
        The last round's search grid for a single param. `_SINGLE_GRID`
        must be sorted ascending, and is presumed to be by
        :func:`_param_conditioning._params` (at least initially).
    _posn : int
        The index position in the previous round's grid where the best
        value fell.
    _is_hard : bool
        Whether the parameter has hard left and right boundaries. This
        field is read from the dtype/search field in _params. If hard,
        the left and right bounds are set from the lowest and highest
        values in the first round's search grid (the grid that was passed
        in `params` at init.)
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
        False,
        _posn,
        _is_hard,
        _hard_min,
        _hard_max,
        _points,
        get_module_name(str(sys.modules[__name__]))
    )

    if _posn == 0:
        # IF ON THE LEFT EDGE OF THE GRID
        _left = _SINGLE_GRID[0]
        _right = _SINGLE_GRID[1]
        if _is_hard:
            if _left == _hard_min:
                _OUT_GRID = np.linspace(_left, _right, _points + 1)[:-1]
            else:
                _left = max(_left - (_right - _left), _hard_min, 0)
                _OUT_GRID = np.linspace(_left, _right, _points + 2)[1:-1]
        else: # elif not hard left bound
            _right = _SINGLE_GRID[1]
            _left = max(_left - (_right - _left), 0)
            _OUT_GRID = np.linspace(_left, _right, _points + 2)[1:-1]

    elif _posn == (len(_SINGLE_GRID) - 1):

        # IF ON THE RIGHT EDGE OF THE GRID
        if _is_hard:
            _left = _SINGLE_GRID[-2]
            _right = _SINGLE_GRID[-1]
            if _right == _hard_max:
                _OUT_GRID = np.linspace(_left, _right, _points + 1)[1:]
            else:
                _right = min(_right + (_right - _left), _hard_max)
                _OUT_GRID = np.linspace(_left, _right, _points + 2)[1: -1]

        else: # elif not hard right bound
            _left = _SINGLE_GRID[-2]
            _right = _SINGLE_GRID[-1] + (_SINGLE_GRID[-1] - _left)
            _OUT_GRID = np.linspace(_left, _right, _points + 2)[1:-1]

    else:  # SOMEWHERE IN THE MIDDLE OF THE GRID

        _left = _SINGLE_GRID[_posn - 1]
        _right = _SINGLE_GRID[_posn + 1]
        _OUT_GRID = np.linspace(_left, _right, _points + 2)[1:-1]

    del _left, _right

    _OUT_GRID = _OUT_GRID.tolist()

    _OUT_GRID = list(map(float, _OUT_GRID))

    return _OUT_GRID








