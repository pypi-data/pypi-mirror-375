# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    SepWipType,
    LineBreakWipType
)

import numbers
import re

from ._splitter import _splitter
from ._stacker import _stacker



def _transform(
    _X: list[str],
    _n_chars: int,
    _sep: SepWipType,
    _line_break: LineBreakWipType,
    _backfill_sep: str
) -> list[str]:
    """Fit text as strings to the user-specified number of characters per
    row.

    For this module, the data must be a 1D Python list of strings.

    `_sep` and `_line_break` must have already been processed
    by :func:`_param_conditioner`, i.e., all literal strings must be
    converted to re.compile and any flags passed as parameters or
    associated with `case_sensitive` must have been put in the compile(s).

    Parameters
    ----------
    _X : list[str]
        The text to justify as a 1D Python list of strings.
    _n_chars : int
        The number of characters per line to target when justifying the
        text.
    _sep : SepWipType
        The regex pattern(s) that indicate to TJ where it is allowed to
        wrap a line.
    _line_break : LineBreakWipType
        The regex pattern(s) that indicate to TJ where it must force a
        new line.
    _backfill_sep : str
        Some lines in the text may not have any of the given wrap
        separators or line breaks at the end of the line. When justifying
        text and there is a shortfall of characters in a line, TJ will
        look to the next line to backfill strings. In the case where the
        line being backfilled onto does not have a separator or line
        break at the end of the string, this character string will
        separate the otherwise separator-less string from the string
        being backfilled onto it.

    Return
    ------
    _X : list[str]
        The justified text in a Python list of strings.

    """


    assert isinstance(_X, list)
    assert isinstance(_n_chars, numbers.Integral)
    assert isinstance(_sep, (re.Pattern, tuple))
    assert isinstance(_line_break, (type(None), re.Pattern, tuple))
    assert isinstance(_backfill_sep, str)


    # loop over the entire data set and split on anything that is a line_break
    # or sep. these user-defined line seps/breaks will end up in an '$'
    # position on impacted lines.
    # e.g. if X is ['jibberish', 'split this, on a comma.', 'jibberish']
    # then the returned list will be:
    # ['jibberish', 'split this,', 'on a comma.', 'jibberish'] and the
    # comma at the end of 'split this,' is easily recognized with $.
    _X:list[str] = _splitter(_X, _sep, _line_break)


    # we now have a 1D list (still) that has any rows with seps/breaks
    # broken out into indivisible strings on each row.

    # now we need to restack these indivisible units to fill the n_char
    # requirement.
    _X:list[str] = _stacker(_X, _n_chars, _sep, _line_break, _backfill_sep)


    return _X




