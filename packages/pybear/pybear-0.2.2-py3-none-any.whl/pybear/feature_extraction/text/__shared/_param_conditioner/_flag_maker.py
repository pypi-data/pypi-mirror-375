# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    TypeAlias,
)

import re



CaseSensitiveType: TypeAlias = bool | list[bool | None]

FlagType: TypeAlias = None | int
FlagsType: TypeAlias = FlagType | list[FlagType]



def _flag_maker(
    _compile_holder: list[list[None] | list[re.Pattern[str]]],
    _case_sensitive: CaseSensitiveType,
    _flags: FlagsType
) -> list[list[None] | list[re.Pattern[str]]]:
    """
    Use flags inferred from _case_sensitive and any user-passed flags
    to put flags in the re.compile objects in _compile_holder. All string
    literals that were in _pattern_holder must already be converted to
    re.compile. _compile_holder can only contain [None]s and
    list[re.Pattern]s.

    Parameters
    ----------
    _compile_holder : RemoveType
        The string searching criteria converted entirely so that row-wise,
        _compile_holder is comprised of list[re.Pattern]s and [None]s.
    _case_sensitive : CaseSensitiveType
        The case-sensitive strategy as passed by the user.
    _flags : FlagsType
        The flags for searches as passed by the user.

    Returns
    -------
    _compile_holder : list[list[None] | list[re.Pattern[str]]]
        _compile_holder object with the appropriate flags now in every
        re.compile object.

    Notes
    -----
    
    **Type Aliases**

    CaseSensitiveType:
        bool | list[bool | None]
    FlagType:
        None | int
    FlagsType:
        FlagType | list[FlagType]

    """


    if _compile_holder is None:
        raise TypeError(
            f"'_compile_holder' is None, should have been handled elsewhere"
        )

    # if _case_sensitive and/or _flags are lists, the length was validated
    # against the data previously.

    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # get the setting for case_sensitive for the row in _X. if cs is list,
    # a value could be None or bool: set None to True

    for _idx, _row in enumerate(_compile_holder):

        if isinstance(_case_sensitive, bool):
            _cs_flags = re.I if _case_sensitive is False else 0
        elif isinstance(_case_sensitive, list):
            # if cs in list is True or None, keep case_sensitive (no flag)
            _cs_flags = re.I if _case_sensitive[_idx] is False else 0
        else:
            raise Exception

        if _flags is None:
            _og_flags = 0
        elif isinstance(_flags, type(re.X)):
            _og_flags = _flags
        elif isinstance(_flags, list):
            _og_flags = _flags[_idx] or 0
        else:
            raise Exception


        _new_flags = _og_flags | _cs_flags

        # go thru the list in every row of _compile_holder. put the flags in.
        for _inner_idx, _inner_thing in enumerate(_row):
            if _inner_thing is None:
                continue
            elif isinstance(_inner_thing, re.Pattern):
                _compile_holder[_idx][_inner_idx] = re.compile(
                    _inner_thing.pattern,
                    _inner_thing.flags | _new_flags
                )
            else:
                raise Exception(f"algorithm failure.")


    return _compile_holder





