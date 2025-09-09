# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler



class TestSKGetParams:


    @staticmethod
    @pytest.fixture(scope='module')
    def _base_params(
        sk_est_log, param_grid_sk_log, standard_thresholds,  standard_cv_int,
        standard_refit, one_scorer, standard_error_score, standard_n_jobs
    ):
        # remember we cant just use the init defaults because we are using
        # the specially init-ed instances from conftest
        return {
            'cv': standard_cv_int,
            'error_score': standard_error_score,
            'estimator': sk_est_log,
            'n_jobs': standard_n_jobs,
            'param_grid': param_grid_sk_log,
            'refit': standard_refit,
            'return_train_score': False,
            'scoring': one_scorer,
            'thresholds': standard_thresholds,
            'verbose': 0
        }


    @pytest.mark.parametrize('bad_deep',
        (0, 1, 3.14, None, 'trash', min, [0,1], (0,1), {'a':1}, lambda x: x)
    )
    def test_rejects_non_bool_deep(
        self, bad_deep,
        sk_GSTCV_est_log_one_scorer_prefit,
        sk_GSTCV_pipe_log_one_scorer_prefit
    ):

        _GSTCV = sk_GSTCV_est_log_one_scorer_prefit
        _GSTCV_PIPE = sk_GSTCV_pipe_log_one_scorer_prefit

        with pytest.raises(ValueError):
            _GSTCV.get_params(bad_deep)

        with pytest.raises(ValueError):
            _GSTCV_PIPE.get_params(bad_deep)


    @pytest.mark.parametrize('_state,_refit',
        (('prefit', False), ('postfit', 'accuracy'), ('postfit', False)),
        scope='class'
    )
    def test_simple_estimator(
        self, _state, _refit,
        sk_est_log,
        sk_GSTCV_est_log_one_scorer_prefit,
        sk_GSTCV_est_log_one_scorer_postfit_refit_false_fit_on_np,
        sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_np,
        _base_params
    ):

        # test shallow no pipe v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

        if _state == 'prefit':
            _GSTCV = sk_GSTCV_est_log_one_scorer_prefit
        elif _state == 'postfit':
            if _refit is False:
                _GSTCV = sk_GSTCV_est_log_one_scorer_postfit_refit_false_fit_on_np
            elif _refit == 'accuracy':
                _GSTCV = sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_np

        # SK SHALLOW ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        act_gstcv_shallow = _GSTCV.get_params(deep=False)

        # create expected output, tack on unique GSTCV params
        # dont need to reinvent GetParamsMixin tests, just show that exp
        # params are in GSTCV.get_params(deep=False)
        exp_gstcv_shallow = deepcopy(_base_params) | {'pre_dispatch': '2*n_jobs'}

        # same number of params
        assert len(exp_gstcv_shallow) == len(act_gstcv_shallow)

        # params are correct
        for _param in exp_gstcv_shallow:
            assert _param in act_gstcv_shallow

        # END SK SHALLOW ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        # END test shallow no pipe v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

        # test deep no pipe v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

        # SK DEEP ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        act_gstcv_deep = _GSTCV.get_params(deep=True)

        # create expected output, tack on unique GSTCV params, tack on est params
        # dont need to reinvent GetParamsMixin tests, just show that exp
        # params are in GSTCV.get_params(deep=True)
        exp_gstcv_deep = deepcopy(_base_params) | {'pre_dispatch': '2*n_jobs'} | {
            f'estimator__{k}': v for k, v in sk_est_log.get_params().items()
        }

        # same number of params
        assert len(exp_gstcv_deep) == len(act_gstcv_deep)

        # param values are correct
        for _param, _exp_value in exp_gstcv_deep.items():
            assert _param in act_gstcv_deep

        # END SK DEEP ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # END test deep no pipe v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v


    @pytest.mark.parametrize('_state,_refit',
        (('prefit', False), ('postfit', 'accuracy'), ('postfit', False)),
        scope='class'
    )
    def test_pipe(
        self, _state, _refit,
        sk_est_log,
        sk_GSTCV_pipe_log_one_scorer_prefit,
        sk_GSTCV_pipe_log_one_scorer_postfit_refit_false_fit_on_np,
        sk_GSTCV_pipe_log_one_scorer_postfit_refit_str_fit_on_np,
        _base_params
    ):

        # shallow pipe v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

        # SK ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        if _state == 'prefit':
            _GSTCV_PIPE = sk_GSTCV_pipe_log_one_scorer_prefit
        elif _state == 'postfit':
            if _refit is False:
                _GSTCV_PIPE = sk_GSTCV_pipe_log_one_scorer_postfit_refit_false_fit_on_np
            elif _refit == 'accuracy':
                _GSTCV_PIPE = sk_GSTCV_pipe_log_one_scorer_postfit_refit_str_fit_on_np


        assert _GSTCV_PIPE.estimator.steps[0][0] == 'sk_StandardScaler'
        assert _GSTCV_PIPE.estimator.steps[1][0] == 'sk_logistic'

        act_gstcv_shallow = _GSTCV_PIPE.get_params(deep=False)

        # create expected output, tack on unique GSTCV params
        # dont need to reinvent GetParamsMixin tests, just show that exp
        # params are in GSTCV.get_params(deep=False)
        exp_gstcv_shallow = deepcopy(_base_params) | {'pre_dispatch': '2*n_jobs'}

        # same number of params
        assert len(exp_gstcv_shallow) == len(act_gstcv_shallow)

        # params are correct
        for _param in exp_gstcv_shallow:
            assert _param in act_gstcv_shallow

        # END SK ** * ** * ** * ** * ** * ** * ** * ** * ** ** * ** * **

        # shallow pipe v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^


        # deep pipe v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

        # SK ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        assert _GSTCV_PIPE.estimator.steps[0][0] == 'sk_StandardScaler'
        assert _GSTCV_PIPE.estimator.steps[1][0] == 'sk_logistic'

        act_gstcv_deep = _GSTCV_PIPE.get_params(deep=True)

        # create expected output, tack on unique GSTCV params, tack on pipe
        # params, tack on est params
        # dont need to reinvent GetParamsMixin tests, just show that exp
        # params are in GSTCV.get_params(deep=True)
        exp_gstcv_deep = deepcopy(_base_params) | {'pre_dispatch': '2*n_jobs'}

        def _helper(thing_to_get_param_names_from, module_name: str):
            out = {f'estimator{module_name}': None}  # dont care about the value
            for k, v in thing_to_get_param_names_from.get_params().items():
                out |= {f'estimator{module_name}__{k}': v}
            return out

        exp_gstcv_deep |= _helper(Pipeline(steps=[]), '')
        exp_gstcv_deep |= _helper(StandardScaler(), '__sk_StandardScaler')
        exp_gstcv_deep |= _helper(sk_est_log, '__sk_logistic')

        # same number of params
        assert len(exp_gstcv_deep) == len(act_gstcv_deep)

        # param values are correct
        for _param, _exp_value in exp_gstcv_deep.items():
            assert _param in act_gstcv_deep

        # END SK ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # END deep pipe v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v





