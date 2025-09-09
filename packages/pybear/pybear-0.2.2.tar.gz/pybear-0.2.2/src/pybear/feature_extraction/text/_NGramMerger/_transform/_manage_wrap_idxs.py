# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Sequence

import numbers



def _manage_wrap_idxs(
    _first_line: Sequence[str],
    _first_hits: Sequence[int],
    _second_hits: Sequence[int],
    _n_len: int
) -> tuple[int, int]:
    """Determine which part of the end of the first line and which part
    of the start of the second line can be used to do a wrap-region
    search for n-grams.

    For both lines, the wrap region cannot include any indices that are
    part of another ngram previously found in the normal linear search
    for ngram patterns.

    Parameters
    ----------
    _first_line : Sequence[str]
        The active line in transform that is being searched for n-grams.
    _first_hits : Sequence[int]
        The first indices of n-gram patterns that were found during the
        normal linear search of first_line.
    _second_hits : Sequence[int]
        The first indices of n-gram patterns that were found during the
        normal linear search of the line in the data that is after
        first_line.
    _n_len : int
        The length of the n-gram pattern that is currently being searched
        for in transform.

    Returns
    -------
    indices : tuple[int, int]
        The index in the first line that starts the wrap region and the
        index in second line that marks the end of the wrap region.
        Python range rules apply.

    """


    # validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    assert isinstance(_first_line, Sequence)
    assert all(map(isinstance, _first_line, (str for _ in _first_line)))

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

    assert isinstance(_n_len, numbers.Integral)
    assert _n_len > 0
    # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # map the first line hits from the start idx of the matching pattern
    # to last idx of the matching pattern and get the maximum index that
    # will be part of a normal linear n-gram merge.
    if len(_first_hits) > 0:
        _max_end_idx = max([i + _n_len - 1 for i in _first_hits])
    else:
        _max_end_idx = len(_first_line) - _n_len
    # increment the max end index to get the start index
    # in the first line for the wrap region
    _start_idx = _max_end_idx + 1
    # truncate _start_idx if needed
    _start_idx = max(_start_idx, len(_first_line) - _n_len + 1)
    # END -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # find the lowest index of a pattern match in the second line
    if len(_second_hits) > 0:
        _end_idx = min(_second_hits)
    else:
        _end_idx = _n_len - 1
    # truncate _end_idx if needed
    _end_idx = min(_end_idx, _n_len - 1)
    # END -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --



    return _start_idx, _end_idx



