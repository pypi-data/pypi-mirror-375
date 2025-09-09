# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Callable
from ..._type_aliases import (
    RefitType,
    ScorerInputType
)

import warnings



def _val_refit(
    _refit: RefitType,
    _scoring: ScorerInputType
) -> None:
    """Validate the `refit` parameter with respect to the number of scorers.

    In all cases, `refit` can be boolean False, a string that indicates
    the scorer to use to determine the best parameters (when there is
    only one scorer there is only one possible string value), or a
    callable. When one metric is used, refit can be boolean True or
    False, but boolean True cannot be used when there is more than one
    scorer.

    The `refit` callable takes in `cv_results_` and returns `best_index_`
    (an integer).

    Parameters
    ----------
    _refit : RefitType
        Whether to refit the estimator on the 'best' parameters after
        completing the grid search, and if so, which scoring metric to
        use to determine the 'best' parameters.
    _scoring : ScorerInputType
        Previously validated `scoring` parameter, the scoring metric(s)
        used to evaluate the predictions on the test (and possibly train)
        sets. Used to determine the number of scorers and valid scorer
        names, which impacts what values are allowed for the `refit`
        param.

    Returns
    -------
    None

    """


    _err_msg = (
        f"for single scoring metric, refit must be:"
        f"\n1) bool, "
        f"\n2) a single string exactly matching the scoring method in scoring, or "
        f"\n3) a callable that takes cv_results_ as input and returns an integer."
        f"\nfor multiple scoring metrics, refit must be:"
        f"\n1) boolean False"
        f"\n2) a single string exactly matching any scoring method in scoring, or "
        f"\n3) a callable that takes cv_results_ as input and returns an integer."
    )


    # _refit can be callable, bool, str

    # need to make a mock '_scorer' Sequence from '_scoring' with all of
    # its possible input types to validate refit
    # we already know from _val_scoring that _scoring is legit
    if isinstance(_scoring, str):
        _mock_scorer = [_scoring.lower()]
    elif isinstance(_scoring, Callable):
        _mock_scorer = ['score']
    else:  # must be list-like or dict:
        _mock_scorer = list(map(str.lower, _scoring))


    if _refit is False or callable(_refit):
        # THERE ISNT A WAY TO RETURN A best_threshold_ WHEN MULTIPLE
        # SCORERS ARE PASSED TO scoring AND refit IS False OR A CALLABLE
        # (OK IF REFIT IS A STRING).
        if len(_mock_scorer) > 1:
            warnings.warn(
                f"\nWHEN MULTIPLE SCORERS ARE USED:"
                f"\nCannot return a best threshold if refit is False or callable."
                f"\nIf refit is False: best_index_, best_estimator_, best_score_, "
                f"and best_threshold_ are not available."
                f"\nIf refit is callable: best_score_ and best_threshold_ "
                f"are not available."
                f"\nIn either case, access score and threshold info via the "
                f"cv_results_ attribute."
            )
    elif _refit is True:
        if len(_mock_scorer) > 1:
            raise ValueError(_err_msg)
    elif isinstance(_refit, str):  # refit MUST MATCH A STRING IN scoring
        _refit = _refit.lower()  # do not return this
        # _scoring KEYS CAN ONLY BE SINGLE STRINGS: 1) user-defined via dict,
        # 2) 'score', or 3) actual score method name
        if _refit not in list(map(str.lower, _mock_scorer)):
            raise ValueError(
                f"if refit is a string ('{_refit}'), refit must exactly "
                f"match the (or one of the) scoring methods in scoring"
            )
    else:
        raise TypeError(_err_msg)


    del _err_msg, _mock_scorer




