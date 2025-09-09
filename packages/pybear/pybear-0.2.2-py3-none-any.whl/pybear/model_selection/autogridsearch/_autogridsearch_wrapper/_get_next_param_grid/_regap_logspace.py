# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy as np
from .._type_aliases_num import (
    NumDataType,
    NumGridType,
    NumParamType
)



def _regap_logspace(
    _param_name: str,
    _grid: NumGridType,
    _is_logspace: float,
    _param_value: NumParamType,
    _pass: int,
    _best_param_from_previous_pass: NumDataType,
    _hard_min: NumDataType,
    _hard_max: NumDataType
) -> tuple[NumGridType, NumParamType, float]:
    """If a logspace numerical parameter has log gap > 1 and has landed
    inside the edges of its grid (or is forced into here due to
    `max_shifts`), re-gap the logspace to 1.

    Parameters
    ----------
    _param_name : str
        Parameter's key in `params`.
    _grid : NumGridType
        The previous search grid for a single logspace param which will
        be regapped here for the current round.
    _is_logspace : float
        The log interval of the parameter's search space.
    _param_value : NumParamType
        agscv instructions this single logspace parameter.
    _pass : int
        The index of the current pass (upcoming gridsearch).
    _best_param_from_previous_pass : NumDataType
        Best result for this param from `best_params_` returned by the
        parent `GridsearchCV`.
    _hard_min : NumDataType
        If hard, the minimum value in the first round's search grid.
        Ignored otherwise.
    _hard_max : NumDataType
        If hard, the maximum value in the first round's search grid.
        Ignored otherwise.

    Returns
    -------
    __ : tuple[NumGridType, NumParamType, float]
        _NEW_GRID : NumGridType
            `_grid` updated with logspace intervals reduced to 1.
        _param_value : NumParamType
            `_param` updated with points reflective of new points for
            logspace interval == 1
        _is_logspace : float
            Updated with the unitized gaps, should be 1.0

    """

    # _param_value = deepcopy(_param_value)

    if not _is_logspace > 1:
        # 24_05_20_11_09_00
        # raise ValueError(f"{_param_name}: logspace==1 in _regap_logspace")
        # this should not happen due to conditions in _get_next_param_grid
        # but if it does, simply return the inputs
        return _grid, _param_value, _is_logspace

    # validate hard_min hard_max ** * ** * ** * ** * ** * ** * ** * ** *
    if 'hard' in _param_value[-1]:
        err_msg = (f"_regap_logspace non-int log10(_hard_min), "
                   f"\n_hard_min = {_hard_min}")
        try:
            _log_hard_min = float(np.log10(_hard_min))
        except:
            raise TypeError(err_msg)

        if int(_log_hard_min) != _log_hard_min:
            raise ValueError(err_msg)
        del err_msg

        err_msg = (f"_regap_logspace non-int log10(_hard_max), "
                   f"\n_hard_max = {_hard_max}")
        try:
            _log_hard_max = float(np.log10(_hard_max))
        except:
            raise TypeError(err_msg)

        if int(_log_hard_max) != _log_hard_max:
            raise ValueError(err_msg)
        del err_msg

        _log_hard_min = int(_log_hard_min)
        _log_hard_max = int(_log_hard_max)

    else:  # if soft
        _log_hard_min = float('-inf')
        _log_hard_max = float('inf')

    # END validate hard_min hard_max ** * ** * ** * ** * ** * ** * ** *

    _LOG_OLD_GRID = np.log10(_grid)

    _log_best = np.log10(_best_param_from_previous_pass)

    _log_gap = np.unique(_LOG_OLD_GRID[1:] - _LOG_OLD_GRID[:-1])

    if len(np.unique(_log_gap)) != 1:
        raise ValueError(
            f"{_param_name}: a logspace with a non-uniform gap in "
            f"_regap_logspace"
        )

    # this should equal _is_logspace
    _log_gap = abs(_log_gap[0])

    # if _max_shifts is reached before landing inside and edge, this param
    # could still be on an edge
    # GET WHERE _best LANDED ON
    _POSN = np.isclose(_LOG_OLD_GRID, _log_best, rtol=1e-6)
    if _POSN[0]:
        _posn = 0
    elif _POSN[-1]:
        _posn = len(_LOG_OLD_GRID) - 1
    elif any(_POSN[1:-1]):
        _posn = int(np.arange(len(_LOG_OLD_GRID))[_POSN][0])
    else:
        raise ValueError(
            f"{_param_name}: _regap_logspace cannot locate position of "
            f"best value within _LOG_OLD_GRID"
        )

    del _POSN

    # USE THE VALUES THAT FALL TO THE LEFT AND RIGHT OF
    # THE BEST VALUE TO CREATE A NEW RANGE WITH INCREMENT 1.
    if _posn == 0:
        _new_left = \
            int(max(_log_hard_min, np.floor(_LOG_OLD_GRID[0] - _log_gap)))
        _new_right = \
            int(min(_log_hard_max, np.ceil(_LOG_OLD_GRID[0] + _log_gap)))

        if 'int' in _param_value[-1]:
            _new_left = max(0, _new_left)

    elif (_posn > 0 and _posn < len(_LOG_OLD_GRID) - 1):
        _new_left = int(max(_log_hard_min, np.floor(_LOG_OLD_GRID[_posn - 1])))
        _new_right = int(min(_log_hard_max, np.ceil(_LOG_OLD_GRID[_posn + 1])))

    elif _posn == len(_LOG_OLD_GRID) - 1:
        _new_left = \
            int(max(_log_hard_min, int(np.floor(_LOG_OLD_GRID[-2]))))
        _new_right = \
            int(min(_log_hard_max, np.ceil(_LOG_OLD_GRID[-1] + _log_gap)))

    del _posn

    _points = abs(_new_right - _new_left) + 1
    _NEW_GRID = np.linspace(_new_left, _new_right, _points)
    del _points
    _NEW_GRID = np.power(10, _NEW_GRID)
    if 'integer' in _param_value[-1]:
        _NEW_GRID = list(map(int, _NEW_GRID.tolist()))
    elif 'float' in _param_value[-1]:
        _NEW_GRID = list(map(float, _NEW_GRID.tolist()))
    else:
        raise ValueError(
            f"{_param_name}: _regap_logspace not finding param dtype in "
            f"_param_value"
        )

    del _LOG_OLD_GRID, _new_left, _new_right

    # OVERWRITE PARAM'S COMING PASS'S _points WITH POINTS FOR GAP==1
    _param_value[1][_pass] = len(_NEW_GRID)


    return _NEW_GRID, _param_value, 1.0





