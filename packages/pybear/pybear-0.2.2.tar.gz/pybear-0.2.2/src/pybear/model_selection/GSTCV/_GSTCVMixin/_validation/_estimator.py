# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases import ClassifierProtocol

import inspect

from .....utilities._check_pipeline import check_pipeline



def _val_estimator(
    _estimator: ClassifierProtocol
) -> None:
    """General validation for sklearn-like estimators.

    The `GSTCV` modules are expected to most likely encounter sklearn,
    dask_ml, xgboost, and lightgbm estimators, and maybe some other
    pybear modules. The estimator must be passed as an instance, not the
    class itself.

    Validate that an estimator:

    1) is an instance, not a class.

    2) if in a pipe, the pipe is built correctly

    3) is a classifier, as indicated by the presence of a `predict_proba`
    method. (early in dev this was done by sklearn.base.is_classifier)

    4) meets the other requirements of `GridSearchCV` in having `fit`,
    `set_params`, and `get_params` methods.

    Parameters
    ----------
    _estimator : ClassifierProtocol
        The estimator to be validated.


    Returns
    -------
    None

    """


    # must be an instance not the class!
    if inspect.isclass(_estimator):
        raise TypeError(f"estimator must be an instance, not the class")

    # could be a pipeline

    # validate pipeline ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    # because sklearn doesn't do this, and could be hard to detect
    if 'pipe' in str(type(_estimator)).lower():
        check_pipeline(_estimator)
    # END validate pipeline ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # validate estimator ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    # must have the sklearn API
    _has_method = lambda _method: callable(getattr(_estimator, _method, None))

    if not _has_method('fit'):
        raise AttributeError(f"estimator must have a 'fit' method")
    if not _has_method('set_params'):
        raise AttributeError(f"estimator must have a 'set_params' method")
    if not _has_method('get_params'):
        raise AttributeError(f"estimator must have a 'get_params' method")
    if not _has_method('predict_proba'):
        raise AttributeError(f"estimator must have a 'predict_proba' method")

    del _has_method
    # END validate estimator ** * ** * ** * ** * ** * ** * ** * ** * **


    return





