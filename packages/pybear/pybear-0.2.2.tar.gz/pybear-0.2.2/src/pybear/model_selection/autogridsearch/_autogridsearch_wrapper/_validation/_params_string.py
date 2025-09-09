# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases_str import InStrParamType



def _val_string_param_value(
    _string_param_key: str,
    _string_param_value: InStrParamType
) -> None:
    """Validate `_string_param_value`.

    COMES IN AS
    list-like(
        list-like('grid_value1', 'grid_value2', etc.),
        int | Sequence[int],
        'fixed_string'
    )

    validate string_params' dict value is a list-like that contains
    (i) a list-like of str/None values
    (ii) 'points' not validated here anymore
    (iii) 'fixed_string' (literal string 'fixed_string')

    Parameters
    ----------
    _string_param_key : str
        The estimator parameter name to be grid-searched.
    _string_param_value : InStrParamType
        The list-like of instructions for the multi-pass grid search of
        this string-valued parameter.

    Returns
    -------
    None

    """


    assert _string_param_value[2] == 'fixed_string'


    _base_err_msg = \
        f"string param '{str(_string_param_key)}' in :param: 'params' "


    # validate first position ** * ** * ** * ** * ** * ** * ** * ** * **
    # (i) a list of str values
    _err_msg = (f"{_base_err_msg} --- "
        f"\nfirst position of the value must be a non-empty list-like that "
        f"\ncontains the first pass grid-search values (strings or None). "
    )

    if not all(map(
        isinstance,
        _string_param_value[0],
        ((str, type(None)) for _ in _string_param_value[0])
    )):
        raise TypeError(_err_msg)

    del _err_msg
    # END validate first position ** * ** * ** * ** * ** * ** * ** * **


    del _base_err_msg





