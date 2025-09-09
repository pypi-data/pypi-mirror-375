# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases import (
    ParamGridInputType,
    ParamGridsInputType,
    ParamGridsWIPType,
    ThresholdsInputType
)

from ._thresholds import _cond_thresholds



def _cond_param_grid(
    _param_grid: ParamGridInputType | ParamGridsInputType,
    _thresholds: ThresholdsInputType    # this is init self.thresholds
) -> ParamGridsWIPType:
    """Condition `param_grid` and any thresholds that may be passed inside.

    Get it/them into list(dict[str, list[Any]]) format. If any grid does
    not have thresholds in it, put the init `thresholds` in it. Condition
    any thresholds that were passed in a `param_grid` into a py list of
    floats.

    Parameters
    ----------
    _param_grid : ParamGridInputType | ParamGridsInputType
        A 'param_grid' is a dictionary with hyperparameter names (str)
        as keys and list-likes of hyperparameter settings to test as
        values. `_param_grid` can be one of the described param_grids,
        or a list-like of such param_grids.
    _thresholds : ThresholdsInputType
        The global decision threshold strategy to use when performing
        hyperparameter search, for those param_grids that did not have
        thresholds passed inside.

    Returns
    -------
    _out_param_grid : ParamGridsWIPType
        Returns param grid(s) inside a list with thresholds inside every
        param_grid, no matter how (or if) thresholds was passed in the
        param_grid.

    """


    if len(_param_grid) == 0:
        _out_param_grid = [{}]
    elif isinstance(_param_grid, dict):
        _out_param_grid = [_param_grid]
    else:
        _out_param_grid = list(_param_grid)


    # param_grid must be list at this point
    for _grid_idx, _grid in enumerate(_out_param_grid):

        _new_grid = {}
        for _k, _v in _grid.items():
            if _k.lower() == 'thresholds':
                _new_grid['thresholds'] = _cond_thresholds(_grid['thresholds'])
            else:
                _new_grid[_k] = list(_v)
        else:
            if 'thresholds' not in _grid:
                _new_grid['thresholds'] = _cond_thresholds(_thresholds)

        _out_param_grid[_grid_idx] = _new_grid
        del _new_grid

    # at this point param_grid must be a list of dictionaries having
    # str as keys and lists as values

    return _out_param_grid





