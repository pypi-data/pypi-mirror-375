# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases import ParamGridInputType

import numbers

import numpy as np

from ._thresholds import _val_thresholds



def _val_param_grid_helper(
    _param_grid: ParamGridInputType,
    _grid_idx: int
) -> None:
    """Validate a single `param_grid` and `thresholds` if they were
    passed in the `param_grid`. Validate format is dict[str, list-like].
    Validate `thresholds` is a list-like of numbers, with numbers in
    [0, 1] interval.

    Parameters
    ----------
    _param_grid : ParamGridInputType
        Dictionary with hyperparameters names (str) as keys and
        list-likes of hyperparameter settings to try as values.
    _grid_idx : int
        The index of this grid in the sequence of grids if multiple
        grids were passed to GSTCV.

    Returns
    -------
    None

    """


    assert isinstance(_grid_idx, numbers.Integral)
    assert _grid_idx >= 0


    _err_msg = (f"a param_grid must be a dictionary with strings for keys "
        f"and non-empty list-likes for values.")


    if not isinstance(_param_grid, dict):
        raise TypeError(_err_msg)

    if len(_param_grid) == 0:
        return


    for _k, _v in _param_grid.items():

        if not isinstance(_k, str):
            raise TypeError(_err_msg + f"\ngot key == {_k}")

        if _k.lower() == 'thresholds':
            _val_thresholds(_v, False, _grid_idx, _must_be_list_like=True)
            continue

        # if not thresholds. it's some other parameter, dont validate the
        # innards, let the estimator do that.
        iter(_v)
        if isinstance(_v, (str, dict)):
            raise TypeError(_err_msg)
        if len(np.array(list(_v), dtype=object).shape) > 1:
            raise ValueError(_err_msg)
        if len(_v) == 0:
            raise ValueError(_err_msg)
        # we have a legit 1D








