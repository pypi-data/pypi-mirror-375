# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases_int import (
    IntDataType,
    IntGridType
)

import sys

import numpy as np

from .._validation._validate_int_float_linlogspace import \
    _validate_int_float_linlogspace
from ......utilities._get_module_name import get_module_name



def _int_linspace_unit_gap(
    _SINGLE_GRID: IntGridType,
    _posn: int,
    _is_hard: bool,
    _hard_min: IntDataType,
    _hard_max: IntDataType,
    _points: int
) -> IntGridType:
    """Build a new grid for a single unit-gapped integer parameter based
    on the previous search round's grid and the best value discovered by
    GridSearch, subject to constraints imposed by 'hard', etc.

    Parameters
    ----------
    _SINGLE_GRID : IntGridType
        The last round's search grid for a single parameter.
        `_SINGLE_GRID` must be sorted ascending, and is presumed to be
        by :func:`_param_conditioning._params` (at least initially).
    _posn : int
        The index position in the previous round's grid where the best
        value fell.
    _is_hard : bool
        Whether the parameter has hard left and right boundaries. This
        field is read from the dtype/search field in _params. If hard,
        the left and right bounds are set from the lowest and highest
        values in the first round's search grid (the grid that was
        passed to `params` at init.)
    _hard_min : IntDataType
        The minimum value in the first round's search grid. Ignored if
        not hard.
    _hard_max : IntDataType
        The maximum value in the first round's search grid. Ignored if
        not hard.
    _points : int
        Number of points to use in the next search grid, subject to
        constraints of `_hard_min`, `_hard_max`, minimum of 1, etc.

    Returns
    -------
    _OUT_GRID : IntGridType
        New search grid for the current pass' upcoming search.

    """

    # 24_05_17_10_04_00 _validation must stay here to get the module name,
    # cannot put in _int
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
        _left = _SINGLE_GRID[0]
        _right = _SINGLE_GRID[1]
        if _is_hard:
            if _left == _hard_min:
                # _left is unchanged
                _right = min(_hard_max, _left + (_points - 1))
            else:  # elif left != hard min
                _left = max(1, _hard_min, _left - 1)
                _right = min(_hard_max, _left + (_points - 1))
        else:  # elif not _is_hard
            _left = max(1, _left - 1)
            _right = _left + (_points - 1)

    elif _posn == len(_SINGLE_GRID) - 1:
        _left = _SINGLE_GRID[-2]
        _right = _SINGLE_GRID[-1]
        if _is_hard:
            if _right == _hard_max:
                # _right is unchanged
                _left = max(1, _right - _points + 1, _hard_min)
            else:
                _right = _right + 1
                _left = max(1, _right - _points + 1, _hard_min)
                _right = min(_hard_max, _left + _points - 1)
        elif not _is_hard:
            _right = _right + 1
            _left = max(1, _right - _points + 1)
            _right = _left + _points - 1

    else:
        _num_left_of_cen = np.floor((_points - 1) // 2)
        if _is_hard:
            _left = max(1, _hard_min, _SINGLE_GRID[_posn] - _num_left_of_cen)
            _right = min(
                _hard_max, _SINGLE_GRID[_posn] - _num_left_of_cen + _points - 1
            )
        else:  # elif not hard
            _left = max(1, _SINGLE_GRID[_posn] - _num_left_of_cen)
            _right = _left + _points - 1
        del _num_left_of_cen


    if int(_left) != _left:
        raise ValueError(f"'_left' is not an integer ({_left})")


    if int(_right) != _right:
        raise ValueError(f"'_right' is not an integer ({_right})")

    _left = int(_left)
    _right = int(_right)

    if _left > _right:
        raise ValueError(f"_left ({_left}) > _right ({_right})")


    _OUT_GRID = np.linspace(_left, _right, int(_right-_left+1)).tolist()

    del _left, _right

    _OUT_GRID = list(map(int, _OUT_GRID))


    return _OUT_GRID




