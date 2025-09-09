# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    TypeAlias
)

import numbers
import re
from copy import deepcopy



FindType: TypeAlias = str | re.Pattern[str]
PatternType: TypeAlias = FindType | tuple[FindType, ...]



def _compile_maker(
    _pattern_holder: PatternType | list[PatternType | None],
    _order_matters: bool,
    _n_rows: int,
    _name:str = 'unnamed pattern holder'
) -> list[list[None] | list[re.Pattern[str]]]:
    """
    Convert any string literals to re.compile and map '_pattern_holder'
    to a list. Do not forget to escape string literals!

    Parameters
    ----------
    _pattern_holder : PatternType | list[PatternType | None]
        The search criteria as passed by the user.
    _order_matters : bool
        When '_pattern_holder' is or has in it a tuple of literal strings
        and/or re.compiles, whether the order of operations and
        redundancy are important. If not important, any redundancy can
        be eliminated with Python sets and order can change without
        consequence.
    _n_rows : int - the number of rows in whatever data is associated
        with '_pattern_holder'.
    _name : str, default = 'unnamed pattern holder'
        The name of the corresponding pattern-holder param in the home
        module, like 'split', 'replace', 'ngrams', etc.

    Returns
    -------
    _compile_holder : list[list[None] | list[re.Pattern[str]]]
        The search criteria mapped to [None] or [re.Pattern[str], ...]
        for every row in whatever data '_pattern_holder' is associated
        with.

    Notes
    -----

    **Type Aliases**

    FindType:
        str | re.Pattern[str]
    PatternType:
        FindType | tuple[FindType, ...]

    """


    # validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    assert isinstance(_order_matters, bool)

    assert isinstance(_n_rows, numbers.Integral)
    assert _n_rows >= 0

    assert isinstance(_name, str)

    if _pattern_holder is None:
        raise TypeError(f"'{_name}' is None, should have been handled elsewhere")

    if isinstance(_pattern_holder, list) and len(_pattern_holder) != _n_rows:
        raise ValueError(f"validation failure: len(list({_name})) != _n_rows")

    # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    if isinstance(_pattern_holder, str):
        _compile_holder = \
            [[re.compile(re.escape(_pattern_holder))] for _ in range(_n_rows)]
    elif isinstance(_pattern_holder, re.Pattern):
        _compile_holder = [[_pattern_holder] for _ in range(_n_rows)]
    elif isinstance(_pattern_holder, tuple):
        # str becomes re.compile, re.compile stays re.compile, cant be None
        _compile_holder = [
            re.compile(re.escape(i)) if isinstance(i, str)
                else i for i in _pattern_holder
        ]
        if _order_matters:
            _compile_holder = [_compile_holder for j in range(_n_rows)]
        else:
            # ensure no duplicates
            _compile_holder = [list(set(_compile_holder)) for j in range(_n_rows)]
    elif isinstance(_pattern_holder, list):

        _compile_holder = deepcopy(_pattern_holder)

        for _idx, k in enumerate(_pattern_holder):  # len is _n_rows by definition
            if k is None:
                _compile_holder[_idx] = [None]
            elif isinstance(k, str):
                _compile_holder[_idx] = [re.compile(re.escape(k))]
            elif isinstance(k, re.Pattern):
                _compile_holder[_idx] = [k]
            elif isinstance(k, tuple):
                # str becomes re.compile, re.compile unchanged, cant be None
                n = [
                    re.compile(re.escape(m)) if isinstance(m, str)
                        else m for m in k
                ]
                if _order_matters:
                    _compile_holder[_idx] = n
                else:
                    # ensure no duplicates
                    _compile_holder[_idx] = list(set(n))
                del n
            else:
                raise Exception(f"validation failure. {type(k)} in '{_name}'.")
    else:
        raise Exception(f"validation failure. '{_name}' is {type(_pattern_holder)}.")


    return _compile_holder







