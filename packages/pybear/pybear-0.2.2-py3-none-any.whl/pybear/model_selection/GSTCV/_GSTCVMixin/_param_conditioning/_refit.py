# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases import (
    RefitType,
    ScorerWIPType
)



def _cond_refit(
    _refit: RefitType,
    _scorer: ScorerWIPType
) -> RefitType:
    """Condition the `refit` parameter.

    If `refit` is a string, make sure it is lower-case, and if there is
    only one scorer, change the string to 'score'. If `refit` is True,
    change `refit` to 'score'.

    Parameters
    ----------
    _refit : RefitType
        Whether to refit the estimator on the 'best' parameters after
        completing the grid searches, and if so, which scoring metric to
        use to determine the 'best' parameters.
    _scorer : dict[str, Callable]
        Previously conditioned scorer object, must be dict[str, Callable].
        Used to determine the number of scorers, which impacts the final
        value for the `refit` param.

    Returns
    -------
    _refit: RefitType, default=True
        Conditioned `refit`.

    """


    # _refit can be callable, bool, str


    if _refit is False or callable(_refit):
        pass
    elif _refit is True:
        # already proved len(_scorer) == 1 when True
        _refit = 'score'
    elif isinstance(_refit, str):  # refit MUST MATCH A STRING IN scoring
        _refit = _refit.lower()
        if len(_scorer) == 1:
            _refit = 'score'
    else:
        # validation module should not allow us to get in here
        raise Exception


    return _refit




