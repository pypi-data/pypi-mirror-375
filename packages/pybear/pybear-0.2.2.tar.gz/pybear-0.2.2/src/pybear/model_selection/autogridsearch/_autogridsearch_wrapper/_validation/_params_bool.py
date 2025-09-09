# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases_bool import InBoolParamType



def _val_bool_param_value(
    _bool_param_key: str,
    _bool_param_value: InBoolParamType
) -> None:
    """Validate `_bool_param_value`.

    COMES IN AS
    list-like(
        list-like('grid_value1', etc.),
        int | Sequence[int],
        'fixed_bool'
    )

    validate bool_params' dict value is a list-like that contains
    (i) a list-like of bool and/or None values
    (ii) 'points' not validated here anymore
    (iii) 'fixed_bool' (literal string 'fixed_bool')

    Parameters
    ----------
    _bool_param_key : str
        The estimator parameter name to be grid-searched.
    _bool_param_value : InBoolParamType
        The list-like of instructions for the multi-pass grid search of
        this boolean-valued parameter.

    Returns
    -------
    None

    """


    assert _bool_param_value[2] == 'fixed_bool'


    _base_err_msg = f"bool param '{str(_bool_param_key)}' in :param: 'params' "


    # validate first position ** * ** * ** * ** * ** * ** * ** * ** * **
    # (i) a list of bool values
    _err_msg = (f"{_base_err_msg} --- "
        f"\nfirst position of the value must be a non-empty list-like that "
        f"\ncontains the first pass grid-search values (booleans or None)."
    )

    if not all(map(
        isinstance,
        _bool_param_value[0],
        ((bool, type(None)) for _ in _bool_param_value[0])
    )):
        raise TypeError(_err_msg)

    del _err_msg
    # END validate first position ** * ** * ** * ** * ** * ** * ** * **


    del _base_err_msg





