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



PatternType: TypeAlias = \
    None | str | re.Pattern[str] | tuple[str | re.Pattern[str], ...]
PatternHolderType: TypeAlias = \
    PatternType | list[PatternType]



def _val_pattern_holder(
    _pattern_holder:PatternHolderType,
    _n_rows:int,
    _name:str = 'unnamed patterns'
) -> None:
    """Validate 'pattern_holder'.

    Must be:
    None,
    a literal string,
    a regex pattern in a re.compile object,
    a tuple of literal strings and/or regex patterns in re.compile objects,
    or a list of Nones, literal strings, regex patterns in re.compile
    objects, and/or the tuples.

    Regex patterns are not validated here, any exception would be raised
    by the re method/function they are being passed to. If passed as a
    list, the number of entries must equal the number of rows in X.

    Parameters
    ----------
    _pattern_holder : PatternHolderType
        The literal strings or re.compile objects used to match patterns
        in the data. When None, no matches are sought. If a single
        literal or re.compile object, that is searched on the entire
        dataset. If a tuple of string literals and/or re.compile objects,
        then each of them is searched on the entire dataset. When passed
        as a list, the number of entries must equal the number of rows
        in the data, and the entries are applied to the corresponding
        row in the data. The list must be a sequence of Nones, string
        literals, re.compile objects and/or tuples of string literals /
        re.compile objects.
    _n_rows : int
        The number of rows in the data.

    Return
    ------
    None

    Notes
    -----

    **Type Aliases**

    PatternType:
        None | str | re.Pattern[str] | tuple[str | re.Pattern[str], ...]

    PatternHolderType:
        PatternType | list[PatternType]

    """


    assert isinstance(_n_rows, numbers.Integral)
    assert not isinstance(_n_rows, bool)
    assert _n_rows >= 0

    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def _val_helper(
        _core_pattern_holder: None | str | re.Pattern[str]
    ) -> bool:
        """
        Helper function to validate the core 'pattern_holder' objects
        are None | str | re.Pattern[str].
        """

        return isinstance(_core_pattern_holder, (type(None), str, re.Pattern))


    def _tuple_helper(
        _pattern_holder: tuple[str | re.Pattern[str]]
    ) -> bool:
        """
        Helper function for validating tuples.
        """

        return isinstance(_pattern_holder, tuple) \
            and all(map(_val_helper, _pattern_holder)) \
            and not any(map(lambda x: x is None, _pattern_holder))


    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    _err_msg = (
        f"'{_name}' must be None, a literal string, a regex pattern in a "
        f"re.compile object, \na tuple of literal strings and/or regex "
        f"patterns in re.compile objects, or a list of any of those "
        f"things. \nIf passed as a list, the number of entries must equal "
        f"the number of rows in the data."
    )

    if _val_helper(_pattern_holder):
        # means is None, str, or re.Pattern
        pass

    elif isinstance(_pattern_holder, tuple):

        if not _tuple_helper(_pattern_holder):
            raise TypeError(_err_msg)

    elif isinstance(_pattern_holder, list):

        if len(_pattern_holder) != _n_rows:
            raise ValueError(_err_msg)

        if not all(_val_helper(i) or _tuple_helper(i) for i in _pattern_holder):
            raise TypeError(_err_msg)

    else:
        raise TypeError(_err_msg)


    del _val_helper, _err_msg





