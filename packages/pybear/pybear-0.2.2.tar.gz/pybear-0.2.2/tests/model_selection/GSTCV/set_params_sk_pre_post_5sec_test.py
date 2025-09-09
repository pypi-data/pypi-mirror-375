# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy

from sklearn.linear_model import LinearRegression as sk_LinearRegression

from sklearn.feature_extraction.text import CountVectorizer as sk_CountVectorizer
from sklearn.pipeline import Pipeline



class TestSKSetParams:


    @pytest.mark.parametrize('_state,_refit',
        (('prefit', False), ('postfit', 'accuracy'), ('postfit', False)),
        scope='class'
    )
    @pytest.mark.parametrize('junk_param',
        (0, 1, 3.14, None, True, 'trash', [0,1], (0, 1), min, lambda x: x)
    )
    def test_rejects_junk_params(
        self, junk_param, _state, _refit,
        sk_GSTCV_est_log_one_scorer_prefit,
        sk_GSTCV_est_log_one_scorer_postfit_refit_false_fit_on_np,
        sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_np,
        sk_GSTCV_pipe_log_one_scorer_prefit,
        sk_GSTCV_pipe_log_one_scorer_postfit_refit_false_fit_on_np,
        sk_GSTCV_pipe_log_one_scorer_postfit_refit_str_fit_on_np
    ):

        if _state == 'prefit':
            _GSTCV = sk_GSTCV_est_log_one_scorer_prefit
            _GSTCV_PIPE = sk_GSTCV_pipe_log_one_scorer_prefit
        elif _state == 'postfit':
            if _refit is False:
                _GSTCV = sk_GSTCV_est_log_one_scorer_postfit_refit_false_fit_on_np
                _GSTCV_PIPE = sk_GSTCV_pipe_log_one_scorer_postfit_refit_false_fit_on_np
            elif _refit == 'accuracy':
                _GSTCV = sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_np
                _GSTCV_PIPE = sk_GSTCV_pipe_log_one_scorer_postfit_refit_str_fit_on_np


        with pytest.raises(TypeError):
            _GSTCV.set_params(junk_param)

        with pytest.raises(TypeError):
            _GSTCV_PIPE.set_params(junk_param)



    @pytest.mark.parametrize('_state,_refit',
        (('prefit', False), ('postfit', 'accuracy'), ('postfit', False)),
        scope='class'
    )
    def test_accuracy(
        self, _state, _refit,
        sk_GSTCV_est_log_one_scorer_prefit,
        sk_GSTCV_est_log_one_scorer_postfit_refit_false_fit_on_np,
        sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_np,
        sk_GSTCV_pipe_log_one_scorer_prefit,
        sk_GSTCV_pipe_log_one_scorer_postfit_refit_false_fit_on_np,
        sk_GSTCV_pipe_log_one_scorer_postfit_refit_str_fit_on_np,
        sk_est_log
    ):

        if _state == 'prefit':
            _GSTCV = sk_GSTCV_est_log_one_scorer_prefit
            _GSTCV_PIPE = sk_GSTCV_pipe_log_one_scorer_prefit
        elif _state == 'postfit':
            if _refit is False:
                _GSTCV = sk_GSTCV_est_log_one_scorer_postfit_refit_false_fit_on_np
                _GSTCV_PIPE = sk_GSTCV_pipe_log_one_scorer_postfit_refit_false_fit_on_np
            elif _refit == 'accuracy':
                _GSTCV = sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_np
                _GSTCV_PIPE = sk_GSTCV_pipe_log_one_scorer_postfit_refit_str_fit_on_np


        # use this to reset the params to original state between tests and
        # at the end
        original_no_pipe_params = deepcopy(_GSTCV.get_params(deep=True))
        original_pipe_shallow_params = deepcopy(_GSTCV_PIPE.get_params(deep=False))
        original_pipe_deep_params = deepcopy(_GSTCV_PIPE.get_params(deep=True))


        # rejects_invalid_params ** * ** * ** * ** * ** * ** * ** * ** *
        # just check param names
        # invalid param names should be caught by set_params()
        # invalid param values should be caught at fit() by _validate()
        bad_params = sk_LinearRegression().get_params(deep=True)

        with pytest.raises(ValueError):
            _GSTCV.set_params(**bad_params)

        with pytest.raises(ValueError):
            _GSTCV_PIPE.set_params(**bad_params)
        # END rejects_invalid_params ** * ** * ** * ** * ** * ** * ** *


        # for shallow and deep no pipe / pipe, just take all the params
        # from itself and verify accepts everything; change some of the
        # params and assert new settings are correct

        # accepts_good_params_shallow_no_pipe ** * ** * ** * ** * ** *

        good_params_shallow_no_pipe = _GSTCV.get_params(deep=False)

        good_params_shallow_no_pipe['thresholds'] = [0.1, 0.5, 0.9]
        good_params_shallow_no_pipe['scoring'] = 'balanced_accuracy'
        good_params_shallow_no_pipe['n_jobs'] = 4
        good_params_shallow_no_pipe['cv'] = 8
        good_params_shallow_no_pipe['refit'] = False
        good_params_shallow_no_pipe['verbose'] = 10
        good_params_shallow_no_pipe['return_train_score'] = True

        _GSTCV.set_params(**good_params_shallow_no_pipe)

        get_params_shallow_no_pipe = _GSTCV.get_params(deep=False)

        assert get_params_shallow_no_pipe['thresholds'] == [0.1, 0.5, 0.9]
        assert get_params_shallow_no_pipe['scoring'] == 'balanced_accuracy'
        assert get_params_shallow_no_pipe['n_jobs'] == 4
        assert get_params_shallow_no_pipe['cv'] == 8
        assert get_params_shallow_no_pipe['refit'] is False
        assert get_params_shallow_no_pipe['verbose'] == 10
        assert get_params_shallow_no_pipe['return_train_score'] is True

        # END accepts_good_params_shallow_no_pipe ** * ** * ** * ** * **


        _GSTCV.set_params(**original_no_pipe_params)


        # accepts_good_params_deep_no_pipe ** * ** * ** * ** * ** * ** *

        good_params_deep_no_pipe = _GSTCV.get_params(deep=True)

        good_params_deep_no_pipe['estimator__tol'] = 1e-6
        good_params_deep_no_pipe['estimator__C'] = 1e-3
        good_params_deep_no_pipe['estimator__fit_intercept'] = False
        good_params_deep_no_pipe['estimator__solver'] = 'saga'
        good_params_deep_no_pipe['estimator__max_iter'] = 10_000
        good_params_deep_no_pipe['estimator__n_jobs'] = 8

        _GSTCV.set_params(**good_params_deep_no_pipe)

        get_params_deep_no_pipe = _GSTCV.get_params(deep=True)

        assert get_params_deep_no_pipe['estimator__tol'] == 1e-6
        assert get_params_deep_no_pipe['estimator__C'] == 1e-3
        assert get_params_deep_no_pipe['estimator__fit_intercept'] is False
        assert get_params_deep_no_pipe['estimator__solver'] == 'saga'
        assert get_params_deep_no_pipe['estimator__max_iter'] == 10_000
        assert get_params_deep_no_pipe['estimator__n_jobs'] == 8

        # END accepts_good_params_deep_no_pipe ** * ** * ** * ** * ** *


        _GSTCV.set_params(**original_no_pipe_params)


        # accepts_good_params_shallow_pipe ** * ** * ** * ** * ** * ** *

        good_params_pipe_shallow = _GSTCV_PIPE.get_params(deep=False)

        good_params_pipe_shallow['estimator'] = \
            Pipeline(steps=[('bag_of_words', sk_CountVectorizer()),
                            ('sk_logistic', sk_est_log)])
        good_params_pipe_shallow['param_grid'] = \
            {'C': [1e-6, 1e-5, 1e-4], 'solver': ['saga', 'lbfgs']}
        good_params_pipe_shallow['scoring'] = 'balanced_accuracy'
        good_params_pipe_shallow['n_jobs'] = 4
        good_params_pipe_shallow['cv'] = 5
        good_params_pipe_shallow['refit'] = False
        good_params_pipe_shallow['return_train_score'] = True

        _GSTCV_PIPE.set_params(**good_params_pipe_shallow)

        get_params_shallow_pipe = _GSTCV_PIPE.get_params(deep=False)

        assert isinstance(get_params_shallow_pipe['estimator'], Pipeline)
        assert isinstance(
            get_params_shallow_pipe['estimator'].steps[0][1],
            sk_CountVectorizer
        )
        assert isinstance(
            get_params_shallow_pipe['estimator'].steps[1][1],
            type(sk_est_log)
        )
        assert get_params_shallow_pipe['param_grid'] == \
               {'C': [1e-6, 1e-5, 1e-4], 'solver': ['saga', 'lbfgs']}
        assert get_params_shallow_pipe['scoring'] == 'balanced_accuracy'
        assert get_params_shallow_pipe['n_jobs'] == 4
        assert get_params_shallow_pipe['cv'] == 5
        assert get_params_shallow_pipe['refit'] is False
        assert get_params_shallow_pipe['return_train_score'] is True

        # END accepts_good_params_shallow_pipe ** * ** * ** * ** * ** *


        _GSTCV_PIPE.set_params(**original_pipe_shallow_params)
        _GSTCV_PIPE.set_params(**original_pipe_deep_params)


        # accepts_good_params_deep_pipe ** * ** * ** * ** * ** * ** * **

        good_params_pipe_deep = _GSTCV_PIPE.get_params(deep=True)

        good_params_pipe_deep['cv'] = 12
        good_params_pipe_deep['estimator__sk_StandardScaler__with_mean'] = True
        good_params_pipe_deep['estimator__sk_logistic__C'] = 1e-3
        good_params_pipe_deep['estimator__sk_logistic__max_iter'] = 10000
        good_params_pipe_deep['estimator__sk_logistic__n_jobs'] = None
        good_params_pipe_deep['n_jobs'] = 8
        good_params_pipe_deep['param_grid'] = {
            'sk_StandardScaler__with_std': [True, False],
            'sk_logistic__C': [0.0001, 0.001, 0.01]
        }
        good_params_pipe_deep['refit'] = False
        good_params_pipe_deep['return_train_score'] = True
        good_params_pipe_deep['scoring'] = 'balanced_accuracy'
        good_params_pipe_deep['verbose'] = 10

        _GSTCV_PIPE.set_params(**good_params_pipe_deep)

        get_params_deep_pipe = _GSTCV_PIPE.get_params(deep=True)

        assert get_params_deep_pipe['cv'] == 12
        assert get_params_deep_pipe['estimator__steps'][0][0] == 'sk_StandardScaler'
        assert get_params_deep_pipe['estimator__steps'][0][1].with_mean is True
        assert get_params_deep_pipe['estimator__steps'][1][0] == 'sk_logistic'
        assert get_params_deep_pipe['estimator__steps'][1][1].C == 1e-3
        assert get_params_deep_pipe['estimator__steps'][1][1].max_iter == 10000
        assert get_params_deep_pipe['estimator__steps'][1][1].n_jobs == None
        assert get_params_deep_pipe['n_jobs'] == 8
        assert get_params_deep_pipe['param_grid'] == {
            'sk_StandardScaler__with_std': [True, False],
            'sk_logistic__C': [0.0001, 0.001, 0.01]
        }
        assert get_params_deep_pipe['refit'] is False
        assert get_params_deep_pipe['return_train_score'] is True
        assert get_params_deep_pipe['scoring'] == 'balanced_accuracy'
        assert get_params_deep_pipe['verbose'] == 10

        # END accepts_good_params_deep_pipe ** * ** * ** * ** * ** * **


        _GSTCV_PIPE.set_params(**original_pipe_shallow_params)
        _GSTCV_PIPE.set_params(**original_pipe_deep_params)








