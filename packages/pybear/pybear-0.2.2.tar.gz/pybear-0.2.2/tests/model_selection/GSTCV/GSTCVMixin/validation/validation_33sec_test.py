# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from sklearn.linear_model import LogisticRegression as sk_logistic

from pybear.model_selection.GSTCV._GSTCVMixin._validation._validation \
    import _validation



class TestValidation:


    @pytest.mark.parametrize('_return_train_score', (True, False))
    @pytest.mark.parametrize('_error_score', (np.e, 'raise'))
    @pytest.mark.parametrize('_verbose', (False, 1_000))
    @pytest.mark.parametrize('_cv',
        (None, 2, ((range(3), range(1,4)), (range(2,5), range(3,6))))
    )
    @pytest.mark.parametrize('_refit',
        (False, True, 'accuracy', lambda _cv_results: 0)
    )
    @pytest.mark.parametrize('_n_jobs', (None, 2))
    @pytest.mark.parametrize('_scoring',
        ('accuracy', ['accuracy', 'precision'], lambda x,y: 0.2835,
         {'accuracy': lambda x,y: 0, 'recall': lambda x,y: 1})
    )
    @pytest.mark.parametrize('_thresholds', (None, 0.5, np.linspace(0,1,11)))
    @pytest.mark.parametrize('_param_grid',
        (
            {'C': np.logspace(-5,5,11), 'fit_intercept': [True, False]},
            [{'C': np.logspace(-5,5,11)}, {'thresholds': [0, 0.5, 1]}]
        )
    )
    @pytest.mark.parametrize('_estimator', (sk_logistic(), ))
    def test_accuracy(
        self, _estimator, _param_grid, _thresholds, _scoring, _n_jobs,
        _refit, _cv, _verbose, _error_score, _return_train_score
    ):

        _will_raise = False
        # only because _scoring list & dict are len==2, not just
        # because they are lists and dicts
        _will_raise += _refit is True and isinstance(_scoring, (list, dict))
        # only because the _refit str is not correct for a scoring callable.
        # the correct str to pass to 'refit' when 'scoring' is a callable
        # is 'score' (or just pass True to 'refit')
        _will_raise += isinstance(_refit, str) and callable(_scoring)

        if _will_raise:
            with pytest.raises(ValueError):
                _validation(
                    _estimator,
                    _param_grid,
                    _thresholds,
                    _scoring,
                    _n_jobs,
                    _refit,
                    _cv,
                    _verbose,
                    _error_score,
                    _return_train_score
                )
        else:
            assert _validation(
                _estimator,
                _param_grid,
                _thresholds,
                _scoring,
                _n_jobs,
                _refit,
                _cv,
                _verbose,
                _error_score,
                _return_train_score
            ) is None





