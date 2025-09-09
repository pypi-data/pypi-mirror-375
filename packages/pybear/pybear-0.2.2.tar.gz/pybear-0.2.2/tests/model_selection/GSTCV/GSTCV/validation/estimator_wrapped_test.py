# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.model_selection.GSTCV._GSTCV._validation._sk_estimator import \
    _val_sk_estimator

from sklearn.preprocessing import OneHotEncoder as sk_OneHotEncoder

from sklearn.linear_model import (
    RidgeClassifier as sk_RidgeClassifier, # wrap with CCCV
    LogisticRegression as sk_LogisticRegression,
    SGDClassifier as sk_SGDClassifier
)

from sklearn.calibration import CalibratedClassifierCV # wrap around RidgeClassifier

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline


# must be an instance not the class! & be an estimator!


class TestValWrappedEstimator:

    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    # CCCV ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    def test_accepts_sk_CCCV(self):
        assert _val_sk_estimator(CalibratedClassifierCV(sk_RidgeClassifier())) is None
        assert _val_sk_estimator(CalibratedClassifierCV(sk_SGDClassifier())) is None

    # END CCCV ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    def _pipeline(self, _estimator_instance):
        return Pipeline(
            steps=[
                ('ct_vect', CountVectorizer()),
                ('clf', _estimator_instance)
            ]
        )


    @pytest.mark.parametrize('good_classifiers', (sk_LogisticRegression, ))
    def test_accepts_sk_classifiers(self, good_classifiers):
        assert _val_sk_estimator(self._pipeline(good_classifiers())) is None


    def test_accepts_wrapped_sk_CCCV(self):
        assert _val_sk_estimator(
            self._pipeline(CalibratedClassifierCV(sk_RidgeClassifier()))
        ) is None
        assert _val_sk_estimator(
            self._pipeline(CalibratedClassifierCV(sk_SGDClassifier()))
        ) is None


    @pytest.mark.parametrize('good_pipeline_steps',
        ([('onehot', sk_OneHotEncoder()), ('logistic', sk_LogisticRegression())],)
    )
    def test_accepts_good_pipeline(self, good_pipeline_steps):

        assert _val_sk_estimator(Pipeline(steps=good_pipeline_steps)) is None





