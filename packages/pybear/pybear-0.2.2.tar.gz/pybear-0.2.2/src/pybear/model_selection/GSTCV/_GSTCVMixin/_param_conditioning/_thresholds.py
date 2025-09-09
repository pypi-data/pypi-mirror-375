# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases import (
    ThresholdsInputType,
    ThresholdsWIPType
)

import numpy as np



def _cond_thresholds(
    _thresholds: ThresholdsInputType,
) -> ThresholdsWIPType:
    """Condition `_thresholds` into a sorted 1D list of 1 or more floats.

    Parameters
    ----------
    _thresholds : ThresholdsInputType
        User-defined threshold(s).

    Returns
    -------
    __thresholds: ThresholdsWIPType
        User-defined or default floats sorted ascending.

    """


    try:
        if _thresholds is None:
            __thresholds = \
                list(map(float, np.linspace(0, 1, 21).astype(np.float64)))
            raise MemoryError
        iter(_thresholds)
        # we know from val that its a legit 1D of floats
        __thresholds = list(map(float, set(_thresholds)))
    except MemoryError:
        pass
    except:
        # must be float
        __thresholds = list(map(float, [_thresholds]))


    __thresholds.sort()


    return __thresholds





