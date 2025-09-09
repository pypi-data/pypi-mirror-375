# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases import (
    DataType,
    GridType,
    ParamType,
    LogspaceType
)

from copy import deepcopy

import numpy as np



def _shift_grid(
    _single_param: ParamType,
    _single_old_grid: GridType,
    _single_is_logspace: LogspaceType,
    _single_best: DataType
) -> GridType:
    """Left-shift or right-shift a single linear-space or log-space
    search grid.

    Remember: `_single_old_grid` is the grid out of the last grid search,
    and is not necessarily the same as the grid in `_single_param` which
    is the first round search grid. Cannot simply take the grid out of
    a `_single_param` and call it `_single_old_grid`.

    Parameters
    ----------
    _single_param : ParamType
        Instruction set out of `params` for a single parameter.
    _single_old_grid : GridType
        Most recent search grid for a single parameter.
    _single_is_logspace : LogspaceType
        `IS_LOGSPACE` value for a single parameter.
    _single_best : DataType
        Best value returned in best_params_ for a single parameter.

    Returns
    -------
    NEW_GRID : GridType
        Left-shifted or right-shifted grid.

    """

    # linspace/logspace, which edge it landed on (if any), number
    # of points, log gap matters here


    # ALREADY KNOW IF linspace/logspace FROM IS_LOGSPACE

    if len(_single_param) != 3:
        raise ValueError(
            f"_single_param is not a proper param value, must be \n"
            f"[[grid], [points], 'data/search type']"
        )

    try:
        list(map(float, _single_old_grid))
    except:
        raise ValueError(f"attempting to shift a non-numeric search grid")

    if _single_param[-1].lower() == 'fixed_string':
        raise ValueError(f"_single_param is non-numeric")

    if 'soft' not in _single_param[-1].lower():
        raise ValueError(
            f"parameter must be 'soft' to do a shift, cannot be 'hard' "
            f"or 'fixed'"
        )


    _NEW_GRID = np.array(deepcopy(_single_old_grid))

    # GET WHICH EDGE _best LANDED ON (IF ANY)
    _left = np.isclose(_single_best, min(_NEW_GRID), rtol=1e-6)
    _right = np.isclose(_single_best, max(_NEW_GRID), rtol=1e-6)

    if not _left and not _right:
        raise ValueError(
            f"_shift_grid(): a param got into _shift_grid but _best did "
            f"not fall on a left or right edge"
        )

    if _single_is_logspace:
        _NEW_GRID = np.log10(_NEW_GRID)

    # left shift offset = GRID += (second lowest number - max)
    # right shift offset = GRID += (second highest number - min)

    if _left:
        _offset = _NEW_GRID[1] - max(_NEW_GRID)
    elif _right:
        _offset = _NEW_GRID[-2] - min(_NEW_GRID)

    del _left, _right


    _NEW_GRID += _offset
    del _offset


    if 'float' in _single_param[-1]:
        # 0 is the universal hard lower bound for floats. if shift
        # caused any float to fall below 0, bump the entire grid up
        # so that the lowest value in the grid is 0.
        if _single_is_logspace:
            _NEW_GRID = 10 ** _NEW_GRID
        else:
            if any(_NEW_GRID < 0):
                _NEW_GRID += np.abs(min(_NEW_GRID))

        _NEW_GRID = list(map(float, _NEW_GRID.tolist()))

    elif 'integer' in _single_param[-1]:
        # 1 is the universal hard lower bound for ints. if shift
        # caused any int to fall below 1, bump the entire grid up so
        # that the lowest value in the grid is 1

        if _single_is_logspace:
            if any(_NEW_GRID < 0):   # meaning 10^0
                _NEW_GRID += np.abs(min(_NEW_GRID))
            _NEW_GRID = 10 ** _NEW_GRID

        elif not _single_is_logspace and any(_NEW_GRID < 1):
            _NEW_GRID += (np.abs(min(_NEW_GRID)) + 1)

        _NEW_GRID = list(map(int, _NEW_GRID.tolist()))


    return _NEW_GRID







