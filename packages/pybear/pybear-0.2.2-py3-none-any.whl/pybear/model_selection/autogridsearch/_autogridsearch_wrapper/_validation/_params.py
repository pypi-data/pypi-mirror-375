# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers

from ._params_numerical import _val_numerical_param_value
from ._params_string import _val_string_param_value
from ._params_bool import _val_bool_param_value

from .._type_aliases import InParamsType



def _val_params(
    _params: InParamsType,
    _total_passes: int
) -> None:
    """Validate numerical, string, and bool params within `_params`
    vis-à-vis `total_passes`.

    dict key must be a string. dict value must be list-like with len==3.

    First position of value must be a non-empty list-like that contains
    the search grid for the first pass. The contents of the first search
    grid are validated within the submodules for the different datatypes.

    Second position of value, 'points', must be a single integer >= 1 or
    a list-type of such integers. If passed as list, the length must
    equal 'total_passes'. If points are passed as integer, later in
    conditioning points are converted to list with `len==total_passes`.
    For any pass where 1 is entered as points, all points thereafter
    must be 1. For fixed float, integer, string or bool, the 'points'
    values must be either the length of the first search grid or 1 (then
    1 thereafter), e.g., [3,3,3,1,1].

    Third position of value must be a string in 'soft_float', 'hard_float',
    'fixed_float', 'soft_integer', 'hard_integer', 'fixed_integer',
    'fixed_string', 'fixed_bool'.

    Parameters
    ----------
    _params : InParamsType
        A single dictionary that contains parameter names as keys and
        list-likes that follow the format rules for string, bool, and
        numerical parameters as values. AutoGridSearch does not accept
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
        to not count toward the originally-specified total number of
        passes. Read elsewhere in the docs for more information about
        'shifting' and 'drilling'.

    Returns
    -------
    None

    Examples
    --------
    string parameter:
        {'solver': [['saga', 'lbfgs'], [2, 1, 1], 'fixed_string']
    bool parameter:
        {'remove_empty_rows': [[True, False], 2, 'fixed_bool']
    numerical parameter:
        {'C': [[10, 20, 30], [3,3,3], 'soft_float']}
    a full parameter dictionary:
        {
            'C': [np.logspace(-5, 5, 11), [11, 11, 11], 'soft_float'],
            'l1_ratio': [np.linspace(0, 1, 21), [21, 6, 6], 'hard_float'],
            'solver': [['saga', 'lbfgs'], 2, 'fixed_string']
        }


    """


    # params ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    if not isinstance(_params, dict):
        raise TypeError(f"'params' must be a dictionary")

    if len(_params) == 0:
        raise ValueError(f"'params' is empty. Pass at least one parameter.")

    for _key, _value in _params.items():

        _base_err_msg = f"param '{str(_key)}' in :param: 'params' "

        # keys are strings
        if not isinstance(_key, str):
            raise TypeError(
                f"{_base_err_msg} --- \ndict key must be a string "
                f"corresponding to a parameter of an estimator"
            )

        # validate outer container ** * ** * ** * ** * ** * ** * ** * **
        _err_msg = (
            f"{_base_err_msg} --- "
            f"\ndict value must be list-like with len==3"
        )
        try:
            iter(_value)
            if isinstance(_value, (dict, str, set)):
                raise Exception
            if len(_value) != 3:
                raise UnicodeError
        except UnicodeError:
            raise ValueError(_err_msg)
        except Exception as e:
            raise TypeError(_err_msg)
        del _err_msg
        # END validate outer container ** * ** * ** * ** * ** * ** * **

        # last posn of value must be a string of dtype / search type **
        allowed = [
            'soft_float', 'hard_float', 'fixed_float', 'soft_integer',
            'hard_integer', 'fixed_integer', 'fixed_string', 'fixed_bool'
        ]

        err_msg = (
            f"{_base_err_msg} --- "
            f"\nthird position in value must be a string in "
            f"\n[{', '.join(allowed)}]"
            f"\ncase sensitive!"
        )

        if not isinstance(_value[2], str):
            raise TypeError(err_msg)

        if _value[2] not in allowed:
            raise ValueError(err_msg)

        del allowed, err_msg

        # END last posn of value must be a string of dtype / search type ** *


        # first grid ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        _err_msg = (f"{_base_err_msg} -- "
            f"\nfirst position in value must be a non-empty list-like "
            f"\nthat contains the search grid for the first pass. "
            f"\nDuplicate grid points are not allowed. "
        )
        try:
            iter(_value[0])
            if isinstance(_value[0], (dict, str)):
                raise Exception
            if len(_value[0]) == 0:
                _addon = f"got empty."
                raise UnicodeError
            if len(set(_value[0])) != len(_value[0]):
                _addon = f"got duplicates."
                raise UnicodeError
        except UnicodeError:
            raise ValueError(_err_msg + _addon)
        except Exception as e:
            raise TypeError(_err_msg)

        # END first grid ** * ** * ** * ** * ** * ** * ** * ** * ** * **


        # validate points ** * ** * ** * ** * ** * ** * ** * ** * **

        # All params can take a list-type or a single integer for 'points'.
        # If any points are passed as lists, the length must equal 'total_passes'.
        # If no points are passed as lists, later in conditioning points are
        # converted to lists with len==total_passes.

        err_msg = (
            f"{_base_err_msg} -- \n'points' must be "
            f"\n(i) a non-bool integer >= 1 or "
            f"\n(ii) a list-type of non-bool integers >=1 with len==passes"
            f"\ngot {_value[1]}, total_passes={_total_passes}"
        )

        # this is a helper only for easier validation, this is not returned
        if isinstance(_value[1], numbers.Number):
            _helper_list = [_value[1] for _ in range(_total_passes)]
        else:
            _helper_list = _value[1]

        try:
            iter(_helper_list)
            if isinstance(_helper_list, (dict, str)):
                raise Exception
            # NUMBER OF POINTS IN points MUST MATCH NUMBER OF PASSES
            if len(_helper_list) != _total_passes:
                raise UnicodeError
            # IF A NON-NUMERIC IS IN POINTS
            map(float, _helper_list)
            # IF A BOOL IS IN POINTS
            if any(map(isinstance, _helper_list, (bool for _ in _helper_list))):
                raise Exception
            # IF A FLOAT IS IN points
            if any(int(i) != i for i in map(float, _helper_list)):
                raise Exception
            # IF ANY INT IN points IS LESS THAN 1
            if min(_helper_list) < 1:
                raise UnicodeError
        except UnicodeError:
            raise ValueError(err_msg)
        except Exception as e:
            raise TypeError(err_msg)

        del err_msg

        _helper_list = list(map(int, _helper_list))

        # IF NUMBER OF POINTS IS EVER SET TO 1, ALL SUBSEQUENT POINTS MUST BE 1
        for idx, points in enumerate(_helper_list[:-1]):
            if points == 1 and _helper_list[idx + 1] > 1:
                raise ValueError(
                    f"{_base_err_msg} -- \nonce number of points is set "
                    f"to 1, all subsequent points must be 1. "
                    f"\ngot {_value[1]}"
                )


        # the desired behavior is that if a user enters this [[1,2,3], 1, ...]
        # then the first points is automatically set to len grid, and all
        # passes after just run the single best value: points = [3, 1, 1, ... ]
        # later in conditioning, if the user passed a list simply overwrite
        # whatever user put in 0 slot for points, without notifying if
        # original entry was erroneous

        # 'fixed' points must be in [1 or len(first grid)] (the first points
        # will be automatically set to len(_value[0]) by conditioning,
        # so only check the values in [1:]
        if 'fixed' in _value[2]:
            if any(map(lambda x: x not in [1, len(_value[0])], _helper_list[1:])):
                raise ValueError(
                    f"{_base_err_msg} -- \nif fixed int/float/str/bool, number "
                    f"of points can only be len(first grid) or 1. "
                    f"\ngot {_value[1]}"
                )

        del _helper_list

        # END validate points ** * ** * ** * ** * ** * ** * ** * ** *


        if _value[2] == 'fixed_string':
            _val_string_param_value(_key, _value)
        elif _value[2] == 'fixed_bool':
            _val_bool_param_value(_key, _value)
        else:
            _val_numerical_param_value(
                _key, _value, _total_passes
            )










