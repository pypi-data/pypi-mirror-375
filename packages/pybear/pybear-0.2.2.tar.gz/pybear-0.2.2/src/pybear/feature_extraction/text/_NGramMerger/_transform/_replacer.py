# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Callable,
    Sequence
)

import re



def _replacer(
    _line: list[str],
    _ngram: tuple[re.Pattern[str], ...],
    _hits: Sequence[int],
    _ngcallable: Callable[[list[str]], str] | None,
    _sep: str | None
) -> list[str]:
    """Using the pattern match indices found by :func:`_match_finder`,
    at those indices in `_line` replace the words with the contiguous
    string mapped from the words.

    Merge ngrams that match ngram patterns using the following hierarchy:

    by the given callable

    by the given separator

    by the default separator

    Parameters
    ----------
    _line : list[str]
        A single 1D sequence of strings.
    _ngram : tuple[re.Pattern[str], ...]
        A single n-gram sequence containing re.compile objects that
        specify an n-gram pattern. Cannot have less than 2 entries.
    _hits : Sequence[int]
        The starting indices of sequences in `_line` that match the
        n-gram pattern.
    _ngcallable : Callable[[list[str]], str] | None
        The callable applied to sequences that match an n-gram pattern
        to produce a single contiguous string.
    _sep : str | None
        The user defined separator to join the words with. If no
        separator is defined by the user, use the default separator.

    Returns
    -------
    _line : list[str]
        The sequence of strings with all matching n-gram patterns
        replaced with contiguous strings.

    """


    if len(_hits) == 0:
        return _line

    _n_len = len(_ngram)

    _sep = _sep or '_'

    if _ngcallable is None:
        _ngcallable = lambda _block: _sep.join(_block)


    for _idx in list(reversed(sorted(list(_hits)))):

        _block = _line[_idx: _idx + _n_len]

        del _line[_idx: _idx + _n_len]
        _str = _ngcallable(_block)
        if not isinstance(_str, str):
            raise TypeError(f"'ngcallable' must return a single string")
        _line.insert(_idx, _str)


    return _line





