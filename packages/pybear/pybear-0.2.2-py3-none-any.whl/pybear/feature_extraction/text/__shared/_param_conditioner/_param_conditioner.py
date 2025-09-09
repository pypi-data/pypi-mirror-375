# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    TypeAlias,
)

import re

from ._compile_maker import _compile_maker
from ._flag_maker import _flag_maker

from .._validation._compile_holder import _val_compile_holder



PatternType: TypeAlias = \
    None | str | re.Pattern[str] | tuple[str | re.Pattern[str], ...]
PatternHolderType: TypeAlias = \
    PatternType | list[PatternType]

WipPatternType: TypeAlias = \
    None | re.Pattern[str] | tuple[re.Pattern[str], ...]
WipPatternHolderType: TypeAlias = \
    WipPatternType | list[WipPatternType]

CaseSensitiveType: TypeAlias = bool | list[bool | None]

FlagType: TypeAlias = None | int
FlagsType: TypeAlias = FlagType | list[FlagType]



def _param_conditioner(
    _pattern_holder:PatternHolderType,
    _case_sensitive:CaseSensitiveType,
    _flags:FlagsType,
    _order_matters:bool,
    _n_rows:int,
    _name:str = 'unnamed pattern holder'
) -> WipPatternHolderType:
    """
    Use the parameters to convert all literal strings to re.compile and
    apply the flags implied by _case_sensitive and _flags.

    Parameters
    ----------
    _pattern_holder : PatternHolderType
        The string search criteria as passed by the user.
    _case_sensitive : CaseSensitiveType
        The case-sensitive strategy as passed by the user.
    _flags : FlagsType
        The flags for searches as passed by the user.
    _order_matters : bool
        When '_pattern_holder' is or has in it a tuple of literal
        strings and/or re.compiles, whether the order of operations and
        redundancy are important. If not important, any redundancy can
        be eliminated with Python sets and order can change without
        consequence.
    _n_rows : int
        The number of rows in the data. if _flags, _pattern_holder,
        and/or _case_sensitive were passed as a list, the length of them
        was already validated against this number.
    _name : str, default = 'unnamed pattern holder'
        The name of the corresponding pattern-holder param in the home
        module, like 'split', 'replace', 'ngrams', etc.

    Returns
    -------
    _compile_holder : WipPatternHolderType
        The search criteria for the data. Could be a single None, as
        single re.Pattern, a single tuple of re.Patterns, or a list
        comprised of any of those things.

    Notes
    -----

    **Type Aliases**

    PatternType:
        None | str | re.Pattern[str] | tuple[str | re.Pattern[str], ...]
    PatternHolderType:
        PatternType | list[PatternType]

    WipPatternType:
        None | re.Pattern[str] | tuple[re.Pattern[str], ...]
    WipPatternHolderType:
        WipPatternType | list[WipPatternType]

    CaseSensitiveType:
        bool | list[bool | None]

    FlagType:
        None | int
    FlagsType:
        FlagType | list[FlagType]

    """

    # dont need validation. these parameters come directly from the
    # instance parameters which are validated in _validation.

    # map the given params to re.Pattern objects if _pattern_holder is
    # not None. only return the output as a list if absolutely necessary.

    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
    # '_pattern_holder' must be None, str, re.compile, tuple or list
    # '_case_sensitive' must be bool, list[None or bool]
    # '_flags' must be None, int, or list[None or int]
    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

    if _pattern_holder is None:
        # from validation we know that '_flags' must be None and
        # '_case_sensitive' cannot be list. they dont matter. there is
        # nothing to remove, a no-op.
        return None

    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
    # '_pattern_holder' must be str, re.compile, tuple[str, compile] or list
    # '_case_sensitive' must be bool, list[None or bool]
    # '_flags' must be None, int, or list[None or int]
    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

    # convert '_pattern_holder' to list, if not already, holding only
    # None/compile.
    # in the process:
    #   convert any associated str into flagless re.compile (re.escape!)
    #   make everything inside the outer list be in a list (so None becomes
    #   [None], compile becomes [compile] and tuple becomes list.

    _compile_holder = _compile_maker(
        _pattern_holder, _order_matters, _n_rows, _name
    )

    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
    # '_compile_holder' must be list[list[None] | list[re.compile[str]]]
    # '_case_sensitive' must be bool, list[None or bool]
    # '_flags' must be None, int, or list[None or int]
    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

    # set the flags for the re.compile objects
    # '_flags' always trumps '_case_sensitive'. if user passed re.I in
    # any way (global or to individual rows) that trumps global
    # '_case_sensitive' == True. if '_case_sensitive' == False, everything
    # gets re.I.

    _compile_holder = _flag_maker(_compile_holder, _case_sensitive, _flags)

    # pull the inner objects out of their lists. if was tuple, turn
    # that back to a tuple
    for _idx, _row in enumerate(_compile_holder):

        if len(_compile_holder[_idx]) == 0:
            raise Exception('algorithm failure')
        elif len(_compile_holder[_idx]) == 1:
            _compile_holder[_idx] = _compile_holder[_idx][0]
        else:
            _compile_holder[_idx] = tuple(_compile_holder[_idx])

    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
    # '_compile_holder' must be list[None | compile[str] | tuple[compile, ...]]
    # '_case_sensitive' doesnt matter anymore
    # '_flags' doesnt matter anymore
    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^


    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    # look to see if _compile_holder is unnecessarily iterable, meaning
    # all the values in _compile_holder are identical
    # do it twice for something like [(x,), (x,)....]
    # _compile_holder cannot have any str
    if hasattr(_compile_holder, '__len__') and len(_compile_holder) \
            and all(map(lambda x: x == _compile_holder[0], _compile_holder)):
        _compile_holder = _compile_holder[0]

    if hasattr(_compile_holder, '__len__') and len(_compile_holder) \
            and all(map(lambda x: x == _compile_holder[0], _compile_holder)):
        _compile_holder = _compile_holder[0]


    # this is validation for an internally built WIP object.
    # technically this is just training wheels. and perhaps could come out
    # once this module is proved to be reliable.
    _val_compile_holder(_compile_holder, _n_rows, _name)


    return _compile_holder




