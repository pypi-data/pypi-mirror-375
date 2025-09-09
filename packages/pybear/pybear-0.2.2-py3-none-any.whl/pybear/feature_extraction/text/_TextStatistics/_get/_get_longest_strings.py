# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers

import numpy as np

from .._validation._string_frequency import _val_string_frequency
from .._validation._n import _val_n



def _get_longest_strings(
    string_frequency: dict[str, int],
    n: int = 10
) -> dict[str, int]:
    """Return the longest strings in the `string_frequency_` attribute
    as a dictionary with strings as keys and frequencies as values.

    If TS parameter `store_uniques` is False, `string_frequency` will be
    empty, so just return an empty dictionary.

    Parameters
    ----------
    string_frequency : dict[str, int]
        The dictionary holding the unique strings seen by the fitted
        `TextStatistics` instance, and the number of occurrences of each
        string.
    n : int, default = 10
        The number of top longest strings to retrieve.

    Returns
    -------
    longest_strings: dict[str, int]
        The top 'n' longest strings and their frequencies.

    """


    _val_string_frequency(string_frequency)
    _val_n(n)


    if not len(string_frequency):
        return {}


    _LENS = np.fromiter(map(len, string_frequency), dtype=np.uint32)
    _UNIQUES = np.fromiter(string_frequency.keys(), dtype=f"<U{int(np.max(_LENS))}")
    _COUNTS = np.fromiter(string_frequency.values(), dtype=np.uint32)

    n = min(n, len(_UNIQUES))
    # SORT ON desc len(str) FIRST, THEN ASC ALPHA ON STR (lexsort GOES BACKWARDS)
    MASK = np.lexsort((_UNIQUES, 1 / _LENS))[:n]
    del _LENS

    TOP_LONGEST_STRINGS = _UNIQUES[MASK]
    TOP_FREQUENCIES = _COUNTS[MASK]
    del _UNIQUES, _COUNTS, MASK

    longest_strings = dict((zip(
        map(str, TOP_LONGEST_STRINGS),
        map(int, TOP_FREQUENCIES)
    )))

    del TOP_LONGEST_STRINGS, TOP_FREQUENCIES


    return longest_strings






