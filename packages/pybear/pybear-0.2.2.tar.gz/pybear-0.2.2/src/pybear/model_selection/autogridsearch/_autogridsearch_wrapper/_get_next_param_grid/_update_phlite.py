# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    ParamsType,
    BestParamsType,
    PhliteType,
    ParamGridType
)
import numpy as np



def _update_phlite(
    _PHLITE: PhliteType,
    _last_param_grid: ParamGridType,  # _GRIDS[_pass-1]
    _params: ParamsType,
    _best_params_from_previous_pass: BestParamsType
) -> PhliteType:
    """Update `PHLITE` (param has landed inside the edges) based on most
    recent results in `_best_params_from_previous_pass` subject to the
    rules for "landing inside the edges".

    The only params that populate `PHLITE` are soft linspace & soft
    logspace.

    ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    Rules for landing inside the edges

    1) if soft landed inside the edges, then truly landed "inside the
        edges" and won't be shifted (True)
    2) if only one option in its grid, cannot be shifted (True)
    3) if landed on an edge, but that edge is a universal hard bound
        (0 FOR float, 1 FOR int) then won't be shifted (True)
    4) if landed on an edge, but that edge is not a universal hard bound,
        user hard bound, or fixed, then shift (stays or re-becomes False)
        (user hard or user fixed cannot get in here because `PHLITE` is
        only populated with soft.)

    Parameters
    ----------
    _PHLITE : PhliteType
        Dictionary for soft estimator parameters indicating if the
        parameter's best result was off the edges of it's last search
        grid (True) or was on one of the edges (False).
    _last_param_grid : ParamGridType
        The param grid from the last search round, i.e., the dict of
        param names and grids passed to the `param_grid` (or something
        similar) parameter of the parent GridSearch.
    _params : ParamsType
        The full set of parameters and their instructions for agscv.
    _best_params_from_previous_pass : BestParamsType
        The full set of parameters and their best values from the last
        round of grid search.

    Returns
    -------
    _PHLITE : PhliteType
        Updated PHLITE dict for the landing spots in the last pass.

    """


    for _param in _PHLITE:

        if 'soft' not in _params[_param][-1]:
            raise ValueError(
                f"'PHLITE' has a non-soft parameter in it --- "
                f"\n{_param}: {_params[_param][-1]}"
            )

        _best = _best_params_from_previous_pass[_param]
        _grid = _last_param_grid[_param]

        _edge_finder = np.abs(np.array(_grid) - _best)
        if _edge_finder[0] == 0 or _edge_finder[-1] == 0:
            _PHLITE[_param] = False
        else:
            _PHLITE[_param] = True
        del _edge_finder

        if len(_grid) == 1:
            _PHLITE[_param] = True

        if 'integer' in _params[_param][-1] and _best == 1:
            _PHLITE[_param] = True

        if 'float' in _params[_param][-1] and _best == 0:
            _PHLITE[_param] = True


    try:
        del _best, _grid, _edge_finder
    except:
        pass


    return _PHLITE







