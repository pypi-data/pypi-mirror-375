# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Literal
from ..._type_aliases import LogspaceType

import numpy as np

from .._float._float import _float
from .._int._int import _int
from .._string._string import _string
from .._bool._bool import _bool

from ..._type_aliases import (
    DataType,
    ParamType,
    GridType
)



def _drill(
    _param_name: str,
    _grid: GridType,
    _param_value: ParamType,
    _is_logspace: LogspaceType,
    _pass: int,
    _best: DataType
) -> tuple[GridType, ParamType, Literal[False]]:
    """Produce the next gridsearch's `_grid` for individual parameters.

    All types (str, int, float) are handled here. Update `_params` with
    new `_points` if any of the individual type's algorithms override
    the user-entered number of points. Update `_is_logspace` for any
    parameters converted from logspace to linspace.

    Parameters
    ----------
    _param_name : str
        A parameter's key in `_params`.
    _grid : GridType
        A parameter's search grid from the last round of `GridSearchCV`.
    _param_value : ParamType
        The parameter's grid construction instructions from `_params`.
    _is_logspace : LogspaceType
        False for all string, hard numerics, and fixed numerics. For
        soft numerical params, if the space is linear, or some other
        non-standard interval, it is False. If it is logspace, the
        'truth' of being a logspace is represented by a number indicating
        the interval of the logspace. E.g., np.logspace(-5, 5, 11) would
        be represented by 1.0, and np.logspace(-20, 20, 9) would be
        represented by 5.0
    _pass : int
        Zero-indexed counter of number of gridsearches performed
        inclusive of this round. If this is the second gridsearch,
        `_pass` == 1.
    _best : DataType
        The best value for this parameter from the previous round as
        returned by `best_params_` from the parent `GridSearchCV`.

    Returns
    -------
    __ : tuple[GridType, ParamType, Literal[False]]

        _grid: GridType
            The new `_grid` for this parameter.
        _param_value : ParamType
            Grid construction instructions from `_params` for this
            parameter with any update to `_points`.
        _is_logspace : Literal[False]
            Updated `_is_logspace` for this parameter; everything
            entering here that is logspace should always be converted to
            linspace, so this should always return False.

    """

    _type = _param_value[-1]

    # string ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    if 'fixed_string' in _type:
        _grid = _string(
            _param_value,
            _grid,
            _pass,
            _best
        )
        # no change to len(_grid), must match what was already in _param_value
        # no change to _is_logspace
        return _grid, _param_value, _is_logspace

    # END string ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # bool ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    if 'fixed_bool' in _type:

        _grid = _bool(
            _param_value,
            _grid,
            _pass,
            _best
        )
        # no change to len(_grid), must match what was already in _param_value
        # no change to _is_logspace
        return _grid, _param_value, _is_logspace

    # END bool ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    _is_close = np.isclose(_grid, _best, atol=1e-50)

    if _is_close.sum() != 1:

        # 24_05_31. isclose is unexpectedly failing on this:
        # grid = [666668, 777778, 888888, 999998, 1000000]
        # best = 999998
        # is locating to 999998 and 1_000_000. Verified and confirmed in
        # jupyter notebook with various atols. In this case, attempt to
        # find a single match by slicing.

        _is_close = (np.array(_grid)==_best)

        if _is_close.sum() != 1:
            raise ValueError(f"{_param_name}: uniquely locating best_param "
                f"position in search grid is failing, should locate to 1 "
                f"position, but locating to {_is_close.sum()} positions"
                f"\ngrid = {_grid}\nbest = {_best}")

    _best_param_posn = int(np.arange(len(_grid))[_is_close][0])
    del _is_close


    _points = _param_value[1][_pass]

    if _points == 1:

        _grid = [_best]

        # no change to len(_grid), _param_value[1][_pass] must have been 1
        _is_logspace = False  # MAY HAVE ALREADY BEEN FALSE
        return _grid, _param_value, _is_logspace

    elif 'fixed' in _type:
        # THIS MUST BE AFTER _points == 1
        _grid = _param_value[0]
        # no change to len(_grid)
        # no change to _is_logspace
        return _grid, _param_value, _is_logspace


    if 'hard' in _type:
        _is_hard = True
    elif 'soft' in _type:
        _is_hard = False
    else:
        raise ValueError(f"{_param_name}: param type str must contain "
             f"'hard' or 'soft' ({_type.lower()})")

    # ONLY NEEDED FOR 'hard' NUMERICAL
    _hard_min = _param_value[0][0]
    _hard_max = _param_value[0][-1]

    if 'integer' in _type:

        _grid, _is_logspace = _int(
            _grid,
            _is_logspace,
            _best_param_posn,
            _is_hard,
            _hard_min,
            _hard_max,
            _points
        )

    elif 'float' in _type:

        _grid, _is_logspace = _float(
            _grid,
            _is_logspace,
            _best_param_posn,
            _is_hard,
            _hard_min,
            _hard_max,
            _points
        )

    else:
        raise ValueError(f"{_param_name}: param type must contain "
             f"'float' or 'integer' if not 'fixed' ({_type.lower()})")

    # IF ANY ADJUSTMENTS WERE MADE TO _points, CAPTURE IN numerical_params
    _param_value[1][_pass] = len(_grid)

    del _type, _points, _best_param_posn, _is_hard, _hard_min, _hard_max


    return _grid, _param_value, _is_logspace








