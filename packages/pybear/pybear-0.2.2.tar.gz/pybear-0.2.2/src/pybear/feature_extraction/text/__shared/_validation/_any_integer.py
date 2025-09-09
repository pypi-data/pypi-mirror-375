# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
)

import numbers



def _val_any_integer(
    _int:int | Sequence[int],
    _name:str = 'unnamed integer',
    _min:numbers.Real = float('-inf'),
    _max:numbers.Real = float('inf'),
    _disallowed:Sequence[int] = [],
    _can_be_bool:bool = False,
    _can_be_None:bool = False
) -> None:
    """Validate any integer or sequence of integers.

    Must be an integer.

    Must be >= '_min'

    Must be <= '_max'

    Must not be in '_disallowed'

    If '_can_be_bool' is True, '_int' can be bool.

    If '_can_be_None' is True, '_int' can be None.

    If '_int' is a sequence, then every value in it must obey the given
    rules.

    Parameters
    ----------
    _int : int | Sequence[int]
        Number to be validated whether it is an integer.
    _min : numbers.Real, default=float('-inf')
        The minimum allowed value '_int' can take.
    _max : numbers.Real, default=float('inf')
        The maximum allowed value '_int' can take.
    _disallowed : Sequence[int], default=[]
        Values that '_int' is not allowed to take.
    _can_be_bool : bool, default=False
        If True, '_int' can be boolean.
    _can_be_None : bool, default=False
        If True, '_int' can be None.

    Returns
    -------
    None

    """


    # validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    if not isinstance(_name, str):
        raise TypeError(f"'_name' must be a string. got {_name}.")
    if not isinstance(_min, numbers.Real):
        raise TypeError(f"'_min' must be a number. got {_min}.")
    if not isinstance(_max, numbers.Real):
        raise TypeError(f"'_max' must be a number. got {_max}.")
    if _min > _max:
        raise ValueError(
            f"'_min' cannot be greather than '_max'. got {_min} and {_max}."
        )
    err_msg = (f"'_disallowed must be a python Sequence of integers. "
               f"\ngot {_disallowed}.")
    if not isinstance(_disallowed, Sequence):
        raise TypeError(err_msg)
    if not all(map(
        isinstance, _disallowed, (numbers.Integral for _ in _disallowed)
    )):
        raise TypeError(err_msg)
    del err_msg
    if not isinstance(_can_be_bool, bool):
        raise TypeError(f"'_can_be_bool' must be boolean. got {_can_be_bool}.")
    if not isinstance(_can_be_None, bool):
        raise TypeError(f"'_can_be_None' must be boolean. got {_can_be_None}.")

    # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # helper function -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    def _helper(
        _int:int | Sequence[int] | None,
    ) -> None:

        """Helper function for validating integers."""

        nonlocal _name, _min, _max, _disallowed, _can_be_bool, _can_be_None

        # manage err_msg -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _err_msg = f"Got {_int} for '{_name}'. '{_name}' must be"
        if _can_be_bool:
            _err_msg += " bool /"
        if _can_be_None:
            _err_msg += " None /"
        _err_msg += " integer"
        # END manage err_msg -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if _int is None and _can_be_None:
            return

        if isinstance(_int, bool) and not _can_be_bool:
            raise TypeError(_err_msg + ".")

        if not isinstance(_int, numbers.Integral):
            raise TypeError(_err_msg + ".")

        if _int < _min:
            raise ValueError(_err_msg + f" >= {_min}.")

        if _int > _max:
            raise ValueError(_err_msg + f" <= {_max}.")

        if _int in _disallowed:
            raise ValueError(_err_msg + f" and cannot be in {_disallowed}.")

        return

    # END helper function -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    _is_iter = False
    try:
        iter(_int)
        if isinstance(_int, str):
            raise Exception
        _is_iter = True
    except Exception as e:
        pass


    if not _is_iter:
        _helper(_int)
    elif _is_iter:

        # to make this raise errors in a nice orderly way that makes
        # test easier, rig this to raise TypeErrors before any ValueErrors

        _type_errors = []
        _value_errors = []
        for _i in _int:

            try:
                _helper(_i)
                _type_errors.append(False)
                _value_errors.append(False)
            except TypeError as t:
                _t = t
                _type_errors.append(True)
                _value_errors.append(False)
            except ValueError as v:
                _v = v
                _type_errors.append(False)
                _value_errors.append(True)
            except Exception as e:
                raise e


        if any(_type_errors):
            raise _t from None
        elif any(_value_errors):
            raise _v from None




