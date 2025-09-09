# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import OverallStatisticsType

import numbers

import numpy as np

from .._validation._string_frequency import _val_string_frequency



def _build_overall_statistics(
    string_frequency_: dict[str, int],
    case_sensitive: bool = False
) -> OverallStatisticsType:
    """Populate a dictionary with the overall statistics.

    Populate a dictionary with the following statistics for all strings
    seen by the TextStatistics instance:

    - size

    - uniques_count

    - average_length

    - std_length

    - max_length

    - min_length

    Parameters
    ----------
    string_frequency_ : dict[str, int]
        A dictionary holding all the unique strings seen and their
        frequencies across all fits on the `TextStatistics` instance.
    case_sensitive : bool, default = False
        Whether to normalize all characters to the same case or preserve
        the original case.

    Returns
    -------
    overall_statistics : dict[str, numbers.Real]
        The statistics for the all the strings seen by the
        `TextStatistics` instance.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    _val_string_frequency(string_frequency_)

    if not isinstance(case_sensitive, bool):
        raise TypeError(f"'case_sensitive' must be boolean")

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    overall_statistics = {}

    overall_statistics['size'] = sum(string_frequency_.values())

    if case_sensitive:
        overall_statistics['uniques_count'] = len(string_frequency_)
    else:
        overall_statistics['uniques_count'] = \
            len(set(map(str.upper, string_frequency_)))


    _LENGTHS = np.fromiter(map(len, string_frequency_), dtype=np.uint32)
    __ = _LENGTHS.copy()
    __ *= np.array(list(string_frequency_.values()), dtype=np.uint32)
    __ = np.sum(__)
    __ /= overall_statistics['size']
    overall_statistics['average_length'] = float(__)
    del __
    len_pool = []
    for k, v in string_frequency_.items():
        len_pool += [len(k) for _ in range(v)]
    overall_statistics['std_length'] = float(np.std(len_pool))
    del len_pool
    overall_statistics['max_length'] = int(np.max(_LENGTHS))
    overall_statistics['min_length'] = int(np.min(min(_LENGTHS)))

    del _LENGTHS


    return overall_statistics





