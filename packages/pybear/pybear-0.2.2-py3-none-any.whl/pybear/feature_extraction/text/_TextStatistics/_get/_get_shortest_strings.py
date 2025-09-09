# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers

import numpy as np

from .._validation._string_frequency import _val_string_frequency
from .._validation._n import _val_n



def _get_shortest_strings(
    string_frequency: dict[str, int],
    n: int = 10
) -> dict[str, int]:
    """Return the shortest strings in the `string_frequency_` attribute
    as a dictionary with strings as keys and frequencies as values. If
    TS parameter `store_uniques` is False, `string_frequency` will be
    empty, so just return an empty dictionary.

    Parameters
    ----------
    string_frequency : dict[str, int]
        The dictionary holding the unique strings seen by the fitted
        `TextStatistics` instance, and the number of occurrences of each
        string.
    n : int, default = 10
        The number of top shortest strings to retrieve.

    Returns
    -------
    shortest_strings : dict[str, int]
        The top 'n' shortest strings and their frequencies.

    """


    _val_string_frequency(string_frequency)
    _val_n(n)


    if not len(string_frequency):
        return {}


    _LENS = np.fromiter(map(len, string_frequency), dtype=np.uint32)
    _UNIQUES = np.fromiter(string_frequency.keys(), dtype=f"<U{int(np.max(_LENS))}")
    _COUNTS = np.fromiter(string_frequency.values(), dtype=np.uint32)

    n = min(n, len(_UNIQUES))
    # SORT ON len(str) FIRST, THEN ASC ALPHA ON STR (lexsort GOES BACKWARDS)
    MASK = np.lexsort((_UNIQUES, _LENS))[:n]
    del _LENS

    TOP_SHORTEST_STRINGS = _UNIQUES[MASK]
    TOP_FREQUENCIES = _COUNTS[MASK]
    del _UNIQUES, _COUNTS, MASK

    shortest_strings = dict((zip(
        map(str, TOP_SHORTEST_STRINGS),
        map(int, TOP_FREQUENCIES)
    )))

    del TOP_SHORTEST_STRINGS, TOP_FREQUENCIES


    return shortest_strings





