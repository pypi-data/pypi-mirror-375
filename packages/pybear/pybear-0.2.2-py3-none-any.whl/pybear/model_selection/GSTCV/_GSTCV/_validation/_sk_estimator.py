# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases import ClassifierProtocol

import sys

from sklearn.pipeline import Pipeline



def _val_sk_estimator(
    _estimator: ClassifierProtocol
) -> None:
    """The GSTCV module is expected to most likely encounter sklearn,
    xgboost, and lightgbm estimators, and maybe some other pybear modules.

    The estimator must be passed as an instance, not the class itself.

    Validate that the estimator is not a dask estimator, either from
    dask itself, or from XGBoost or LightGBM.

    Parameters
    ----------
    _estimator : ClassifierProtocol
        The estimator to be validated.

    Returns
    -------
    None

    """


    # validate estimator ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    def get_inner_most_estimator(__estimator):

        try:
            if isinstance(__estimator, Pipeline):
                return get_inner_most_estimator(__estimator.steps[-1][-1])
            else:
                return get_inner_most_estimator(__estimator.estimator)
        except:
            return __estimator


    __estimator = get_inner_most_estimator(_estimator)

    try:
        _module = sys.modules[__estimator.__class__.__module__].__file__
    except:
        raise AttributeError(f"'{__estimator.__class__.__name__}' is not "
            f"a valid classifier")

    if 'dask' in str(_module).lower():
        raise TypeError(f"{__estimator.__class__.__name__}: GSTCV cannot "
            f"accept dask classifiers. To use dask classifiers, use GSTCVDask.")

    del get_inner_most_estimator, __estimator, _module

    # END validate estimator ** * ** * ** * ** * ** * ** * ** * ** * **







