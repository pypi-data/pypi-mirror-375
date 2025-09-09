# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    XContainer,
    CoreSepBreakType
)

import numbers
import re

from ._sep_or_line_break import _val_sep_or_line_break

from ...__shared._validation._1D_X import _val_1D_X
from ...__shared._validation._2D_X import _val_2D_X
from ...__shared._validation._any_bool import _val_any_bool
from ...__shared._validation._any_integer import _val_any_integer
from ...__shared._validation._any_string import _val_any_string



def _validation(
    _X: XContainer,
    _n_chars: int,
    _sep: CoreSepBreakType,
    _sep_flags: int | None,
    _line_break: CoreSepBreakType | None,
    _line_break_flags: int | None,
    _case_sensitive: bool,
    _backfill_sep: str,
    _join_2D: str
) -> None:
    """Validate data and parameters for TJ.

    This is a centralized hub for validation, the brunt of the work is
    handled by the individual modules. See the docs of the individual
    modules for more details.

    When `sep` (and `line_breaks`, if passed) are passed as literal
    strings, there is validation in place that is not in place for
    regular expressions. No `sep` can be a substring of another `sep`.
    No `sep` can be identical to a `line_break` entry and no sep can be
    a substring of a `line_break`. No `line_break` can be a substring of
    another `line_break`. No `line_break` can be identical to a `sep`
    entry and no `line_break` can be a substring of a `sep`.

    `line_break_flags` cannot be passed if `line_break` is not passed.


    Parameters
    ----------
    _X : XContainer
        The text to be justified. 2D containers can be ragged.
    _n_chars : int
        The number of characters per line to target when justifying the
        text.
    _sep : CoreSepBreakType
        STR
        str | Sequence[str] - the literal string character sequence(s)
        that indicate to TJ where it is allowed to wrap a line. Cannot
        be an empty string, cannot be an empty list-like.

        REGEX
        None | re.Pattern[str] | Sequence[re.Pattern[str]] - the
        re.compile object(s) that indicate to TJ where it is allowed
        to wrap a line. Cannot be a regex pattern that blatantly returns
        zero-span matches, cannot be an empty list-like.
    _sep_flags:
        int | None - the flags for the `sep` parameter.
    _line_break:
        STR
        None | str | Sequence[str] - the character string sequence(s)
        that indicate to TJ where it must force a new line. Can be None.
        Cannot be an empty string, cannot be an empty list-like.
        REGEX
        None | re.Pattern[str] | Sequence[re.Pattern[str]] - the
        re.compile object(s) that indicate to TJ where it must force a
        new line. Can be None. Cannot be a regex pattern that blatantly
        returns zero-span matches, cannot be an empty list-like.
    _line_break_flags : int | None
        The flags for the `line_break` parameter.
    _backfill_sep : str
        Some lines in the text may not have any of the given wrap
        separators or line breaks at the end of the line. When
        justifying text and there is a shortfall of characters in a
        line, TJ will look to the next line to backfill strings. In
        the case where the line being backfilled onto does not have a
        separator or line break at the end of the string, this character
        string will separate the otherwise separator-less string from
        the string being backfilled onto it.
    _join_2D : str
        Ignored if the data is given as a 1D sequence. For 2D containers
        of strings, this is the character string sequence that is used
        to join the strings across rows to convert the data to 1D for
        processing. The single string value is used to join for all rows.

    Return
    ------
    None

    Notes
    -----

    **Type Aliases**

    CoreSepBreakType:
        str | Sequence[str] | re.Pattern[str] | Sequence[re.Pattern[str]]]

    """


    # assess the contents of 'sep'. 'sep' must either be all literal
    # strings OR re.compile objects, they cannot be mixed. If
    # 'line_break' is passed, it must only be of the same type as
    # what is passed to 'sep'... that check is handled below by
    # _val_sep_or_line_break for line_break after '_mode' is set by the
    # contents of '_sep'.

    if isinstance(_sep, str):
        _mode = 'str'
    elif isinstance(_sep, re.Pattern):
        _mode = 'regex'
    else:
        err_msg = (f"'sep' must be composed of either ALL literal strings "
        f"or ALL re.compile objects, they cannot be mixed. \n'sep' must "
        f"be a single literal string or 1D vector of such, or a single "
        f"re.compile object or a 1D vector of such.")
        try:
            iter(_sep)
            if isinstance(_sep, dict):
                raise Exception
        except Exception as e:
            raise TypeError(err_msg)

        if all(map(isinstance, _sep, (str for _ in _sep))):
            _mode = 'str'
        elif all(map(isinstance, _sep, (re.Pattern for _ in _sep))):
            _mode = 'regex'
        else:
            raise TypeError(err_msg)

        del err_msg
    # END ASSESS CONTENTS OF sep #######################################
    ####################################################################

    # X & join_2D
    try:
        _val_2D_X(_X, _require_all_finite=True)
        # only check join_2D if _X is 2D, join_2D is ignored if data is 1D
        _val_any_string(_join_2D, 'join_2D', _can_be_None=False)
    except:
        try:
            _val_1D_X(_X, _require_all_finite=True)
        except:
            raise TypeError(
                f"TextJustifier expected a 1D sequence of strings or a "
                f"(possibly ragged) 2D array-like of strings. \nSee the "
                f"docs for clarification of accepted containers."
            )

    # n_chars
    if not isinstance(_n_chars, numbers.Integral):
        raise TypeError(f"'n_chars' must be an integer greater than zero.")

    # sep
    _val_sep_or_line_break(_sep, _name='sep', _mode=_mode)

    # sep_flags
    _val_any_integer(_sep_flags, 'sep_flags', _can_be_None=True)
    if not isinstance(_sep_flags, (type(None), numbers.Integral)):
        raise TypeError(f"'sep_flags' must be an integer or None.")

    # line_break
    _val_sep_or_line_break(_line_break, _name='line_break', _mode=_mode)

    # line_break_flags
    _val_any_integer(_line_break_flags, 'line_break_flags', _can_be_None=True)
    if not isinstance(_line_break_flags, (type(None), numbers.Integral)):
        raise TypeError(f"'line_break_flags' must be an integer or None.")

    if _line_break is None and _line_break_flags is not None:
        raise ValueError(
            f"cannot pass 'line_break_flags' when 'line_break' is not passed."
        )

    # case_sensitive
    _val_any_bool(_case_sensitive, 'case_sensitive', _can_be_None=False)

    # backfill_sep
    _val_any_string(_backfill_sep, 'backfill_sep', _can_be_None=False)

    # string-mode sep/line_break conflict
    if _mode == 'str':
        err_msg = (
            f"there is a conflict between strings for 'sep' and/or "
            f"'line_break'. "
            f"\nno 'sep' can be a substring of another 'sep'. "
            f"\nno 'line_break' can be a substring of another 'line_break'. "
            f"\nno 'sep' and 'line_break' character sequences can be "
            f"identical. "
            f"\nno 'sep' can be a substring of any 'line_break'. "
            f"\nno 'line_break' can be a substring of any 'sep'. "
        )

        if isinstance(_sep, str):
            set1 = {_sep, }
        else:
            set1 = set(_sep)

        if _line_break is None:
            set2 = set()
        elif isinstance(_line_break, str):
            set2 = {_line_break, }
        else:
            set2 = set(_line_break)

        _union = set1 | set2

        if len(_union) != len(set1) + len(set2):
            raise ValueError(err_msg)
        # we know there are no exact duplicates
        # now find if there are any shared substrings
        for s1 in _union:
            if any(s1 in s2 for s2 in _union if s2 != s1):
                raise ValueError(err_msg)

        del err_msg, set1, set2, _union







