# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd

from sklearn.model_selection import StratifiedKFold

from pybear.model_selection.GSTCV._GSTCV.GSTCV import GSTCV

# 24_08_11 this module tests the operation of the cv kwarg in sk GSTCV,
# proves the equality of cv_results_ when cv as int and cv as iterable
# are expected to give identical folds. This only needs to be tested for
# an estimator, as the splitting processes is independent of estimator
# being a single estimator or a pipeline.



class TestCV:


    @pytest.mark.parametrize('_n_jobs', (-1, 1))  # 1 is important
    def test_accuracy_cv_int_vs_cv_iter(
        self, X_np, y_np, sk_est_log, standard_WIP_scorer, _n_jobs
    ):

        # test equivalent cv as int or iterable give same output
        _cv_int = 3

        # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

        # dont use session fixture!
        TestCls1 = GSTCV(
            estimator=sk_est_log,
            param_grid=[
                {'C': [1e-5], 'fit_intercept': [True]},
                {'C': [1e-1], 'fit_intercept': [False]}
            ],
            cv=_cv_int,     # <===========
            error_score='raise',
            refit=False,
            verbose=0,
            scoring=standard_WIP_scorer,
            n_jobs=_n_jobs,
            pre_dispatch='2*n_jobs',
            return_train_score=True
        )

        TestCls1.fit(X_np, y_np)

        cv_results_int = pd.DataFrame(TestCls1.cv_results_)
        # drop time columns
        _drop_columns = [c for c in cv_results_int.columns if 'time' in c]
        cv_results_int = cv_results_int.drop(columns=_drop_columns)
        del _drop_columns

        # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

        # must use StratifiedKFold to pass this test
        # dont use session fixture!
        TestCls2 = GSTCV(
            estimator=sk_est_log,
            param_grid=[
                {'C': [1e-5], 'fit_intercept': [True]},
                {'C': [1e-1], 'fit_intercept': [False]}
            ],
            cv=StratifiedKFold(n_splits=_cv_int).split(X_np, y_np), # <===
            error_score='raise',
            refit=False,
            verbose=0,
            scoring=standard_WIP_scorer,
            n_jobs=_n_jobs,
            pre_dispatch='2*n_jobs',
            return_train_score=True
        )

        TestCls2.fit(X_np, y_np)

        cv_results_iter = pd.DataFrame(TestCls2.cv_results_)
        # drop time columns
        _drop_columns = [c for c in cv_results_iter.columns if 'time' in c]
        cv_results_iter = cv_results_iter.drop(columns=_drop_columns)
        del _drop_columns

        # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

        assert np.array_equal(cv_results_int.columns, cv_results_iter.columns)

        for _c in cv_results_int:
            assert np.array_equal(cv_results_int[_c], cv_results_iter[_c]), \
                f"{cv_results_int[_c]} fail"

        # cv_results_ being equal for both outs proves that comparable
        # cv as int & cv as iterator give same output





