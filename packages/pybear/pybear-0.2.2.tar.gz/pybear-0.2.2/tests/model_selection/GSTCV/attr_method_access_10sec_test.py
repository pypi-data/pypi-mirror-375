# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
from sklearn.utils.validation import check_is_fitted



class TestGSTCVAttrs:


    # pre-fit, all attrs should not be available and should except


    @pytest.mark.parametrize('_scoring',
        (['accuracy'], ['accuracy', 'balanced_accuracy'])
    )
    @pytest.mark.parametrize('attr',
        ('cv_results_', 'best_estimator_', 'best_index_', 'scorer_',
         'n_splits_', 'refit_time_', 'multimetric_', 'feature_names_in_',
         'best_threshold_', 'best_score_', 'best_params_', 'classes_',
         'n_features_in_')
    )
    def test_prefit(
        self, attr, _scoring,
        sk_GSTCV_est_log_one_scorer_prefit,
        sk_GSTCV_est_log_two_scorers_prefit
    ):

        if _scoring == ['accuracy']:
            sk_GSTCV_prefit = sk_GSTCV_est_log_one_scorer_prefit

        elif _scoring == ['accuracy', 'balanced_accuracy']:
            sk_GSTCV_prefit = sk_GSTCV_est_log_two_scorers_prefit


        with pytest.raises(AttributeError):
            getattr(sk_GSTCV_prefit, attr)


    @pytest.mark.parametrize('_format', ('np', 'pd'))
    @pytest.mark.parametrize('_scoring',
        (['accuracy'], ['accuracy', 'balanced_accuracy'])
    )
    @pytest.mark.parametrize('_refit',(False, 'accuracy', lambda x: 0))
    def test_postfit(self, _refit, _format, _scoring, param_grid_sk_log,
        sk_est_log, standard_cv_int,
        X_np, X_pd, y_np, y_pd, _cols, COLUMNS,
        sk_GSTCV_est_log_one_scorer_postfit_refit_false_fit_on_np,
        sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_np,
        sk_GSTCV_est_log_one_scorer_postfit_refit_fxn_fit_on_np,
        sk_GSTCV_est_log_two_scorers_postfit_refit_false_fit_on_np,
        sk_GSTCV_est_log_two_scorers_postfit_refit_str_fit_on_np,
        sk_GSTCV_est_log_two_scorers_postfit_refit_fxn_fit_on_np,
        sk_GSTCV_est_log_one_scorer_postfit_refit_false_fit_on_pd,
        sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_pd,
        sk_GSTCV_est_log_one_scorer_postfit_refit_fxn_fit_on_pd,
        sk_GSTCV_est_log_two_scorers_postfit_refit_false_fit_on_pd,
        sk_GSTCV_est_log_two_scorers_postfit_refit_str_fit_on_pd,
        sk_GSTCV_est_log_two_scorers_postfit_refit_fxn_fit_on_pd
    ):

        # post-fit, all attrs should or should not be available based on
        # whether data was passed as DF, refit is callable, etc. Lots of
        # ifs, ands, and buts.

        if _format == 'np' and _scoring == ['accuracy']:
            if _refit is False:
                _sk_GSTCV = sk_GSTCV_est_log_one_scorer_postfit_refit_false_fit_on_np
            elif _refit == 'accuracy':
                _sk_GSTCV = sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_np
            elif callable(_refit):
                _sk_GSTCV = sk_GSTCV_est_log_one_scorer_postfit_refit_fxn_fit_on_np
        elif _format == 'np' and _scoring == ['accuracy', 'balanced_accuracy']:
            if _refit is False:
                _sk_GSTCV = sk_GSTCV_est_log_two_scorers_postfit_refit_false_fit_on_np
            elif _refit == 'accuracy':
                _sk_GSTCV = sk_GSTCV_est_log_two_scorers_postfit_refit_str_fit_on_np
            elif callable(_refit):
                _sk_GSTCV = sk_GSTCV_est_log_two_scorers_postfit_refit_fxn_fit_on_np
        elif _format == 'pd' and _scoring == ['accuracy']:
            if _refit is False:
                _sk_GSTCV = sk_GSTCV_est_log_one_scorer_postfit_refit_false_fit_on_pd
            elif _refit == 'accuracy':
                _sk_GSTCV = sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_pd
            elif callable(_refit):
                _sk_GSTCV = sk_GSTCV_est_log_one_scorer_postfit_refit_fxn_fit_on_pd
        elif _format == 'pd' and _scoring == ['accuracy', 'balanced_accuracy']:
            if _refit is False:
                _sk_GSTCV = sk_GSTCV_est_log_two_scorers_postfit_refit_false_fit_on_pd
            elif _refit == 'accuracy':
                _sk_GSTCV = sk_GSTCV_est_log_two_scorers_postfit_refit_str_fit_on_pd
            elif callable(_refit):
                _sk_GSTCV = sk_GSTCV_est_log_two_scorers_postfit_refit_fxn_fit_on_pd
        else:
            raise Exception

        # 1a) ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        # these are returned no matter what data format is passed or what
        # refit is set to or how many metrics are used ** * ** * ** * **

        # cv_results_
        __ = getattr(_sk_GSTCV, 'cv_results_')
        assert isinstance(__, dict)  # cv_results is dict
        assert all(map(isinstance, __.keys(), (str for _ in __))) # keys are str
        for _ in __.values():   # values are np masked or np array
            assert isinstance(_, (np.ma.masked_array, np.ndarray))
        assert len(__[list(__)[0]]) == 2  # number of permutations

        # scorer_
        __ = getattr(_sk_GSTCV, 'scorer_')
        assert isinstance(__, dict)   # scorer_ is dict
        assert len(__) == len(_scoring)  # len dict same as len passed
        assert all(map(isinstance, __.keys(), (str for _ in __))) # keys are str
        assert all(map(callable, __.values()))  # keys are callable (sk metrics)

        # n_splits_
        assert getattr(_sk_GSTCV, 'n_splits_') == standard_cv_int

        # multimetric_ false if 1 scorer, true if 2+ scorers
        assert getattr(_sk_GSTCV, 'multimetric_') is bool(len(_scoring) > 1)

        # END 1a) ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # 1b) ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        # when there is only one scorer these are returned no matter what
        # data format is passed or what refit is set to but when there
        # is more than one scorer, they are only exposed when refit is
        # not False
        for attr in ('best_params_', 'best_index_'):
            if len(_sk_GSTCV.scorer_) == 1 or _refit is not False:
                __ = getattr(_sk_GSTCV, attr)
                if attr == 'best_params_':
                    assert isinstance(__, dict)  # best_params_ is dict
                    for param, best_value in __.items():
                        # all keys are in param_grid
                        assert param in param_grid_sk_log
                        # best value was in grid
                        assert best_value in param_grid_sk_log[param]
                elif attr == 'best_index_':
                    assert int(__) == __  # best_index is integer
                    if isinstance(_refit, str):
                        # if refit is str, returned index is rank 1 in cv_results
                        suffix = 'score' if len(_scoring) == 1 else f'{_refit}'
                        assert _sk_GSTCV.cv_results_[f'rank_test_{suffix}'][__] == 1
                    elif callable(_refit):
                        # if refit is callable, passing cv_results to it == best_idx
                        assert _sk_GSTCV._refit(_sk_GSTCV.cv_results_) == __
                else:
                    raise Exception
            else:
                with pytest.raises(AttributeError):
                    getattr(_sk_GSTCV, attr)

        # END 1b) ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


        # 2a)
        # otherwise these always give attr error when refit is False **
        if _refit is False:
            for attr in (
                'best_estimator_', 'refit_time_', 'classes_',
                'n_features_in_', 'feature_names_in_'
            ):
                with pytest.raises(AttributeError):
                    getattr(_sk_GSTCV, attr)
        # END 2a) ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # 2b) best_score_ with refit=False: available when there is one
        # scorer, unavailable with multiple ** * ** * ** * ** * ** * **
            if len(_sk_GSTCV.scorer_) == 1:
                assert 0 <= getattr(_sk_GSTCV, 'best_score_') <= 1
            else:
                with pytest.raises(AttributeError):
                    getattr(_sk_GSTCV, attr)
        # END 2b) ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


        # 3)
        # otherwise, refit is not false and these always return numbers, class
        # instances, or dicts that can use 'isinstance' or '==' ** * ** *

        elif _refit == 'balanced_accuracy' or callable(_refit):

            __ = getattr(_sk_GSTCV, 'best_estimator_')
            assert isinstance(__, type(sk_est_log))  # same class as given estimator
            assert check_is_fitted(__) is None  # is fitted; otherwise cif raises

            og_params = _sk_GSTCV.estimator.get_params(deep=True)

            for param, value in __.get_params(deep=True).items():
                # if param from best_estimator_.get_params is not in best_params_,
                # it should be equal to the value given in the originally-
                # passed estimator
                if param not in _sk_GSTCV.best_params_:
                    if value is np.nan:
                        assert og_params[param] is np.nan
                    else:
                        assert value == og_params[param]
                # if the best_estimator_.param is in best_params_, the value
                # for best_estimator_ should equal the value in best_params_
                elif param in _sk_GSTCV.best_params_:
                    if value is np.nan:
                        assert _sk_GSTCV.best_params_[param] is np.nan
                    else:
                        assert value == _sk_GSTCV.best_params_[param]

            __ = getattr(_sk_GSTCV, 'refit_time_')
            assert isinstance(__, float)
            assert __ > 0

            assert getattr(_sk_GSTCV, 'n_features_in_') == _cols
        # END otherwise, refit is not false and these always return numbers,
        # class instances, or dicts that can use 'isinstance' or '==' ** * ** *

        # 4a)
        # when refit not False, data format is anything, returns array-like ** *
            __ = getattr(_sk_GSTCV, 'classes_')
            assert isinstance(__, np.ndarray)
            assert np.array_equiv(sorted(__), sorted(np.unique(y_np)))
        # END when refit not False, data format is anything, returns array-like ** *

        # 4b)
        # when refit not False, and it matters what the data format is,
        # returns array-like that needs np.array_equiv ** * ** * ** * **
            # feature_names_in_ gives AttrErr when X was array
            if _format == 'np':
                with pytest.raises(AttributeError):
                    getattr(_sk_GSTCV, 'feature_names_in_')
            # feature_names_in_ gives np vector when X was DF
            elif _format == 'pd':
                __ = getattr(_sk_GSTCV, 'feature_names_in_')
                assert isinstance(__, np.ndarray)
                assert np.array_equiv(__, COLUMNS)

        # END when refit not False, and it matters what the data format is,
        # returns array-like that needs np.array_equiv ** * ** * ** * **

        # best_score_. this one is crazy.
        # 5a) ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        # when refit is not False and not a callable, no matter how many
        # scorers there are, sk_GSCV and GSTCV return a numeric best_score_.
            if isinstance(_refit, str):
                __ = getattr(_sk_GSTCV, 'best_score_')
                assert isinstance(__, float)
                assert 0 <= __ <= 1

                col = f'mean_test_' + ('score' if len(_scoring) == 1 else _refit)
                assert __ == _sk_GSTCV.cv_results_[col][_sk_GSTCV.best_index_]

        # END 5a ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # 5b) ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        # GSTCV: when _refit is a callable, if there is only one scorer,
        # GSTCV returns a numeric best_score_
            elif callable(_refit):
                if len(_sk_GSTCV.scorer_) == 1:
                    __ = getattr(_sk_GSTCV, 'best_score_')
                    assert isinstance(__, float)
                    assert 0 <= __ <= 1

                    col = f'mean_test_' + ('score' if len(_scoring) == 1 else _refit)
                    assert __ == _sk_GSTCV.cv_results_[col][_sk_GSTCV.best_index_]
        # END 5b) ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # 5c) ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        # GSTCV: when refit is a callable, if there is more than one
        # scorer, GSTCV raises AttErr
                else:
                    with pytest.raises(AttributeError):
                        getattr(_sk_GSTCV, 'best_score_')
        # END 5c) ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

            else:
                raise Exception(f"unexpected refit '{_refit}'")

        # 6) ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        # GSTCV: best_threshold_ is available whenever there is only one
        #   scorer. when multiple scorers, best_threshold_ is only available
        #   when refit is str.

        if len(_sk_GSTCV.scorer_) == 1:
            __ = getattr(_sk_GSTCV, 'best_threshold_')
            assert isinstance(__, float)
            assert 0 <= __ <= 1
            _best_idx = _sk_GSTCV.best_index_
            assert _sk_GSTCV.cv_results_[f'best_threshold'][_best_idx] == __
        elif isinstance(_refit, str):
            __ = getattr(_sk_GSTCV, 'best_threshold_')
            assert isinstance(__, float)
            assert 0 <= __ <= 1
            _best_thr = \
                lambda col: _sk_GSTCV.cv_results_[col][_sk_GSTCV.best_index_]
            if len(_scoring) == 1:
                assert _best_thr(f'best_threshold') == __
            elif len(_scoring) > 1:
                assert _best_thr(f'best_threshold_{_refit}') == __
        else:
            with pytest.raises(AttributeError):
                getattr(_sk_GSTCV, 'best_threshold_')

        # END 6) ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *




class TestGSTCVMethods:

    # methods & signatures (besides fit)
    # --------------------------
    # decision_function(X)
    # inverse_transform(Xt)
    # predict(X)
    # predict_log_proba(X)
    # predict_proba(X)
    # score(X, y=None, **params)
    # score_samples(X)
    # transform(X)
    # visualize(filename=None, format=None)



    # '_refit' mark must have False last! set_params(refit=xxx) is mutating
    # session fixtures. we need to leave the session fixtures at the starting
    # value for 'refit' in the 'sk_gscv_init_params', which is False.
    @pytest.mark.parametrize('_scoring',
        (['accuracy'], ['accuracy', 'balanced_accuracy'])
    )
    @pytest.mark.parametrize('_refit', ('accuracy', lambda x: 0, False))
    def test_prefit(
        self, _refit, _scoring, X_np, y_np, sk_GSTCV_est_log_one_scorer_prefit,
        sk_GSTCV_est_log_two_scorers_prefit,
    ):

        if _scoring == ['accuracy']:
            _GSTCV = sk_GSTCV_est_log_one_scorer_prefit

        elif _scoring == ['accuracy', 'balanced_accuracy']:
            _GSTCV = sk_GSTCV_est_log_two_scorers_prefit


        _GSTCV.set_params(refit=_refit)


        for _attr in (
            'decision_function', 'inverse_transform', 'predict', 'transform',
            'predict_log_proba', 'predict_proba', 'score_samples'
        ):
            with pytest.raises(AttributeError):
                    getattr(_GSTCV, _attr)(X_np)


        # get_metadata_routing
        with pytest.raises(NotImplementedError):
            getattr(_GSTCV, 'get_metadata_routing')()


        # score
        with pytest.raises(AttributeError):
            getattr(_GSTCV, 'score')(X_np, y_np)


        # visualize
        with pytest.raises(AttributeError):
            getattr(_GSTCV, 'visualize')(filename=None, format=None)


    @pytest.mark.parametrize('_scoring',
        (['accuracy'], ['accuracy', 'balanced_accuracy'])
    )
    @pytest.mark.parametrize('_refit', ('accuracy', lambda x: 0, False))
    def test_postfit(
        self, _refit, _scoring, X_np, y_np,
        sk_GSTCV_est_log_one_scorer_postfit_refit_false_fit_on_np,
        sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_np,
        sk_GSTCV_est_log_one_scorer_postfit_refit_fxn_fit_on_np,
        sk_GSTCV_est_log_two_scorers_postfit_refit_false_fit_on_np,
        sk_GSTCV_est_log_two_scorers_postfit_refit_str_fit_on_np,
        sk_GSTCV_est_log_two_scorers_postfit_refit_fxn_fit_on_np
    ):

        # these can only be exposed if refit is not False

        if _scoring == ['accuracy']:
            if _refit is False:
                GSTCV = sk_GSTCV_est_log_one_scorer_postfit_refit_false_fit_on_np
            elif _refit == 'accuracy':
                GSTCV = sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_np
            elif callable(_refit):
                GSTCV = sk_GSTCV_est_log_one_scorer_postfit_refit_fxn_fit_on_np
        elif _scoring == ['accuracy', 'balanced_accuracy']:
            if _refit is False:
                GSTCV = sk_GSTCV_est_log_two_scorers_postfit_refit_false_fit_on_np
            elif _refit == 'accuracy':
                GSTCV = sk_GSTCV_est_log_two_scorers_postfit_refit_str_fit_on_np
            elif callable(_refit):
                GSTCV = sk_GSTCV_est_log_two_scorers_postfit_refit_fxn_fit_on_np


        # get_metadata_routing
        with pytest.raises(NotImplementedError):
            getattr(GSTCV, 'get_metadata_routing')()


        # predict
        if _refit is False:
            with pytest.raises(AttributeError):
                getattr(GSTCV, 'predict')(X_np)
        elif _refit == 'accuracy':
            __ = getattr(GSTCV, 'predict')(X_np)
            assert isinstance(__, np.ndarray)
            assert __.dtype == np.uint8
        elif callable(_refit):
            # this is to accommodate lack of threshold when > 1 scorer
            if isinstance(_scoring, list) and len(_scoring) > 1:
                with pytest.raises(AttributeError):
                    getattr(GSTCV, 'predict')(X_np)
            else:
                __ = getattr(GSTCV, 'predict')(X_np)
                assert isinstance(__, np.ndarray)
                assert __.dtype == np.uint8


        # decision_function, predict_log_proba, predict_proba
        for _attr in ('decision_function', 'predict_log_proba', 'predict_proba'):
            if _refit is False:
                with pytest.raises(AttributeError):
                    getattr(GSTCV, _attr)(X_np)
            elif _refit == 'accuracy' or callable(_refit):
                __ = getattr(GSTCV, _attr)(X_np)
                assert isinstance(__, np.ndarray)
                assert __.dtype == np.float64


        # score
        if _refit is False:
            with pytest.raises(AttributeError):
                getattr(GSTCV, 'score')(X_np, y_np)
        elif _refit == 'accuracy':
            __ = getattr(GSTCV, 'score')(X_np, y_np)
            assert isinstance(__, float)
            assert 0 <= __ <= 1
        elif callable(_refit):
            __ = getattr(GSTCV, 'score')(X_np, y_np)
            if not isinstance(_scoring, list) or len(_scoring) == 1:
                # if resfit fxn & one scorer, score is always returned
                assert isinstance(__, float)
                assert 0 <= __ <= 1
            else:
                # if refit fxn & >1 scorer, refit fxn is returned
                assert callable(__)
                cvr = GSTCV.cv_results_
                assert isinstance(__(cvr), int) # refit(cvr) returns best_index_
                # best_index_ must be in range of the rows in cvr
                assert 0 <= __(cvr) < len(cvr[list(cvr)[0]])


        # inverse_transform, score_samples, transform
        for _attr in ('inverse_transform', 'score_samples', 'transform'):
            with pytest.raises(AttributeError):
                getattr(GSTCV, _attr)(X_np)


        # visualize
        with pytest.raises(AttributeError):
            getattr(GSTCV, 'visualize')(filename=None, format=None)





