# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Sequence

import numbers

import numpy as np


def _get_wrap_match_idxs(
    _first_line: Sequence[str],
    _start_idx: int,
    _end_idx: int,
    _wrap_match_idx: Sequence[int],
    _n_len: int
) -> tuple[list[int], list[int]]:
    """Create 2 separate lists of indices.

    Can only access this module if there was a match in the wrap region.
    The first list contains the indices in the ORIGINAL first line where
    the pattern match partially overlays. The second list contain the
    indices in the ORIGINAL second line where the match partially
    overlays. Need to know these things to mutate the original lines.

    Parameters
    ----------
    _first_line : Sequence[str]
        The active line in transform that is being searched for n-grams.
    _start_idx : int
        The index in the first line where the wrap region started. Python
        range rules apply.
    _end_idx : int
        The index in the second line where the wrap region ended. Python
        range rules apply.
    _wrap_match_idx : Sequence[int]
        The index in the wrap region object where an n-gram pattern match
        started. cannot be empty if this module is accessed.
    _n_len : int
        The length of the n-gram pattern that is currently being searched
        for in transform.

    Returns
    -------
    indices : tuple[list[int], list[int]]
        The indices in the original first line and original second line
        where the pattern match overlays.

    """


    # validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    assert isinstance(_first_line, Sequence)
    assert all(map(isinstance, _first_line, (str for _ in _first_line)))

    assert isinstance(_start_idx, numbers.Integral)
    # start_idx cant be outside of first_line, if it was, we would have
    # short circuited out of _wrap_manager and returned the original lines
    assert _start_idx < len(_first_line)

    assert isinstance(_end_idx, numbers.Integral)
    # start_idx cant be 0,, if it was, we would have
    # short circuited out of _wrap_manager and returned the original lines
    assert _end_idx > 0

    assert isinstance(_wrap_match_idx, Sequence)
    # to get into this module there must have been a match, len == 1
    assert len(_wrap_match_idx) == 1
    assert all(map(
        isinstance,
        _wrap_match_idx,
        (numbers.Integral for _ in _wrap_match_idx)
    ))
    assert all(map(lambda x: x >= 0, _wrap_match_idx))

    assert isinstance(_n_len, numbers.Integral)
    assert _n_len > 0
    # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # if we get into this module then there is a merge in the wrap region

    # create a list of the indices in the original objects that comprised
    # the actual wrap region
    _og_idxs = list(range(len(_first_line)))[_start_idx:]
    _og_idxs += list(range(_end_idx))
    # get all the indices in the wrap region that are part of the ngram match
    _n_gram_range = [_wrap_match_idx[0] + i for i in range(_n_len)]
    # overlay these indices on the og idxs that were in the wrap region
    # to get the idxs in the original lines that are part of the ngram match
    _merged_idxs = np.array(_og_idxs)[_n_gram_range].tolist()
    del _og_idxs, _n_gram_range

    # idx zero from the second line must be in _merged_idxs
    # split these based on their home line
    # each lines indices must be contiguous within each subset of indices
    _first_line_idxs = []
    _second_line_idxs = []
    _goes_in_first_line = False
    # we need to traverse these indices so that we know that the first
    # zero we hit is definitely associated with the second line
    for x in reversed(_merged_idxs):
        # this is flipped so we are going thru second line idxs first
        if _goes_in_first_line:
            _first_line_idxs.append(x)
        else:
            _second_line_idxs.append(x)
        if (x == 0):
            _goes_in_first_line = True

    del x, _merged_idxs, _goes_in_first_line


    return sorted(_first_line_idxs), sorted(_second_line_idxs)





