# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd


# this module tests score for handling y.
# any X validation is handled by the estimator.





class TestSKScore_Y_Validation:


    @pytest.mark.parametrize('junk_y',
        (-1, 0, 1, 3.14, True, False, None, 'trash', min, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_y(
        self, X_np, junk_y, sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_np
    ):

        # this is raised by estimator, let it raise whatever
        with pytest.raises(Exception):
            sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_np.fit(X_np, junk_y)


    @pytest.mark.parametrize('_scoring',
        (['accuracy'], ['accuracy', 'balanced_accuracy']))
    @pytest.mark.parametrize('_y_container', ('np', 'df'))
    @pytest.mark.parametrize('_y_state', ('bad_features', 'bad_data'))
    def test_scoring(
        self, X_np, _scoring, _y_container, _y_state, _rows, _cols, COLUMNS,
        sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_np,
        sk_GSTCV_est_log_two_scorers_postfit_refit_str_fit_on_np
    ):


        if _scoring == ['accuracy']:
            sk_GSTCV = sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_np
        elif _scoring == ['accuracy', 'balanced_accuracy']:
            sk_GSTCV = sk_GSTCV_est_log_two_scorers_postfit_refit_str_fit_on_np

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
                getattr(sk_GSTCV, 'score')(X_np, y_sk)
        elif _y_state == 'bad_features':
            # this is raised by GSTCV in _val_y
            with pytest.raises(ValueError):
                getattr(sk_GSTCV, 'score')(X_np, y_sk)



