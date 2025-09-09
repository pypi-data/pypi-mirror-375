# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



def _val_any_string(
    _str:str,
    _name:str = 'unnamed string',
    _can_be_None:bool = False
) -> None:
    """Validate that a parameter is a string, or None if allowed to be None.

    Parameters
    ----------
    _str : str
        The object to be validated as a string (or None).
    _name : str, default='unnamed string'
        The name of the parameter being validated.
    _can_be_None : bool
        Whether None can be accepted in place of a string.

    Returns
    -------
    None

    """


    # validation --- --- --- --- --- --- --- --- --- --- --- --- --- ---

    if not isinstance(_name, str):
        raise TypeError(f"'_name' must be a string. got {type(_name)}.")

    if not isinstance(_can_be_None, bool):
        raise TypeError(f"'_can_be_None' must be bool. got {type(_can_be_None)}.")

    # END validation --- --- --- --- --- --- --- --- --- --- --- --- ---


    if _can_be_None and _str is None:
        return


    if not isinstance(_str, str):
        raise TypeError(f"'{_name}' must be a string. got {type(_str)}.")






