# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    InParamsType,
    ParamsType
)

import numpy as np



def _cond_params(
    _params: InParamsType,
    _total_passes: int
) -> ParamsType:
    """Standardize the format of `params`, vis-à-vis `total_passes`.

    Parameters
    ----------
    _params : InParamsType
        A single dictionary that contains parameter names as keys and
        list-likes that follow the format rules for string, bool, and
        numerical parameters as values. `AutoGridSearch` does not accept
        lists of multiple params dictionaries in the same way that
        scikit-Learn accepts multiple param_grids.
    _total_passes : int
        The number of grid searches to perform. The actual number of
        passes run can be different from this number based on the setting
        for `total_passes_is_hard`. If `total_passes_is_hard` is True,
        then the maximum number of total passes will always be the value
        assigned to `total_passes`. If `total_passes_is_hard` is False,
        a round that performs a 'shift' operation will increment the
        allowed total number of passes, essentially causing shift passes
        to not count toward the original-entered total number of passes.
        Read elsewhere in the docs for more information about 'shifting'
        and 'drilling'.

    Returns
    -------
    _params : ParamsType
        Dictionary of grid-building instructions for all parameters.

    Examples
    --------
    string parameter:
        {'solver': [['saga', 'lbfgs'], [2, 2, 2], 'fixed_string']
    bool parameter:
        {'remove_empty_rows': [[True, False], [2, 2, 2], 'fixed_bool']
    numerical parameter:
        {'C': [[10, 20, 30], [3, 3, 3], 'soft_float']}
    a full parameter dictionary:
        {
            'C': [np.logspace(-5, 5, 11), [11, 11, 11], 'soft_float'],
            'l1_ratio': [np.linspace(0, 1, 21), [21, 6, 6], 'hard_float'],
            'solver': [['saga', 'lbfgs'], [2, 2, 2], 'fixed_string']
        }

    """


    # _total_passes must be int >= 1

    # when points are passed as lists, len must equal 'total_passes'.
    # All params can take a list-type or a single integer for 'points'.
    # If a param is passed with a an int for points, the total_passes
    # arg is used to build the points list.


    assert isinstance(_params, dict)

    # 25_05_10 pytest session fixtures for params are showing that params
    # is mutated somewhere. create a new copy of params, and do the
    # conditioning on that, not the original self.params
    _cond_params = {}

    for _key, _value in _params.items():


        _value = list(_value)

        _value[2] = _value[2].lower()


        # standardize first_grid in 0 slot ** * ** * ** * ** * ** * ** *

        _value[0] = list(_value[0])

        if 'integer' in _value[-1]:
            _value[0] = list(map(int, np.sort(list(_value[0]))))
        elif 'float' in _value[-1]:
            _value[0] = list(map(float, np.sort(list(_value[0]))))
        elif 'string' in _value[-1]:
            _value[0] = list(map(str, list(_value[0])))

        # END standardize first_grid in 0 slot ** * ** * ** * ** * ** *


        # standardize points ** * ** * ** * ** * ** * ** * ** * ** * **
        try:
            iter(_value[1])  # IF IS A SINGLE NON-SEQUENCE, CONVERT TO LIST
            _value[1] = list(map(int, _value[1]))
        except Exception as e:
            _value[1] = [int(_value[1]) for _ in range(_total_passes)]

        # the desired behavior is that if a user enters this [[1,2,3], 1, ...]
        # then the first points is automatically set to len grid, and all
        # passes after just run the single best value: points = [3, 1, 1, ... ]
        # simply overwrite whatever user put in 0 slot for points, without
        # notifying if original entry was erroneous
        _value[1][0] = len(_value[0])
        # END standardize points part 1 ** * ** * ** * ** * ** * ** * **

        _cond_params[_key] = _value


    return _cond_params






