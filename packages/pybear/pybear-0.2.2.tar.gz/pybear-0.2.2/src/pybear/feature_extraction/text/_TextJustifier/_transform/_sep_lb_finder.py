# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    SepWipType,
    LineBreakWipType
)

import re



def _sep_lb_finder(
    _X: list[str],
    _join_2D: str,
    _sep: SepWipType,
    _line_break: LineBreakWipType
) -> list[bool]:
    """Find rows that end with a `sep`.

    If any `sep` or `line_break` pattern matches coincidentally end with
    the `join_2D` character sequence, then find which rows end with a
    `sep` or a `line_break` pattern match. `X` will always be 1D.

    When justifying (which is always in 1D), if the line ended with a
    `sep` or `line_break` pattern match, then that stayed on the end of
    the last word. And if that `sep` or `line_break` coincidentally ends
    with the `join_2D` character string, then `TextSplitter` will leave
    a relic '' at the end of the corresponding rows. So for the case
    where a `sep` or `line_break` pattern match ends with `join_2D`,
    look at the end of each line and if ends with a `sep` or `line_break`
    pattern match then signify that in the outputted list. `backfill_sep`
    should never be at the end of a line.

    This module tries hard to only find rows where TJ itself put a
    `sep`/`line_break` on the end of line and causes a relic ''. It also
    tries hard NOT to touch other rows that don't end in `sep` or
    `line_break` but the user entry of `join_2D` caused the `join_2D`
    string to be at the end of a line (when `X` goes back to 2D the line
    will have '' and the end of it and the user did it to themself).
    This module also tries hard to use logic that honors the lack of
    validation between `sep` and line_break in TJ regex mode. Whereas
    string mode would preclude `sep` and `linebreak` from simultaneously
    ending a line (and perhaps the line also ends with `join_2D`),
    anything goes in regex mode. This module is intended to be identical
    for string and regex modes.

    Parameters
    ----------
    _X : list[str]
        The data that has been justified. Need to find places where
        `join_2D` may incidentally coincide with `sep` or `line_break`
        at the end of a line.
    _join_2D : str
        The character sequence that joined the tokens in each row of the
        data if the data was originally passed as 2D.
    _sep : SepWipType - the patterns where TJ may have wrapped a line.
    _line_break : LineBreakType
        The patterns where TJ forced a line break.

    Returns
    -------
    _MASK : list[bool]
        A 1D boolean list signifying which rows will end up with a relic
        '' in the last position by TJ's own handling of the 2D-to-1D-to-2D
        transitions.

    """


    assert isinstance(_X, list)
    assert isinstance(_join_2D, str)
    assert isinstance(_sep, (re.Pattern, tuple))
    assert isinstance(_line_break, (type(None), re.Pattern, tuple))

    # join_2D must be a str. the only way this module can be accessed is
    # if _was_2D in the main transform() is True, which means that X
    # was 2D, which means that join_2D was validated and it must be str.


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # condition 'sep' and 'line_break' to only look at the end of lines.
    # do this ahead of time or the for loop will constantly be rebuilding
    # the same $ sep & line_break patterns for each line in the data.

    def _endswith_helper(_sep: re.Pattern[str]) -> re.Pattern[str]:
        """Helper function for extracting patterns/flags and adding $."""
        return re.compile(f'{_sep.pattern}$', flags=_sep.flags)

    if isinstance(_sep, re.Pattern):
        _new_sep = _endswith_helper(_sep)
    elif isinstance(_sep, tuple):
        _new_sep = tuple(map(lambda x: _endswith_helper(x), _sep))
    else:
        raise Exception

    if _line_break is None:
        _new_line_break = None
    elif isinstance(_line_break, re.Pattern):
        _new_line_break = _endswith_helper(_line_break)
    elif isinstance(_line_break, tuple):
        _new_line_break = tuple(map(lambda x: _endswith_helper(x), _line_break))
    else:
        raise Exception

    del _endswith_helper
    # END condition 'sep' and 'line_break'
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


    _MASK = [False for _ in _X]


    def _match_helper(_sep: re.Pattern[str], _line: str) -> bool:
        """Helper function for finding pattern matches at the end of lines."""
        _match = re.search(_sep, _line)
        return _match is not None and _match.span()[0] != _match.span()[1]


    for _r_idx, _line in enumerate(_X):

        if re.search(f'{re.escape(_join_2D)}$', _line):

            _a =  isinstance(_new_sep, re.Pattern) and _match_helper(_new_sep, _line)

            _b = isinstance(_new_sep, tuple) \
                    and any(map(lambda x: _match_helper(x, _line), _new_sep))

            _c = isinstance(_new_line_break, re.Pattern) \
                 and _match_helper(_new_line_break, _line)

            _d = isinstance(_new_line_break, tuple) \
                    and any(map(lambda x: _match_helper(x, _line), _new_line_break))

            if _a or _b or _c or _d:
                _MASK[_r_idx] = True


    del _new_sep, _new_line_break, _match_helper


    return _MASK






