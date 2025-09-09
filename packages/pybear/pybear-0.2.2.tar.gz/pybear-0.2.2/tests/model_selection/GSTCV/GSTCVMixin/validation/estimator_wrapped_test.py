# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.model_selection.GSTCV._GSTCVMixin._validation._estimator import \
    _val_estimator

from sklearn.preprocessing import OneHotEncoder as sk_OneHotEncoder

from sklearn.linear_model import (
    LinearRegression as sk_LinearRegression,
    Ridge as sk_Ridge,
    RidgeClassifier as sk_RidgeClassifier, # wrap with CCCV
    LogisticRegression as sk_LogisticRegression,
    SGDClassifier as sk_SGDClassifier,
    SGDRegressor as sk_SGDRegressor
)

from sklearn.calibration import CalibratedClassifierCV # wrap around RidgeClassifier

from sklearn.feature_extraction.text import CountVectorizer as sk_CountVectorizer
from sklearn.pipeline import Pipeline


# must be an instance not the class! & be an estimator!


class TestValWrappedEstimator:

    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    # CCCV ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    def test_accepts_sk_CCCV(self):
        assert _val_estimator(CalibratedClassifierCV(sk_RidgeClassifier())) is None
        assert _val_estimator(CalibratedClassifierCV(sk_SGDClassifier())) is None

    # END CCCV ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    # pipeline - 2 inner objects ** * ** * ** * ** * ** * ** * ** * ** *

    def _pipeline(self, _estimator_instance):
        return Pipeline(
            steps=[
                ('ct_vect', sk_CountVectorizer()),
                ('clf', _estimator_instance)
            ]
        )


    @pytest.mark.parametrize('junk_pipeline_steps',
        (
            [sk_OneHotEncoder(), sk_LogisticRegression()],
            [(4, sk_OneHotEncoder()), (3.14, sk_LogisticRegression())],
            [('onehot', 4), ('logistic', 3.14)]
        )
    )
    def test_rejects_pipeline_with_bad_steps(self, junk_pipeline_steps):
        # 24_07_27, unfortunately, sk pipeline does not do this, it will
        # allow bad steps (not in (str, cls()) format) and proceed and
        # return nonsensical results

        with pytest.raises(ValueError):
            _val_estimator(Pipeline(steps=junk_pipeline_steps))


    def test_rejects_not_instantiated(self):

        with pytest.raises(TypeError):
            _val_estimator(Pipeline)


    @pytest.mark.parametrize('non_estimator',
        (int, str, list, object, sk_OneHotEncoder)
    )
    def test_rejects_non_estimator(self, non_estimator):

        with pytest.raises((AttributeError, ValueError)):
            _val_estimator(self._pipeline(non_estimator()))


    @pytest.mark.parametrize('non_classifier',
        (sk_LinearRegression, sk_Ridge, sk_SGDRegressor)
    )
    def test_rejects_sk_non_classifier(self, non_classifier):

        with pytest.raises(AttributeError):
            _val_estimator(self._pipeline(non_classifier()))


    @pytest.mark.parametrize('good_classifiers', (sk_LogisticRegression, ))
    def test_accepts_classifiers(self, good_classifiers):
        assert _val_estimator(self._pipeline(good_classifiers())) is None


    def test_accepts_wrapped_sk_CCCV(self):
        assert _val_estimator(
            self._pipeline(CalibratedClassifierCV(sk_RidgeClassifier()))
        ) is None
        assert _val_estimator(
            self._pipeline(CalibratedClassifierCV(sk_SGDClassifier()))
        ) is None


    @pytest.mark.parametrize('junk_pipeline_steps',
        (
            [sk_OneHotEncoder(), sk_LogisticRegression()],
            [(4, sk_OneHotEncoder()), (3.14, sk_LogisticRegression())],
            [('onehot', 4), ('logistic', 3.14)]
        )
    )
    def test_rejects_pipeline_with_bad_steps(self, junk_pipeline_steps):
        # 24_07_27, unfortunately, sk pipeline does not do this, it will
        # allow bad steps (not in (str, cls()) format) and proceed and
        # return nonsensical results

        with pytest.raises(ValueError):
            _val_estimator(Pipeline(steps=junk_pipeline_steps))



    @pytest.mark.parametrize('good_pipeline_steps',
        ([('onehot', sk_OneHotEncoder()), ('logistic', sk_LogisticRegression())],)
    )
    def test_accepts_good_pipeline(self, good_pipeline_steps):

        assert _val_estimator(Pipeline(steps=good_pipeline_steps)) is None

    # END pipeline - 2 inner objects ** * ** * ** * ** * ** * ** * ** *
    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    # pipeline - 3 inner objects ** * ** * ** * ** * ** * ** * ** * ** *

    @staticmethod
    @pytest.fixture
    def sk_pipeline():
        # must be an instance not the class!
        return Pipeline(
            steps=[
                ('sk_CountVectorizer', sk_CountVectorizer()),
                ('sk_OneHotEncoder', sk_OneHotEncoder()),
                ('sk_Logistic', sk_LogisticRegression())
            ],
            verbose=0
        )


    def test_accuracy_pipeline(self,
        sk_pipeline
    ):

        assert _val_estimator(sk_pipeline) is None


    # END pipeline - 3 inner objects ** * ** * ** * ** * ** * ** * ** *
    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **




