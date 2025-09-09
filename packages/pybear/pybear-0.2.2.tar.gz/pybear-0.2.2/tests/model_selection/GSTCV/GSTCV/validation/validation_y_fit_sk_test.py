# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
from copy import deepcopy
import numpy as np
import pandas as pd


# this module tests fit for handling y.
# any X validation is handled by the estimator.



class TestSKFit_Y_Validation:


    @pytest.mark.parametrize('junk_y',
        (-1, 0, 1, 3.14, True, False, None, 'trash', min, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_y(
        self, X_np, junk_y, sk_GSTCV_est_log_one_scorer_prefit
    ):

        # this is raised by estimator, let it raise whatever
        with pytest.raises(Exception):
            sk_GSTCV_est_log_one_scorer_prefit.fit(X_np, junk_y)


    @pytest.mark.parametrize('_y_container', ('np', 'df'))
    @pytest.mark.parametrize('_y_state', ('bad_data', 'bad_features'))
    def test_y(
        self, _y_container, _y_state, X_np, _rows, _cols,
        COLUMNS, sk_GSTCV_est_log_one_scorer_prefit
    ):

        # need to make a new instance of the prefit GSTCV, because the fitting
        # tests alter its state along the way, and it is a session fixture
        shallow_params = \
            deepcopy(sk_GSTCV_est_log_one_scorer_prefit.get_params(deep=False))
        deep_params = \
            deepcopy(sk_GSTCV_est_log_one_scorer_prefit.get_params(deep=True))

        sk_GSTCV = type(sk_GSTCV_est_log_one_scorer_prefit)(**shallow_params)
        sk_GSTCV.set_params(**deep_params)

        # y ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        if _y_state == 'bad_data':
            y_sk = np.random.choice(list('abcd'), (_rows, 1), replace=True)
        elif _y_state == 'bad_features':
            y_sk = np.random.randint(0, 2, (_rows, 2))
        else:
            raise Exception

        if _y_container == 'df':
            y_sk = pd.DataFrame(data=y_sk)
        # END y ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


        if _y_state == 'bad_data':
            # this is raised by _val_y for not in [0,1]
            with pytest.raises(ValueError):
                getattr(sk_GSTCV, 'fit')(X_np, y_sk)
        elif _y_state == 'bad_features':
            # this is raised by GSTCV in _val_y
            with pytest.raises(ValueError):
                getattr(sk_GSTCV, 'fit')(X_np, y_sk)



