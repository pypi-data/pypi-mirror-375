# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Callable
from ..._type_aliases import (
    ScorerInputType,
    ScorerWIPType,
)

from ....GSTCV._GSTCVMixin._validation._scoring import master_scorer_dict



def _cond_scoring(
    _scoring: ScorerInputType
) -> ScorerWIPType:
    """Condition `scoring`, the scoring metric(s) used to evaluate the
    predictions on the test (and possibly train) sets.

    Convert any of the valid input formats to an output format of
    dict[str, Callable]. Can come in here as str, Sequence[str],
    Callable, dict[str, Callable].

    Parameters
    ----------
    _scoring : ScorerInputType
        The scoring metric(s) used to evaluate the predictions on the
        test (and possibly train) sets.

    Returns
    -------
    _scoring : ScorerWIPType
        Dictionary of format {scorer_name: scorer callable} no matter
        how many metrics are used. When one metric is used, change the
        actual scorer name to 'score'.

    """


    try:
        if isinstance(_scoring, Callable):
            raise Exception
        iter(_scoring)
        if isinstance(_scoring, (dict, str)):
            raise Exception
        _is_list_like = True
    except:
        _is_list_like = False


    if isinstance(_scoring, str):
        _scoring = {_scoring.lower(): master_scorer_dict[_scoring]}

    elif callable(_scoring):
        _scoring = {f'score': _scoring}

    elif _is_list_like:

        _scoring = list(set(map(str.lower, _scoring)))

        _scoring = {k: v for k, v in master_scorer_dict.items() if k in _scoring}

    elif isinstance(_scoring, dict):

        for key in list(_scoring.keys()):
            _scoring[key.lower()] = _scoring.pop(key)

    else:
        raise Exception


    del _is_list_like

    # IF ONE THING IN SCORING, CHANGE THE KEY TO 'score'
    if len(_scoring) == 1:
        _scoring = {'score': v for k, v in _scoring.items()}


    # dict of functions - Scorer functions used on the held out data to
    # choose the best parameters for the model, in a dictionary of format
    # {scorer_name: scorer}, when one or multiple metrics are used.
    return _scoring






