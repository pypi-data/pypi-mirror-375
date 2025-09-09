# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases import (
    ParamsType,
    IsLogspaceType
)

import numpy as np



def _validate_is_logspace(
    _IS_LOGSPACE: IsLogspaceType,
    _params: ParamsType
) -> None:
    """Validate `_IS_LOGSPACE`.

    Should be dict[str, Literal[False] | numbers.Integer]

    Parameters
    ----------
    _IS_LOGSPACE : IsLogspaceType
        For all numerical parameters, if the space is linear, or some
        other non-standard interval, it is False. If it is logspace, the
        'truth' of being a logspace is represented by a number indicating
        the interval of the logspace. E.g., np.logspace(-5, 5, 11) would
        be represented by 1.0, and np.logspace(-20, 20, 9) would be
        represented by 5.0.
    _params : ParamsType
        The agscv instructions for all parameters.

    Returns
    -------
    None

    """


    err_msg = (f"_IS_LOGSPACE must be a dict with str keys and bool/float "
               f"values >= 0")
    if not isinstance(_IS_LOGSPACE, dict):
        raise TypeError(err_msg)

    if not all(map(
        isinstance,
        _IS_LOGSPACE.keys(),
        (str for _ in _IS_LOGSPACE)
    )):
        raise TypeError(err_msg)

    # all params in _params must be in IS_LOGSPACE and vice versa
    NOT_IN_LOGSPACE = []
    NOT_IN_PARAMS = []
    for _param in _params:
        if _param not in _IS_LOGSPACE:
            NOT_IN_LOGSPACE.append(_param)
    for _param in _IS_LOGSPACE:
        if _param not in _params:
            NOT_IN_PARAMS.append(_param)

    if len(NOT_IN_LOGSPACE):
        raise ValueError(f"parameters in _params not in _IS_LOGSPACE: "
            f"{', '.join(NOT_IN_LOGSPACE)}")

    if len(NOT_IN_PARAMS):
        raise ValueError(f"parameters in _IS_LOGSPACE not in _params: "
            f"{', '.join(NOT_IN_PARAMS)}")

    del NOT_IN_LOGSPACE, NOT_IN_PARAMS

    try:
        __ = list(map(float, _IS_LOGSPACE.values()))
    except:
        raise TypeError(err_msg)

    if not np.array_equiv(__, list(map(abs, __))):
        raise ValueError(err_msg)

    del err_msg, __







