# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases import GridsType, BestParamsType



def _validate_best_params(
    _GRIDS: GridsType,
    _pass: int,
    _best_params_from_previous_pass: BestParamsType,
) -> None:
    """
    Check that:

    - `_best_params_from_previous_pass` is (still) dict (this is a parent
        GridSearch output and is beyond the control of pybear.)
    - params (keys) returned in `_best_params_from_previous_pass` match
        those passed by GRIDS in quantity and values
    - values returned in `best_params_` were in the allowed search space

    Parameters
    ----------
    _GRIDS : GridsType
        `param_grid` for each round.
    _pass : int
        Zero-indexed pass of `GridSearchCV`.
    _best_params_from_previous_pass : BestParamsType
        `best_params_` as returned by parent `GridSearchCV`.

    Returns
    -------
    None

    """


    # best_params_ from sklearn GridSearchCV looks like
    # {'C': 1, 'l1_ratio': 0.9}

    if not isinstance(_best_params_from_previous_pass, dict):
        raise TypeError(
            f'best_params_from_previous_pass is not a dict. Has '
            f'GridSearchCV best_params_ output changed?'
        )


    _, __ = len(_best_params_from_previous_pass), len(_GRIDS[_pass - 1])
    if _ != __:
        raise ValueError(
            f'len(best_params_from_previous_pass) ({_}) != len(params)'
            f' from previous pass ({__})'
        )
    del _, __

    for param_ in _best_params_from_previous_pass:
        # VALIDATE best_param_ KEYS WERE IN GRIDS
        if param_ not in _GRIDS[_pass - 1]:
            raise ValueError(
                f'{param_} in best_params_from_previous_pass is not in '
                f'params given by GRIDS on the previous pass'
            )

        # VALIDATE THAT RETURNED best_params_ HAS VALUES THAT ARE WITHIN
        # THE PREVIOUS SEARCH SPACE
        _value = _best_params_from_previous_pass[param_]
        _OLD_GRID = _GRIDS[_pass - 1][param_]
        if _value not in _OLD_GRID:
            raise ValueError(
                f"{param_}: best_params_ contains a value ({_value}, "
                f"type={type(_value)}) that was not in its given search "
                f"space ({_OLD_GRID}, types={list(map(type, _OLD_GRID))})"
            )
        del _OLD_GRID


    for param_ in _GRIDS[_pass - 1]:
        # VALIDATE GRID KEYS ARE IN best_params_from_previous_pass
        if param_ not in _best_params_from_previous_pass:
            raise ValueError(
                f'{param_} in GRIDS[{_pass}] is not in '
                f'best_params_from_previous_pass'
            )






