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



def _splitter(
    _X: list[str],
    _sep: SepWipType,
    _line_break: LineBreakWipType
) -> list[str]:
    """Split the text strings in `X` on all user-defined line break and
    wrap patterns.

    `_sep` and `_line_break` must have already been processed by
    :func:`_param_conditioner`, i.e., all literal strings must be
    converted to re.compile(s) and any flags passed as parameters or
    associated with `case_sensitive` must have been put in the compile(s).

    Split the text strings in `X` on all user-defined line break and
    wrap patterns, so that each line has no breaks or wraps, or if they
    do, the wraps/breaks are at the very end of the line. For each string
    in `X`, find the first split location, if any, and keep the left side
    of any split in the original row. Insert the right side of the split
    into the index slot immediately after. Then proceed to that next row
    and repeat the procedure until all lines in `X` are exhausted. In
    the event of a conflict, apply `sep`.

    Parameters
    ----------
    _X : list[str]
        The data to have individual rows split on line-break and wrap
        separator patterns defined by the user.
    _sep : SepWipType
        The regex pattern(s) that indicate to TJ where it is allowed to
        wrap a line.
    _line_break : LineBreakWipType
        The regex pattern(s) that indicate to TJ where it must force a
        new line.

    Returns
    -------
    _X : list[str]
        The data split into strings that are not divisible.

    """


    assert isinstance(_X, list)
    assert isinstance(_sep, (re.Pattern, tuple))
    assert isinstance(_line_break, (type(None), re.Pattern, tuple))


    def _match_dict_helper(_pattern: re.Pattern, _line:str) -> dict:
        """Helper function to search pattern and return match dictionary."""
        _match = re.search(_pattern, _line)
        if _match is not None and _match.span()[0] != _match.span()[1]:
            return {_match.start(): _match.group()}
        return {}


    # convert these to a tuple for easy iterating later
    if isinstance(_sep, re.Pattern):
        _sep = (_sep, )

    if isinstance(_line_break, re.Pattern):
        _line_break = (_line_break, )


    line_idx = 0
    while True:

        try:
            _line = _X[line_idx]
        except IndexError:
            break
        except Exception as e:
            raise e

        # go thru the seps & line_breaks and look for the first hit in
        # the string.
        _sep_dict = {}
        for _s in _sep:
            _sep_dict |= _match_dict_helper(_s, _line)

        _line_break_dict = {}
        if _line_break is not None:
            for _lb in _line_break:
                _line_break_dict |= _match_dict_helper(_lb, _line)

        hit_dict = _line_break_dict | _sep_dict
        del _sep_dict, _line_break_dict
        # if no hits, this is zero-len dict, there are no seps or line breaks
        # in that line
        if len(hit_dict) == 0:
            # rows that do not have seps/line_breaks will not be changed.
            # increment the line index, and back to the top
            line_idx += 1
            continue

        _lowest_idx = min(hit_dict)
        _first_lb_s = hit_dict[_lowest_idx]
        _adj_lowest_idx = _lowest_idx + len(_first_lb_s) - 1

        del _lowest_idx, _first_lb_s

        # if the hit is in the last position of the string do nothing
        if len(hit_dict) == 1 and _adj_lowest_idx == len(_line)-1:
            line_idx += 1
            continue

        # if there is a hit...
        # keep the left side in the current row
        # insert the right side in the next index after
        if _adj_lowest_idx >= len(_line) - 1:
            _left = _line
            _right = ''
        else:
            _left = _line[:_adj_lowest_idx + 1]
            _right = _line[_adj_lowest_idx + 1:]

        del _line
        _X[line_idx] = _left
        _X.insert(line_idx+1, _right)
        del _left, _right

        line_idx += 1
        continue


    del _match_dict_helper


    return _X








