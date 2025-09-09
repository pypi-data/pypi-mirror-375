# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases_num import InNumParamType

import numbers

import numpy as np



def _val_numerical_param_value(
    _num_param_key: str,
    _num_param_value: InNumParamType,
    _total_passes: int
) -> None:
    """Validate `_num_param_value`.

    COMES IN AS
    list-like(
        list-like('grid_value1', etc.),
        int | Sequence[int],
        '{soft|hard|fixed}_{float|integer}'
    )

    validate numerical_params' dict value is a list-like that contains:
    (i) a list-like of first-round grid-search values (numbers)
    (ii) 'points' indicating search grids of len 2 are not allowed for
        'soft' numerical params
    (iii) literal string in 'soft_float', 'hard_float', 'fixed_float',
    'soft_integer', 'hard_integer', or 'fixed_integer'.

    Integer spaces must be >= 1 , float spaces must be >= 0.

    Logspace intervals must be integer >= 1. Meaning you cannot have
    powers that are like 10^0.5, 10^0.6, ..., but you can have powers
    like 10^2, 10^4, ...

    Parameters
    ----------
    _num_param_key : str
        The estimator parameter name to be grid-searched.
    _num_param_value : InNumParamType
        The list-like of instructions for the multi-pass grid search of
        this numerical parameter.
    _total_passes : int
        The total number of rounds of gridsearch entered by the user at
        init.

    Returns
    -------
    None

    """


    assert any(
        map(lambda x: x in _num_param_value[2], ('float', 'integer'))
    )


    _base_err_msg = \
        f"numerical param '{str(_num_param_key)}' in :param: 'params' "


    # validate contains [first_grid] in 0 slot ** * ** * ** * ** * ** *
    _err_msg = (f"{_base_err_msg} -- "
        f"\nfirst position of the value must be a non-empty list-like that "
        f"\ncontains the first pass grid-search values (numbers). "
    )

    try:
        if any(map(
            isinstance,
            _num_param_value[0],
            (bool for _ in _num_param_value[0])
        )):
            raise Exception
        list(map(float, _num_param_value[0]))
    except:
        raise TypeError(_err_msg)

    del _err_msg

    if 'integer' in _num_param_value[2]:

        if not all(int(i) == i for i in _num_param_value[0]):
            raise ValueError(
                f"{_base_err_msg} -- \nwhen numerical is integer (soft, "
                f"hard, or fixed), \nall search values must be integers. "
                f"\ngrid = {_num_param_value[0]}"
            )

        if _num_param_value[2] in ['hard_integer', 'soft_integer'] \
                and min(_num_param_value[0]) < 1:
            raise ValueError(
                f"{_base_err_msg} -- \nwhen numerical is hard/soft integer, "
                f"\nall search values must be >= 1. "
                f"\ngrid = {_num_param_value[0]}"
            )

    elif 'float' in _num_param_value[2]:

        if _num_param_value[2] in ['hard_float', 'soft_float'] \
                and (np.array(list(_num_param_value[0])) < 0).any():
            raise ValueError(
                f"{_base_err_msg} -- \nwhen numerical is hard/soft float, "
                f"\nall search values must be >= 0. "
                f"\ngrid = {_num_param_value[0]}")

    else:
        raise Exception


    # LOGSPACE
    if 'fixed' not in _num_param_value[2] \
            and len(_num_param_value[0]) >= 3 \
            and 0 not in _num_param_value[0]:

        # this sort is important, or the sign could come out negative
        log_grid = np.log10(sorted(list(_num_param_value[0])))
        log_gaps = log_grid[1:] - log_grid[:-1]
        _unq_log_gap = np.unique(np.round(log_gaps, 14))

        if len(_unq_log_gap) == 1:  # else is not a logspace
            # CURRENTLY ONLY HANDLES LOGSPACE BASE 10 OR GREATER
            if _unq_log_gap[0] < 1:
                raise ValueError(
                    f"{_base_err_msg} -- \nonly handles logspaces with "
                    f"base 10 or greater"
                )

            # 24_05_14_07_53_00 ENFORCING INTEGER FOR LOGSPACE MAKES MANAGING
            # GAPS IN DRILL SECTION A LOT EASIER
            if int(_unq_log_gap[0]) != _unq_log_gap[0]:
                raise ValueError(
                    f'{_base_err_msg} -- \nlogspaces must have integer intervals'
                )

        del log_grid, log_gaps, _unq_log_gap

    # END validate contains [first_grid] in 0 slot ** * ** * ** * ** *

    # validate points ** * ** * ** * ** * ** * ** * ** * ** * **

    # this is a helper only for easier validation! this is not returned
    if isinstance(_num_param_value[1], numbers.Number):
        _helper_list = [_num_param_value[1] for _ in range(_total_passes)]
    else:
        _helper_list = _num_param_value[1]


    _helper_list = list(map(int, _helper_list))


    if 'soft' in _num_param_value[2] and 2 in _helper_list:
        raise ValueError(
            f'{_base_err_msg} -- \nGrids of size 2 are not allowed for '
            f'"soft" numerical params'
        )

    del _helper_list

    # END validate points ** * ** * ** * ** * ** * ** * ** * ** *









