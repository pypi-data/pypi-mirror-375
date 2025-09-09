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
import numbers

from ._match_finder import _match_finder
from ._replacer import _replacer
from ._manage_wrap_idxs import _manage_wrap_idxs
from ._get_wrap_match_idxs import _get_wrap_match_idxs

from .._validation._ngcallable import _val_ngcallable

from ...__shared._validation._any_string import _val_any_string



def _wrap_manager(
    _first_line: list[str],
    _second_line: list[str],
    _first_hits: Sequence[int],
    _second_hits: Sequence[int],
    _ngram: tuple[re.Pattern[str], ...],
    _ngcallable: Callable[[list[str]], str] | None,
    _sep: str | None
) -> tuple[list[str], list[str]]:
    """Define a wrap region and look in it for any n-gram matches.

    Only if the user has indicated to look for n-grams around the ends
    and beginnings of lines. If there are any matches, make the changes
    to the 2 impacted lines and return them.

    Parameters
    ----------
    _first_line : list[str]
        The current line being searched for ngram patterns
        in :meth:`transform`.
    _second_line : list[str]
        The line below the current line being searched for ngram patterns
        in `transform`.
    _first_hits : Sequence[int]
        The first indices of any matching n-gram patterns found in the
        current line during the normal linear n-gram search.
    _second_hits : Sequence[int]
        The first indices of any matching n-gram patterns found in the
        line below the current line during the normal linear n-gram
        search.
    _ngram : tuple[re.Pattern[str], ...]
        A single n-gram sequence containing re.compile objects that
        specify an n-gram pattern. Cannot have less than 2 entries.
    _ngcallable : Callable[[list[str]], str] | None
        The callable applied to sequences that match an n-gram pattern
        to produce a single contiguous string.
    _sep : str | None
        The user defined separator to join the words with, if
        `_ngcallable` is not given. If no separator is defined by the
        user, use the default separator.

    Returns
    -------
    lines : tuple[list[str], list[str]]
        The current line and the line below it with any wrap-region
        ngrams joined into a contiguous string in the current line.

    """


    # validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    assert isinstance(_first_line, Sequence)
    assert all(map(isinstance, _first_line, (str for _ in _first_line)))

    assert isinstance(_second_line, Sequence)
    assert all(map(isinstance, _second_line, (str for _ in _second_line)))

    assert isinstance(_first_hits, Sequence)
    assert all(map(
        isinstance,
        _first_hits,
        (numbers.Integral for _ in _first_hits)
    ))
    assert all(map(lambda x: x >= 0, _first_hits))

    assert isinstance(_second_hits, Sequence)
    assert all(map(
        isinstance,
        _second_hits,
        (numbers.Integral for _ in _second_hits)
    ))
    assert all(map(lambda x: x >= 0, _second_hits))

    assert all(map(isinstance, _ngram, ((str, re.Pattern) for _ in _ngram)))

    _val_ngcallable(_ngcallable)
    _val_any_string(_sep, 'sep', _can_be_None=True)
    # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # if wrap is True wrap region is
    # first_line[-len(ngram)+1:]
    # to second_line[:len(ngram)-1]
    # if there are any hits in wrap region on the first
    # line or second line dont include in the wrap area search

    _n_len = len(_ngram)

    # get the maximum index in the first line that was found to be part
    # of a normal linear ngram merge, then send the part after that to
    # the wrap part
    # find the lowest hit in the second line, then send the part before
    # that to the wrap part
    _start_idx, _end_idx = _manage_wrap_idxs(
        _first_line,
        _first_hits,
        _second_hits,
        _n_len
    )

    # short circuit out if either side doesnt have a valid wrap region
    if _start_idx >= len(_first_line) or _end_idx == 0:
        return _first_line, _second_line

    # _WRAPPED is the possibly truncated wrap region
    _WRAPPED = _first_line[_start_idx:]
    _WRAPPED += _second_line[:_end_idx]

    # send the wrap region to the match finder, it will return a list.
    # if there is a match it will have the starting position, otherwise
    # empty there should only be one number at most
    _wrap_match_idx = _match_finder(_WRAPPED, _ngram)

    # short circuit out if there is no ngram pattern match
    if len(_wrap_match_idx) == 0:
        return _first_line, _second_line

    if len(_wrap_match_idx) > 0:
        # then there is a merge in the wrap region
        # create a list for first_line and another for second_line
        # find where the wrap region ngram match overlays with the
        # the original lines and put the overlaid indices in their
        # respective buckets.
        _first_line_idxs, _second_line_idxs = \
            _get_wrap_match_idxs(
                _first_line,
                _start_idx,
                _end_idx,
                _wrap_match_idx,
                _n_len
            )

        # remove the words that match the ngram pattern across the wrap
        # we know all the matches in the second line must be contiguous
        # from idx 0
        for _ in _second_line_idxs:
            _second_line.pop(0)
        # do this backwards
        for x in reversed(sorted(_first_line_idxs)):
            _first_line.pop(x)

        # find out what the merged word was
        _merged_word = _replacer(
            _WRAPPED,
            _ngram,
            _wrap_match_idx,
            _ngcallable,
            _sep
        )[_wrap_match_idx[0]]

        # and put it into the first list
        _first_line.insert(_first_line_idxs[0], _merged_word)

        del _merged_word, _first_line_idxs, _second_line_idxs


    return _first_line, _second_line





