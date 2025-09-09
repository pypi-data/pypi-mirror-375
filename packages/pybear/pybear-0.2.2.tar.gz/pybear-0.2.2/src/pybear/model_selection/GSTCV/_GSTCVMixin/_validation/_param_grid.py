# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases import (
    ParamGridInputType,
    ParamGridsInputType
)

from ._param_grid_helper import _val_param_grid_helper



def _val_param_grid(
    _param_grid:ParamGridInputType | ParamGridsInputType,
    _must_be_list_dict:bool = True
) -> None:
    """Validate `_param_grid` and any `thresholds` that may have been
    passed inside.

    `_param_grid` can be a single param_grid or a list-like of
    param_grids.

    Validate format(s) is/are dict[str, list-like]. Validate `thresholds`
    is a list-like of numbers, with numbers in [0, 1] interval.

    Parameters
    ----------
    _param_grid : ParamGridInputType | ParamGridsInputType
        A `param_grid` is a dictionary with hyperparameter names (str)
        as keys and list-likes of hyperparameter settings to test as
        values. `_param_grid` can be one of the described param_grids or
        a list-like of such param_grids.
    _must_be_list_dict : bool, default=True
        Whether `_param_grid` must have already been conditioned into a
        list of dictionaries.

    Returns
    -------
    None

    """


    assert isinstance(_must_be_list_dict, bool)


    try:
        iter(_param_grid)
        if isinstance(_param_grid, str):
            raise Exception
    except Exception as e:
        raise TypeError(
            f"'param_grid' must be (1 - dictionary) or (2 - a list-like "
            f"of dictionaries). \nthe dictionary keys must be strings "
            f"and the dictionary values must be list-like."
        )

    # _param_grid must be iter
    if isinstance(_param_grid, dict):
        if _must_be_list_dict:
            raise TypeError(f"'param_grid' must be a list of dictionaries.")
        if len(_param_grid) == 0:
            return
        _dpg = [_param_grid]   # _dpg = dum_param_grid
    else:
        _dpg = list(_param_grid)
    # _dpg must be list[non-empty dict] or list[some non-string iterables]


    for _grid_idx, _grid in enumerate(_dpg):

        _val_param_grid_helper(_grid, _grid_idx)






