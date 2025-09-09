# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Callable,
    TypeAlias
)
from .._type_aliases import (
    ReplaceType,
    WipReplaceType,
    CaseSensitiveType,
    FlagsType
)

import numbers
import re

from .._validation._replace import _val_replace

from ...__shared._param_conditioner._flag_maker import _flag_maker


ModFindType: TypeAlias = list[list[re.Pattern[str] | None]]
ModReplaceType: TypeAlias = list[list[str | Callable]]



def _special_param_conditioner(
    _replace: ReplaceType,
    _case_sensitive: CaseSensitiveType,
    _flags: FlagsType,
    _n_rows: int,
) -> WipReplaceType:
    """Standardize the `replace` parameter with (escaped!) re.compiles
    in every 'find' position and global flags applied.

    Do not condense any duplicate find/replace pairs that may be in a
    tuple of pairs because the user may have actually wanted to run the
    same pair several times. This means we cannot use most of the
    param_conditioning modules to handle this, which will blindly
    condense any group of equal objects, but we can use the `_flag_maker`
    module. Need to get the pattern portion of `replace` into the format
    for that module. So we will extract both the 'find' and 'replace'
    parts of the Replacer tuples, package 'find' so it can go into
    `_flag_maker`, and package 'replace' in the same way to that it is
    easy to stitch them back together into the original format of the
    'replacer' param.

    Parameters
    ----------
    _replace : ReplaceType - the 'replace' parameter as passed at init.
    _case_sensitive : CaseSensitiveType
        The 'case_sensitive' parameter as passed at init.
    _flags : FlagsType
        The 'flags' parameter as passed at init.
    _n_rows : int
        The number of rows in the data passed to :meth:`transform`.

    Returns
    -------
    _replace : WipReplaceType
        The original 'replace' parameter with all literals converted to
        re.compile and any flags also put into the re.compiles.

    Notes
    -----

    **Type Aliases**

    ReplaceType:
        ReplaceSubType | list[ReplaceSubType]

    WipReplaceType:
        WipReplaceSubType | list[WipReplaceSubType]

    CaseSensitiveType:
        bool | list[bool | None]

    FlagsType:
        FlagType | list[FlagType]

    """


    # validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    assert isinstance(_case_sensitive, (bool, list))
    if isinstance(_case_sensitive, list):
        assert all(map(
            isinstance,
            _case_sensitive,
            ((type(None), bool) for _ in _case_sensitive)
        ))
    assert isinstance(_flags, (type(None), numbers.Integral, list))
    if isinstance(_flags, list):
        assert all(map(
            isinstance,
            _flags,
            ((type(None), numbers.Integral) for _ in _flags)
        ))
    assert isinstance(_n_rows, numbers.Integral) and \
           not isinstance(_n_rows, bool) and _n_rows >= 0

    # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # only condense a LIST with all the same thing. do not condense any
    # tuples. it might condense repeated replaces that the user actually
    # wants to run multiple times (like ('  ', ' ')).
    if isinstance(_replace, list) and len(_replace) \
            and all(map(lambda x: x == _replace[0], _replace)):
        _replace = _replace[0]


    # do not use _param_conditioner! that will condense repeated
    # patterns in a tuple, when the user actually wants to run the same
    # replace multiple times. but _flag_maker is OK. so pull all the
    # 'find' parts of the tuples, do re.compile(re.escape(find)), put
    # them in a special container that _flag_maker likes, and run it
    # thru _flag_maker. also make an equally sized special container
    # for the replace values. after all finds are converted to re.compile
    # and flags are put in, merge the two lists back together


    # pull apart _replace -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # need to get the find parts to be in ModFindType, a list of len _n_rows.
    # make an equally shaped container for replace

    if _replace is None:
        _mod_find = [[None] for _ in range(_n_rows)]
        _mod_replace = [[None] for _ in range(_n_rows)]
    elif isinstance(_replace, tuple):
        if all(map(isinstance, _replace, (tuple for _ in _replace))):
            # tuple of pairs
            _patterns = []
            _replaces = []
            for _tuple in _replace:
                if isinstance(_tuple[0], str):
                    _patterns.append(re.compile(re.escape(_tuple[0])))
                elif isinstance(_tuple[0], re.Pattern):
                    _patterns.append(_tuple[0])
                else:
                    raise Exception
                _replaces.append(_tuple[1])
            _mod_find = [_patterns for _ in range(_n_rows)]
            _mod_replace = [_replaces for _ in range(_n_rows)]
            del _patterns, _replaces
        else:
            # just one pair
            if isinstance(_replace[0], str):
                _pattern = re.compile(re.escape(_replace[0]))
            elif isinstance(_replace[0], re.Pattern):
                _pattern = _replace[0]
            else:
                raise Exception
            _mod_find = [[_pattern] for _ in range(_n_rows)]
            _mod_replace = [[_replace[1]] for _ in range(_n_rows)]
            del _pattern
    elif isinstance(_replace, list):

        if len(_replace) != _n_rows:
            raise ValueError(f"'len(replace) != len(X)")

        _mod_find = []
        _mod_replace = []
        for _row_idx, _row_replace in enumerate(_replace):
            if _row_replace is None:
                _mod_find.append([None])
                _mod_replace.append([None])
            elif isinstance(_row_replace, tuple):
                if all(map(isinstance, _row_replace, (tuple for _ in _row_replace))):
                    # tuple of pairs
                    _patterns = []
                    _replaces = []
                    for _tuple in _row_replace:
                        if isinstance(_tuple[0], str):
                            _patterns.append(re.compile(re.escape(_tuple[0])))
                        elif isinstance(_tuple[0], re.Pattern):
                            _patterns.append(_tuple[0])
                        else:
                            raise Exception
                        _replaces.append(_tuple[1])
                    _mod_find.append(_patterns)
                    _mod_replace.append(_replaces)
                    del _patterns, _replaces
                else:
                    # just one pair
                    if isinstance(_row_replace[0], str):
                        _pattern = re.compile(re.escape(_row_replace[0]))
                    elif isinstance(_row_replace[0], re.Pattern):
                        _pattern = _row_replace[0]
                    else:
                        raise Exception
                    _mod_find.append([_pattern])
                    _mod_replace.append([_row_replace[1]])
                    del _pattern
            else:
                raise TypeError(
                    f"unexpected type in 'replace' list: {type(_row_replace)}"
                )
    else:
        raise TypeError(f"unexpected type {type(_replace)}")

    del _replace

    # END pull apart _replace -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # run the list of compiled search patterns thru flag maker to get any
    # flags set by 'case_sensitive' and 'flags'
    _mod_find: ModFindType = _flag_maker(
        _mod_find,
        _case_sensitive,
        _flags
    )

    # put the re.compiles back into the original params -- -- -- -- -- --

    # _mod_find should be list[list[None] | list[re.Pattern[str]]]
    assert isinstance(_mod_find, list)
    assert all(map(isinstance, _mod_find, (list for _ in _mod_find)))

    # _mod_replace should be list[list[None], list[str]]
    assert isinstance(_mod_replace, list)
    assert all(map(isinstance, _mod_replace, (list for _ in _mod_replace)))


    # stitch the lists of patterns and replacements back together
    # just write over the original 'replace'
    _replace = []
    for _row_idx, (_patterns, _replaces) in enumerate(zip(_mod_find, _mod_replace)):

        assert len(_patterns) == len(_replaces)

        if _patterns[0] is None:
            assert _replaces[0] is None
            _replace.append(None)
        # otherwise must be [tuple(Pattern, str), ...]
        elif isinstance(_patterns, list) and len(_patterns) == 1:
            assert isinstance(_patterns[0], re.Pattern)
            assert isinstance(_replaces[0], (str, Callable))
            _replace.append((_patterns[0], _replaces[0]))
        elif isinstance(_patterns, list): # and len(_patterns) > 1:
            # this must be a tuple of pairs
            _new_tuple = []
            for _idx in range(len(_patterns)):
                assert isinstance(_patterns[_idx], re.Pattern)
                assert isinstance(_replaces[_idx], (str, Callable))
                _new_tuple.append((_patterns[_idx], _replaces[_idx]))
            _replace.append(tuple(_new_tuple))
            del _new_tuple
        else:
            raise TypeError(f"unexpected type {type(_patterns)} in new_find")

    del _mod_find, _mod_replace

    # END put the re.compiles back into the original params -- -- -- -- --


    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    # remember we had to blow out _replace into 2 lists in order to pass
    # the 'find' part to _flag_maker, then put back together as a list.
    # if that list can be condensed, do that now.
    # something that was originally not a list may not be condensible
    # because there may have been varying row-wise flags.
    if len(_replace) and all(map(lambda x: x == _replace[0], _replace)):
        _replace = _replace[0]
    # # END condenser -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # _replace should be back in a place where it passes validation for
    # the OG 'replace' param
    # this is validation for an internally built WIP object.
    # technically this is just training wheels. and perhaps could come out
    # once this module is proved to be reliable.
    _val_replace(_replace, _n_rows)


    return _replace





