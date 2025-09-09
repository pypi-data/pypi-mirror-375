# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
    Literal
)
from .._type_aliases import (
    SKXType,
    SKYType
)
from ..._type_aliases import ClassifierProtocol

import numbers
import time
import warnings

import joblib



@joblib.wrap_non_picklable_objects
def _parallelized_fit(
    _f_idx: int,
    _X_train: SKXType,
    _y_train: SKYType,
    _estimator: ClassifierProtocol,
    _grid: dict[str, Any],
    _error_score: numbers.Real | Literal['raise'],
    **_fit_params
) -> tuple[ClassifierProtocol, float, bool]:
    """Estimator fit method designed for joblib parallelism.

    Special exception handling on fit.

    Parameters
    ----------
    _f_idx : int
        The zero-based fold index of the train partition used in this
        fit; parallelism occurs over the different folds.
    _X_train : DaskXType
        A train partition of the data being fit.
    _y_train : SKYType
        The corresponding train partition of the target for the X train
        partition.
    _estimator : ClassifierProtocol
        Any non-dask scikit-style classifier, having `fit`, `get_params`,
        `predict_proba`, and `set_params` methods (the `score` method is
        not necessary, as `GSTCV` never calls it.) This includes, but is
        not limited to, scikit-learn, XGBoost, and LGBM classifiers.
    _grid : dict[str, Any]
        The hyperparameter values to be used during this fit. One
        permutation of all the grid search permutations.
    _error_score : numbers.Real | Literal['raise']
        If a training fold excepts during fitting, the exception can be
        allowed to raise by passing the 'raise' literal. Otherwise,
        passing a number-like will cause the exception to be handled,
        allowing the grid search to proceed, and the given number
        carries through scoring tabulations in place of the missing
        score(s).
    **_fit_params : dict[str, Any]
        Dictionary of fit_param:value pairs to be passed to the
        estimator's fit method. `fit_params` must have been processed
        by :func:`_estimator_fit_params_helper` so that any fit_param
        that has length == (n_samples in X and y) is split in the same
        way as X and y.

    Returns
    -------
    __ : tuple[EstimatorProtocol, float, bool]
        _estimator : EstimatorProtocol
            The fit estimator.
        _fit_time : float
            The seconds elapsed when performing the fit.
        _fit_excepted : bool
            True if the fit excepted and '_error_score' was not 'raise';
            False if the fit ran successfully.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    assert isinstance(_f_idx, int)
    assert isinstance(_grid, dict)
    assert isinstance(_error_score, (str, numbers.Real))

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * *


    _fit_excepted = False




    t0_fit = time.perf_counter()

    try:
        _estimator.fit(_X_train, _y_train, **_fit_params)
    except BrokenPipeError:
        raise BrokenPipeError  # FOR PYTEST ONLY
    except Exception as f:
        if _error_score == 'raise':
            raise ValueError(
                f"estimator excepted during fitting on {_grid}, cv fold "
                f"index {_f_idx} --- {f}"
            )
        else:
            _fit_excepted = True
            warnings.warn(
                f'\033[93mfit excepted on {_grid}, cv fold index {_f_idx}\033[0m'
            )

    _fit_time = time.perf_counter() - t0_fit

    del t0_fit

    return _estimator, _fit_time, _fit_excepted





