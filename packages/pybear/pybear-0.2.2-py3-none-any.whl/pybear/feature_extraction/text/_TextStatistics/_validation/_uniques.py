# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Sequence

import numpy as np



def _val_uniques(_uniques: Sequence[str]) -> None:
    """Validate that `_uniques` is a sequence of strings, and that all
    the values in it are unique.

    Parameters
    ----------
    _uniques : Sequence[str]
        A sequence of unique strings. Could be the uniques seen
        on one partial fit, or all uniques seen during fits on the
        `TextStatistics` instance.

    Returns
    -------
    None

    """

    try:
        iter(_uniques)
        if isinstance(_uniques, (str, dict)):
            raise Exception
        if not all(map(isinstance, _uniques, (str for _ in _uniques))):
            raise Exception
        if np.any(np.unique(_uniques, return_counts=True)[1] > 1):
            raise Exception
    except Exception as e:
        raise TypeError(
            f"'_uniques' must be a sequence of strings without any duplicates"
        )






