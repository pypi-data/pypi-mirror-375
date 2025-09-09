# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases_str import (
    StrDataType,
    StrParamType,
    StrGridType
)



def _string(
    _param_value: StrParamType,
    _grid: StrGridType,
    _pass: int,
    _best_param_from_previous_pass: StrDataType
) -> StrGridType:
    """Create the current round's search grid for a string parameter
    based on results from `best_params_`.

    Parameters
    ----------
    _param_value : StrParamType
        String parameter grid instructions.
    _grid : StrGridType
        Previous round's gridsearch values for string parameter.
    _pass : int
        Zero-indexed count of passes to this point, inclusive; the
        current pass.
    _best_param_from_previous_pass : str
        Best value returned from parent GridSearch's `best_params_`.

    Returns
    -------
    _grid : StrGridType
        New search grid for the current pass.

    """


    # pass is zero-indexed, _param_value[1] is not
    if _param_value[1][_pass] == 1:
        # _best_param_from_previous_pass] is a single value, wrap with []
        _grid = [_best_param_from_previous_pass]
    else:
        _grid = _param_value[0]


    return _grid



