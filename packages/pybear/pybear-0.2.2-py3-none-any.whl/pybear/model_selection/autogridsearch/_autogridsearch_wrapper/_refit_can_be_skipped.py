# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Callable,
    Literal
)

from sklearn.model_selection import (
    GridSearchCV as SklearnGridSearchCV,
    RandomizedSearchCV as SklearnRandomizedSearchCV
)

from ...GSTCV._GSTCV import GSTCV

# agscv could possibly be wrapping a dask GSCV (dask_ml or pybear),
# but we cant import anything from dask, want to keep dask/dask_ml out
# of pybear. So in the absence of the ability to check for this, we only
# have a list of non-dask GSCVs that can skip refits, and anything not
# on the list (which includes everything we cant check for) must run
# refit on every pass. so for dask things this imposes the worst case
# and forces refit to happen on every pass, which is actually the correct
# thing to do for dask_ml, but is forcing GSTCVDask to do this
# unnecessarily (they should be using AutoGSTCVDask anyway!)



def _refit_can_be_skipped(
    _GridSearchParent,
    _scoring: None | str | list | Callable | dict | Literal[False],
    _total_passes: int
) -> bool:
    """Determine if the parent GridSearch, the scoring strategy, and the
    total number of passes allow for refits to be skipped until the
    final pass.

    `best_params_` needs to be exposed on every pass. Some GridSearch
    parents require that `refit` be True to expose `best_params_`. All
    require that `refit` be specified if `scoring` is multiple scorers
    to expose `best_params_`. Refit cannot be skipped if agscv is only
    running one pass.

    This ignores whether `refit` was originally passed as False. If it
    was, then this module will still allow agscv to overwrite pre-final
    pass `refit` with False, which is just overwriting the same value.

    Parameters
    ----------
    _GridSearchParent : object
        The parent `GridSearchCV` class passed to the agscv wrapper.
    _scoring : None | str | list | Callable | dict | Literal[False]]
        The value passed to the `scoring` parameter of the parent
        `GridSearchCV`. On the off chance that the parent GridSearch
        does not have a `scoring` parameter, Literal[False] is passed to
        here.
    _total_passes : int
        The number of grid searches to perform. This number is dynamic
        and can be incremented by agscv during a run, based on the need
        to shift grids and the setting of `total_passes_is_hard`.

    Returns
    -------
    _refit_can_be_skipped : bool
        Whether or not to allow refits to be skipped until the last pass
        of agscv.

    """


    # *** ONLY REFIT ON THE LAST PASS TO SAVE TIME WHEN POSSIBLE ***
    # IS POSSIBLE WHEN PARENT:
    # == has refit param, is not False, AND is using only one scorer
    # IS NOT POSSIBLE WHEN:
    # == total_passes = 1
    # == When using multiple scorers, refit must always be left on
    # because multiple scorers dont expose best_params_ when
    # multiscorer and refit=False
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # all of these have refit
    _is_candidate_gscv = _GridSearchParent in (
        SklearnGridSearchCV, SklearnRandomizedSearchCV, GSTCV
    )

    # if 'scoring' is not available from parent (Literal[False] was sent
    # into here), assume the worst case and set _is_multimetric to True
    # so that refit (if available) will always run
    _is_multimetric = 1
    _is_multimetric -= callable(_scoring)
    _is_multimetric -= isinstance(_scoring, (str, type(None)))
    # sklearn anomaly that list scoring is always multimetric,
    # even if len(list)==1.
    _is_not_multimetric = not bool(_is_multimetric)

    _is_multipass = (_total_passes > 1)
    # *** END ONLY REFIT ON THE LAST PASS TO SAVE TIME ************
    # *************************************************************


    return (_is_candidate_gscv and _is_not_multimetric and _is_multipass)




