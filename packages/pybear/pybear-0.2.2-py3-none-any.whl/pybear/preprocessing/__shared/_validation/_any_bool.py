# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



def _val_any_bool(
    _bool:bool,
    _name:str = 'unnamed boolean',
    _can_be_None:bool = False
) -> None:
    """Validate `_bool`. Must be boolean.

    Parameters
    ----------
    _bool: bool
        Something that can only be boolean.
    _name : str, default='unnamed boolean'
        The name of the parameter being validated as boolean, or None if
        allowed.
    _can_be_None : bool, default=False
        Whether the boolean value is allowed to be passed as None.

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


    if _can_be_None and _bool is None:
        return


    if not isinstance(_bool, bool):
        raise TypeError(f"'{_name}' must be boolean.")






