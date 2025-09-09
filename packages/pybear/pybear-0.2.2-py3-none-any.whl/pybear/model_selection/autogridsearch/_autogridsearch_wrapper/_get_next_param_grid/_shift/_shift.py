# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases import (
    GridsType,
    ParamsType,
    BestParamsType,
    IsLogspaceType,
    PhliteType
)

from copy import deepcopy

import numpy as np

from ._shift_points_and_passes import _shift_points_and_passes

from ._shift_grid import _shift_grid



def _shift(
    _GRIDS: GridsType,
    _PHLITE : PhliteType,
    _IS_LOGSPACE: IsLogspaceType,
    _params: ParamsType,
    _pass: int,
    _best_params_from_previous_pass: BestParamsType,
    _total_passes_is_hard: bool
) -> tuple[GridsType, ParamsType]:
    """When prompted by False value(s) for any param(s) in PHLITE, shift
    the respective params' grids based on whether the best value fell
    on a left or right edge of the search grid.

    When there is a shift, update the 'points' field in `_params` to
    replicate the last round's number of points into the current round.
    (During a shift, the values in the search grid are being reduced or
    increased, but the number of points in the grid does not change.)
    Essentially, the last gridsearch is to be repeated identically except
    that any params landing on the edges of their ranges are shifted.

    If `total_passes_is_hard` is False, inserting a shift pass into the
    search increases the total number of passes by 1. If True, the shift
    pass is inserted and what previously would have been the final pass
    is truncated, preserving the original number of total passes.

    Parameters
    ----------
    _GRIDS : GridsType
        Holds all of the param_grids run so far, and an empty dict for
        the current pass, to be filled here.
    _PHLITE : PhliteType
        Holds bools for soft params indicating if it is to be shifted.
    _IS_LOGSPACE : IsLogspaceType
        `_IS_LOGSPACE` is a dictionary keyed by all param names,
        including string params. String params are always False. For
        numerical params, if the space is linear, or some other
        non-standard interval, it is False. If it is logspace, The
        'truth' of being a logspace is represented by a number indicating
        the interval of the logspace. E.g., np.logspace(-5, 5, 11) would
        be represented by 1.0, and np.logspace(-20, 20, 9) would be
        represented by 5.0.
    _params : ParamsType
        Search instructions for each param
    _pass : int
        The index of the current gridsearch we are preparing to do by
        being in here.
    _best_params_from_previous_pass : BestParamsType
        `best_params_` from the parent GridsearchCV
    _total_passes_is_hard : bool
        Whether to increment total_passes when a shift is needed.

    Returns
    -------
    __ : tuple[GridsType, ParamsType]
        _GRIDS : GridsType
            `_GRIDS` filled with new grids for the current pass.
        _params : ParamsType
            `_params` with updated points field.

    """


    # we are in this module because at least 1 False was in PHLITE,
    # meaning at least 1 numerical was on an edge, which means a shift
    # will happen and the next coming pass will have identical number of
    # points for all params (unless a logspace happens to get regapped,
    # which would happen after this, and points for the those params
    # would also be adjusted again there).


    try:
        _GRIDS[_pass]
    except:
        raise ValueError(f"_GRIDS does not have key for {_pass}")


    if _GRIDS[_pass] != {}:
        raise ValueError(
            f"_GRIDS pass {_pass} going into _shift is not empty."
        )


    for _param in _params:

        _OLD_GRID = np.array(deepcopy(_GRIDS)[_pass - 1][_param])
        _OLD_GRID.sort()

        if _PHLITE.get(_param, True) == True:
            # only 'soft' nums are in PHLITE; doing a get() on anything
            # else (hard/fixed/string) will enter here and copy over old
            # grid to next pass. anything that is in PHLITE and has
            # landed inside the edges will also enter here and carry old
            # grid over to the next pass.
            _GRIDS[_pass][_param] = _OLD_GRID.tolist()

        elif _PHLITE.get(_param, True) == False:

            _best = _best_params_from_previous_pass[_param]

            _GRIDS[_pass][_param] = _shift_grid(
                _params[_param],
                _OLD_GRID.tolist(),
                _IS_LOGSPACE[_param],
                _best
            )

            del _OLD_GRID, _best


    # This must remain separate from grid shift because all points/passes
    # are always shifted even if only one param's grid is actually shifted.


    _params = _shift_points_and_passes(
        deepcopy(_params),   # 25_04_23 verified deepcopy needs to be here
        _pass,
        _total_passes_is_hard
    )


    return _GRIDS, _params


























