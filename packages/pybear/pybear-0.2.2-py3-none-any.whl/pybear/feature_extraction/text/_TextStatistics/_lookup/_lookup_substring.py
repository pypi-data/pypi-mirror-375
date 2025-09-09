# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
)

import re

import numpy as np



def _lookup_substring(
    _pattern:str | re.Pattern[str],
    _uniques:Sequence[str],
    _case_sensitive:bool = True
) -> list[str]:
    """Use string literals or regular expressions to look for substring
    matches in the fitted words.

    `pattern` can be a literal string or a regular expression in a
    re.compile object.

    If re.compile object is passed, `case_sensitive` is ignored and the
    fitted words are searched with the compile object as given. If string
    is passed and `case_sensitive` is True, search for an exact substring
    match of the passed string; if `case_sensitive` is False, search
    without regard to case.

    If a substring match is not found, return an empty list. If matches
    are found, return a 1D list of the matches in their original form
    from the fitted data.

    This is only available if parameter `store_uniques` in the main
    `TextStatistics` module is True. If False, the unique strings that
    have been fitted on the `TextStatistics` instance are not retained
    therefore cannot be searched, and an empty list is always returned.

    Parameters
    ----------
    _pattern : str | re.Pattern[str]
        Character sequence or regular expression in a re.compile object
        to be looked up against the strings fitted on the `TextStatistics`
        instance.
    _uniques : Sequence[str]
        The unique strings found by the `TextStatistics` instance during
        fitting.
    _case_sensitive : bool, default = True
        Ignored if an re.compile object is passed to `pattern`. If True,
        search for the exact pattern in the fitted data. If False, ignore
        the case of words in uniques while performing the search.

    Returns
    -------
    list[str]:
        List of all strings in the fitted data that contain the given
        character substring. Returns an empty list if there are no
        matches.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    if not isinstance(_pattern, (str, re.Pattern)):
        raise TypeError(
            f"'pattern' must be a string literal or a re.compile object."
        )

    if not isinstance(_case_sensitive, bool):
        raise TypeError(f"'case_sensitive' must be boolean")

    try:
        iter(_uniques)
        if isinstance(_uniques, (str, dict)):
            raise Exception
        if not all(map(isinstance, _uniques, (str for _ in _uniques))):
            raise Exception
    except:
        raise TypeError(
            f"'uniques' must be a list-like sequence of strings."
        )

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *



    if not len(_uniques):
        return []


    # if re.compile was passed, just use that directly.
    # if user passed a literal string or regex, build re.Pattern from it
    if isinstance(_pattern, re.Pattern):
        _re_pattern = _pattern
    else:
        _re_pattern = re.compile(
            re.escape(_pattern),
            re.I if not _case_sensitive else 0
        )

    # _pattern and _case_sensitive dont matter after here, use _re_pattern


    def _finder(_x: str) -> bool:
        """Helper function for parallel pattern search."""
        nonlocal _re_pattern
        _hit = re.search(_re_pattern, _x)
        return (_hit is not None and _hit.span() != (0, 0))


    MASK = np.fromiter(map(_finder, _uniques), dtype=bool)

    del _finder

    if np.any(MASK):
        # convert to list so np.array always takes it, covert to ndarray to
        # apply mask, convert to set to get unique strings, then
        # convert back to list.
        return sorted(list(set(map(str, np.array(list(_uniques))[MASK].tolist()))))
    elif not np.any(MASK):
        return []





