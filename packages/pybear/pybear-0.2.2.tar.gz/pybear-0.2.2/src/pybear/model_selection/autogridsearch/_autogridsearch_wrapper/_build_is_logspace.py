# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy as np

from ._type_aliases import (
    ParamsType,
    IsLogspaceType
)



def _build_is_logspace(
    _params: ParamsType
) -> IsLogspaceType:
    """`_IS_LOGSPACE` is a dictionary keyed by all param names,
    including fixed params. Fixed params are always False. For numerical
    params, if the space is linear, or some other non-standard interval,
    the value is False. If it is logspace, the 'truth' of being a
    logspace is represented by a number indicating the interval of the
    logspace. E.g., np.logspace(-5, 5, 11) would be represented by 1.0,
    and np.logspace(-20, 20, 9) would be represented by 5.0.

    Parameters
    ----------
    _params : ParamsType
        The instructions for performing grid searches for each parameter.

    Returns
    -------
    _IS_LOGSPACE : IsLogspaceType
        A dictionary indicating whether a parameter's search space is
        logarithmic. If so, the logspace interval of the space.

    """


    _IS_LOGSPACE = dict()
    for _param in _params:

        __ = _params[_param]

        if __[-1] == 'fixed_string':
            _IS_LOGSPACE[_param] = False

        elif __[-1] == 'fixed_bool':
            _IS_LOGSPACE[_param] = False

        else:
            # "soft" & "hard" CAN BE LOGSPACES, BUT "fixed" CANNOT
            if "fixed" in __[-1]:
                _IS_LOGSPACE[_param] = False
                continue

            # if 0 in the space, cannot be logspace
            if 0 in __[0]:
                _IS_LOGSPACE[_param] = False
                continue

            # if 2 or less points in points, cannot be logspace
            if __[-2][0] <= 2:
                _IS_LOGSPACE[_param] = False
                continue

            # IF IS LOGSPACE, PUT IN THE INTERVAL OF THE GAP
            log_gap = np.log10(__[0])[1:] - np.log10(__[0])[:-1]

            if len(np.unique(log_gap)) == 1:  # UNIFORM GAP SIZE IN LOG SCALE
                _IS_LOGSPACE[_param] = log_gap[0]
            else:
                # MUST BE LINSPACE OR SOMETHING ELSE
                _IS_LOGSPACE[_param] = False

            del __, log_gap


    return _IS_LOGSPACE








