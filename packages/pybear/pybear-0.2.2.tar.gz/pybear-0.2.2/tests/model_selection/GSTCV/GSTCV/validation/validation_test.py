# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.model_selection.GSTCV._GSTCV._validation._validation import \
    _validation

import pytest

from sklearn.linear_model import LogisticRegression as sk_LogisticRegression



class TestValidation:


    @pytest.mark.parametrize('_estimator', (sk_LogisticRegression(), ))
    @pytest.mark.parametrize('_pre_dispatch',  ('all', '2*n_jobs'))
    def test_accuracy(self, _estimator, _pre_dispatch):

        _validation(
            _estimator,
            _pre_dispatch
        )





