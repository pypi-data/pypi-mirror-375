# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.model_selection.GSTCV._GSTCV._validation._sk_estimator import \
    _val_sk_estimator

from sklearn.linear_model import LogisticRegression as sk_LogisticRegression


# must be an instance not the class! & be an estimator!


class TestValSkEstimator:


    @pytest.mark.parametrize('good_classifiers', (sk_LogisticRegression, ))
    def test_accepts_sk_classifiers(self, good_classifiers):
        assert _val_sk_estimator(good_classifiers()) is None



