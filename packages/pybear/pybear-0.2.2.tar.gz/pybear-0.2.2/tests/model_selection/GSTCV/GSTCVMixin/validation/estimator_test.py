# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.model_selection.GSTCV._GSTCVMixin._validation._estimator import \
    _val_estimator

from sklearn.preprocessing import OneHotEncoder as sk_OneHotEncoder
from sklearn.feature_extraction.text import CountVectorizer as sk_CountVectorizer

# wrap around RidgeClassifier
from sklearn.calibration import CalibratedClassifierCV

from sklearn.linear_model import (
    LinearRegression as sk_LinearRegression,
    Ridge as sk_Ridge,
    RidgeClassifier as sk_RidgeClassifier, # wrap with CCCV
    LogisticRegression as sk_LogisticRegression,
    SGDClassifier as sk_SGDClassifier,
    SGDRegressor as sk_SGDRegressor
)

# must be an instance not the class! & be an estimator!



class TestValEstimator:


    @pytest.mark.parametrize('not_instantiated',
        (sk_OneHotEncoder, sk_LinearRegression, sk_Ridge, sk_RidgeClassifier,
        sk_LogisticRegression, sk_SGDClassifier, sk_SGDRegressor,
        CalibratedClassifierCV)
    )
    def test_rejects_not_instantiated(self, not_instantiated):

        with pytest.raises(
            TypeError,
            match=f"estimator must be an instance, not the class"
        ):
            _val_estimator(not_instantiated)


    @pytest.mark.parametrize('non_estimator',
        (int, str, list, object, sk_OneHotEncoder, sk_CountVectorizer)
    )
    def test_rejects_non_estimator(self, non_estimator):

        with pytest.raises(AttributeError):
            _val_estimator(non_estimator())


    @pytest.mark.parametrize('non_classifier',
        (sk_LinearRegression, sk_Ridge, sk_SGDRegressor)
    )
    def test_rejects_non_classifier(self, non_classifier):

        with pytest.raises(AttributeError):
            _val_estimator(non_classifier())


    @pytest.mark.parametrize('good_classifiers', (sk_LogisticRegression, ))
    def test_accepts_sk_classifiers(self, good_classifiers):

        assert _val_estimator(good_classifiers()) is None





