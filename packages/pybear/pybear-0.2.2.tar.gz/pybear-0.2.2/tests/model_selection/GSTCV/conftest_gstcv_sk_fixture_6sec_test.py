# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from sklearn.model_selection import GridSearchCV as sk_GridSearchCV
from sklearn.pipeline import Pipeline as sk_Pipeline
from pybear.model_selection.GSTCV._GSTCV.GSTCV import GSTCV as sk_GSTCV



class TestSKGridSearchFixtures:


    def test_single_estimators(self,
        sk_est_log,
        sk_GSCV_est_log_one_scorer_prefit,
        sk_GSCV_est_log_one_scorer_postfit_refit_false,
        sk_GSCV_est_log_one_scorer_postfit_refit_str,
        sk_GSTCV_est_log_one_scorer_prefit,
        sk_GSTCV_est_log_one_scorer_postfit_refit_false_fit_on_np,
        sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_np,
        sk_GSTCV_est_log_one_scorer_postfit_refit_fxn_fit_on_np,
        sk_GSTCV_est_log_one_scorer_postfit_refit_false_fit_on_pd,
        sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_pd,
        sk_GSTCV_est_log_one_scorer_postfit_refit_fxn_fit_on_pd,
        sk_GSTCV_est_log_two_scorers_prefit,
        sk_GSTCV_est_log_two_scorers_postfit_refit_false_fit_on_np,
        sk_GSTCV_est_log_two_scorers_postfit_refit_str_fit_on_np,
        sk_GSTCV_est_log_two_scorers_postfit_refit_fxn_fit_on_np,
        sk_GSTCV_est_log_two_scorers_postfit_refit_false_fit_on_pd,
        sk_GSTCV_est_log_two_scorers_postfit_refit_str_fit_on_pd,
        sk_GSTCV_est_log_two_scorers_postfit_refit_fxn_fit_on_pd,
    ):

        name_gscv_tuples = [
            (f'sk_GSCV_est_log_one_scorer_prefit',
             sk_GSCV_est_log_one_scorer_prefit),
            (f'sk_GSCV_est_log_one_scorer_postfit_refit_false',
             sk_GSCV_est_log_one_scorer_postfit_refit_false),
            (f'sk_GSCV_est_log_one_scorer_postfit_refit_str',
             sk_GSCV_est_log_one_scorer_postfit_refit_str),
            (f'sk_GSTCV_est_log_one_scorer_prefit',
             sk_GSTCV_est_log_one_scorer_prefit),
            (f'sk_GSTCV_est_log_one_scorer_postfit_refit_false_fit_on_np',
             sk_GSTCV_est_log_one_scorer_postfit_refit_false_fit_on_np),
            (f'sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_np',
             sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_np),
            (f'sk_GSTCV_est_log_one_scorer_postfit_refit_fxn_fit_on_np',
             sk_GSTCV_est_log_one_scorer_postfit_refit_fxn_fit_on_np),
            (f'sk_GSTCV_est_log_one_scorer_postfit_refit_false_fit_on_pd',
             sk_GSTCV_est_log_one_scorer_postfit_refit_false_fit_on_pd),
            (f'sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_pd',
             sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_pd),
            (f'sk_GSTCV_est_log_one_scorer_postfit_refit_fxn_fit_on_pd',
             sk_GSTCV_est_log_one_scorer_postfit_refit_fxn_fit_on_pd),
            (f'sk_GSTCV_est_log_two_scorers_prefit',
             sk_GSTCV_est_log_two_scorers_prefit),
            (f'sk_GSTCV_est_log_two_scorers_postfit_refit_false_fit_on_np',
             sk_GSTCV_est_log_two_scorers_postfit_refit_false_fit_on_np),
            (f'sk_GSTCV_est_log_two_scorers_postfit_refit_str_fit_on_np',
             sk_GSTCV_est_log_two_scorers_postfit_refit_str_fit_on_np),
            (f'sk_GSTCV_est_log_two_scorers_postfit_refit_fxn_fit_on_np',
             sk_GSTCV_est_log_two_scorers_postfit_refit_fxn_fit_on_np),
            (f'sk_GSTCV_est_log_two_scorers_postfit_refit_false_fit_on_pd',
             sk_GSTCV_est_log_two_scorers_postfit_refit_false_fit_on_pd),
            (f'sk_GSTCV_est_log_two_scorers_postfit_refit_str_fit_on_pd',
             sk_GSTCV_est_log_two_scorers_postfit_refit_str_fit_on_pd),
            (f'sk_GSTCV_est_log_two_scorers_postfit_refit_fxn_fit_on_pd',
             sk_GSTCV_est_log_two_scorers_postfit_refit_fxn_fit_on_pd)
        ]

        for idx, (_name, _gscv_or_gstcv) in enumerate(name_gscv_tuples):

            __ = _gscv_or_gstcv

            if 'GSCV' in _name:
                assert isinstance(__, sk_GridSearchCV)
            elif 'GSTCV' in _name:
                assert isinstance(__, sk_GSTCV)

            _est = getattr(__, 'estimator')

            assert isinstance(_est, type(sk_est_log))

            _scoring = getattr(__, 'scoring')
            if 'one_scorer' in _name:
                assert isinstance(_scoring, str) or len(_scoring) == 1
            elif 'two_scorers' in _name:
                assert len(_scoring) == 2

            _refit = getattr(__, 'refit')
            if 'prefit' in _name:
                assert _refit is False
            elif 'postfit_refit_false' in _name:
                assert _refit is False
            elif 'postfit_refit_str' in _name:
                assert isinstance(_refit, str)
            elif 'postfit_refit_fxn' in _name:
                assert callable(_refit)
            else:
                raise Exception(f"invalid fixture name '{_name}'")


            if 'prefit' in _name:
                assert not hasattr(__, 'scorer_')

            elif 'postfit' in _name:
                assert hasattr(__, 'scorer_')

                if 'refit_false' in _name:
                    assert not hasattr(__, 'best_estimator_')
                elif 'refit_str' in _name or 'refit_fxn' in _name:
                    assert hasattr(__, 'best_estimator_')


    def test_pipelines(self,
        sk_est_log,
        sk_standard_scaler,
        sk_GSCV_pipe_log_one_scorer_prefit,
        sk_GSCV_pipe_log_one_scorer_postfit_refit_false,
        sk_GSCV_pipe_log_one_scorer_postfit_refit_str,
        sk_GSTCV_pipe_log_one_scorer_prefit,
        sk_GSTCV_pipe_log_one_scorer_postfit_refit_false_fit_on_np,
        sk_GSTCV_pipe_log_one_scorer_postfit_refit_str_fit_on_np
    ):

        name_pipeline_tuples = [
            (f'sk_GSCV_pipe_log_one_scorer_prefit',
             sk_GSCV_pipe_log_one_scorer_prefit),
            (f'sk_GSCV_pipe_log_one_scorer_postfit_refit_false',
             sk_GSCV_pipe_log_one_scorer_postfit_refit_false),
            (f'sk_GSCV_pipe_log_one_scorer_postfit_refit_str',
             sk_GSCV_pipe_log_one_scorer_postfit_refit_str),
            (f'sk_GSTCV_pipe_log_one_scorer_prefit',
             sk_GSTCV_pipe_log_one_scorer_prefit),
            ('sk_GSTCV_pipe_log_one_scorer_postfit_refit_false_fit_on_np',
             sk_GSTCV_pipe_log_one_scorer_postfit_refit_false_fit_on_np),
            ('sk_GSTCV_pipe_log_one_scorer_postfit_refit_str_fit_on_np',
             sk_GSTCV_pipe_log_one_scorer_postfit_refit_str_fit_on_np)
        ]

        for idx, (_name, _gscv_or_gstcv) in enumerate(name_pipeline_tuples):

            __ = _gscv_or_gstcv

            if 'GSCV' in _name:
                isinstance(__, sk_GridSearchCV)
            elif 'GSTCV' in _name:
                isinstance(__, sk_GSTCV)

            _pipe = getattr(__, 'estimator')

            assert isinstance(_pipe, sk_Pipeline)

            assert _pipe.steps[0][0] == 'sk_StandardScaler'
            assert isinstance(_pipe.steps[0][1], type(sk_standard_scaler))

            assert _pipe.steps[1][0] == 'sk_logistic'
            assert isinstance(_pipe.steps[1][1], type(sk_est_log))

            _scoring = getattr(__, 'scoring')
            if 'one_scorer' in _name:
                assert isinstance(_scoring, str) or len(_scoring) == 1
            elif 'two_scorers' in _name:
                assert len(_scoring) == 2

            _refit = getattr(__, 'refit')
            if 'prefit' in _name:
                assert _refit is False
            elif 'postfit_refit_false' in _name:
                assert _refit is False
            elif 'postfit_refit_str' in _name:
                assert isinstance(_refit, str)
            elif 'postfit_refit_fxn' in _name:
                assert callable(_refit)
            else:
                raise Exception(f"invalid fixture name '{_name}'")


            if 'prefit' in _name:
                assert not hasattr(__, 'scorer_')

            elif 'postfit' in _name:
                assert hasattr(__, 'scorer_')

                if 'refit_false' in _name:
                    assert not hasattr(__, 'best_estimator_')
                elif 'refit_str' in _name or 'refit_fxn' in _name:
                    assert hasattr(__, 'best_estimator_')





