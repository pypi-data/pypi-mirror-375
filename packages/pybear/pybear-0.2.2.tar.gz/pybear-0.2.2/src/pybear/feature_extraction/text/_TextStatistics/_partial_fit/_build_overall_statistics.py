# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
)
from .._type_aliases import OverallStatisticsType

import numpy as np

from .....base._check_1D_str_sequence import check_1D_str_sequence



def _build_overall_statistics(
    STRINGS:Sequence[str],
    case_sensitive:bool = False
) -> OverallStatisticsType:
    """Populate a dictionary with the overall statistics.

    Populate a dictionary with the following statistics for the current
    batch of strings:

    - size

    - uniques_count

    - average_length

    - std_length

    - max_length

    - min_length


    Parameters
    ----------
    STRINGS : Sequence[str]
        A list-like of strings passed to `fit` or `partial_fit`.
    case_sensitive : bool, default = False
        Whether to normalize all characters to the same case or preserve
        the original case.

    Returns
    -------
    overall_statistics: dict[str, numbers.Real]
        The statistics for the current batch of data.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    check_1D_str_sequence(STRINGS, require_all_finite=False)

    if len(STRINGS) == 0:
        raise ValueError(
            f"'strings' must be passed as a list-like vector of "
            f"strings, cannot be empty."
        )

    if not isinstance(case_sensitive, bool):
        raise TypeError(f"'case_sensitive' must be boolean")

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    _LENGTHS = np.fromiter(map(len, STRINGS), dtype=np.uint32)

    overall_statistics = {}

    overall_statistics['size'] = len(STRINGS)

    if case_sensitive:
        overall_statistics['uniques_count'] = len(set(STRINGS))
    else:
        overall_statistics['uniques_count'] = len(set(map(str.upper, STRINGS)))

    overall_statistics['average_length'] = float(np.mean(_LENGTHS))
    overall_statistics['std_length'] = float(np.std(_LENGTHS))
    overall_statistics['max_length'] = int(np.max(_LENGTHS))
    overall_statistics['min_length'] = int(np.min(min(_LENGTHS)))

    del _LENGTHS


    return overall_statistics






