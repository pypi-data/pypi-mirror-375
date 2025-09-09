# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Sequence

import math
import numbers

from .....base._check_1D_str_sequence import check_1D_str_sequence



def view_text_snippet(
    _VECTOR:Sequence[str],
    _idx:int,
    _span:int = 9
) -> str:
    """Highlights the word of interest (which is given by the 'idx' value)
    in a series of words.

    For example, in a simple case that avoids edge effects, a span of 9
    would show 4 strings to the left of the target string in lower-case,
    the target string itself capitalized, then the 4 strings to the right
    of the target string in lower-case.

    Parameters
    ----------
    _VECTOR : Sequence[str]
        The sequence of strings that provides a subsequence of strings
        to highlight. Cannot be empty.
    _idx : int
        The index of the string in the sequence of strings to highlight.
    _span : int, default = 9
        The number of strings in the sequence of strings to select when
        highlighting one particular central string.

    Returns
    -------
    str:
        The highlighted portion of the string sequence.

    """

    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    check_1D_str_sequence(_VECTOR)
    if len(_VECTOR) == 0:
        raise ValueError(f"'VECTOR' cannot be empty")


    # idx -- -- -- -- -- -- -- -- -- --
    err_msg = f"'idx' must be a non-negative integer in range of the given vector"
    if not isinstance(_idx, numbers.Integral):
        raise TypeError(err_msg)
    if isinstance(_idx, bool):
        raise TypeError(err_msg)
    if _idx not in range(0, len(_VECTOR)):
        raise ValueError(err_msg)
    del err_msg
    # END idx -- -- -- -- -- -- -- -- --

    # span -- -- -- -- -- -- -- -- -- --
    err_msg = f"'span' must be an integer >= 3"
    if not isinstance(_span, numbers.Integral):
        raise TypeError(err_msg)
    if isinstance(_span, bool):
        raise TypeError(err_msg)
    if _span < 3:
        raise ValueError(err_msg)
    del err_msg
    # END span -- -- -- -- -- -- -- -- --

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    _lower = math.floor(_idx - (_span - 1) / 2)
    _upper = math.ceil(_idx + (_span - 1) / 2)
    if _lower <= 0:
        _min, _max = 0, min(_span, len(_VECTOR))
    elif _upper >= len(_VECTOR):
        _min, _max = max(0, len(_VECTOR) - _span), len(_VECTOR)
    else:
        _min, _max = _lower, _upper + 1
    del _lower, _upper

    SNIPPET = []
    for word_idx in range(_min, _max):
        if word_idx == _idx:
            SNIPPET.append(_VECTOR[word_idx].upper())
        else:  # word_idx is not on the target word...
            SNIPPET.append(_VECTOR[word_idx].lower())


    return " ".join(SNIPPET)  # RETURNS AS STRING




