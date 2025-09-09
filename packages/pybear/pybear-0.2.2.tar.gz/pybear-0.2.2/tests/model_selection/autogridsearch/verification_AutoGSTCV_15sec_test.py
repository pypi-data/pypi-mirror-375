# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



# this module tests compatibility of autogridsearch_wrapper with GSTCV
# simply by running wrapped GSTCV to completion and asserting a few of
# the GSTCV attributes are exposed by the wrapper.



# demo_test incidentally handles testing of all autogridsearch_wrapper
# functionality except fit() (because demo bypasses fit().) This test
# module handles fit().



import pytest

import numpy as np

from pybear.model_selection.autogridsearch.AutoGSTCV import AutoGSTCV



class TestAutoGSTCV:

    #         estimator,
    #         params: ParamsType,
    #         total_passes: int = 5,
    #         total_passes_is_hard: bool = False,
    #         max_shifts: None | int = None,
    #         agscv_verbose: bool = False,
    #         **parent_gscv_kwargs


    def test_accepts_threshold_kwarg(self, mock_estimator):

        _thresholds = np.linspace(0, 1, 3)

        _agscv = AutoGSTCV(
            estimator=mock_estimator,
            params={},
            refit=False,
            thresholds=_thresholds
        )

        assert np.array_equiv(_agscv.thresholds, _thresholds)


    @pytest.mark.parametrize('_total_passes', (2, 3, 4))
    @pytest.mark.parametrize('_scorer',
        ('accuracy', ['accuracy', 'balanced_accuracy'])
    )
    @pytest.mark.parametrize('_tpih', (True, ))
    @pytest.mark.parametrize('_max_shifts', (2, ))
    @pytest.mark.parametrize('_refit', ('accuracy', False, lambda x: 0))
    def test_AGSTCV(self, mock_estimator, mock_estimator_params,
        _total_passes, _scorer, _tpih, _max_shifts, _refit, X_np, y_np
    ):

        AGSTCV_params = {
            'estimator': mock_estimator,
            'params': mock_estimator_params,
            'total_passes': _total_passes,
            'total_passes_is_hard': _tpih,
            'max_shifts': _max_shifts,
            'agscv_verbose': False,
            'thresholds': [0.4, 0.6],
            'scoring': _scorer,
            'n_jobs': 1,     # leave a 1, confliction
            'refit': _refit,
            'cv': 4,
            'verbose': 0,
            'pre_dispatch': '2*n_jobs',
            'error_score': 'raise',
            'return_train_score': False
        }


        AGSTCV = AutoGSTCV(**AGSTCV_params)

        # 25_04_19 changed fit() to raise ValueError when best_params_
        # is not exposed. it used to be that agscv code was shrink-wrapped
        # around sklearn gscv quirks as to when it does/doesnt expose
        # best_params_. there are no longer any bandaids that condition params
        # for the parent gscvs to get them to "properly" expose 'best_params_',
        # and there are no more predictive shrink-wraps to block failure.
        # The user is left to die by however the parent gscv handles the exact
        # params as given. what that means here is that we are not going to
        # coddle to every little nuanced thing that makes a gscv not want to
        # expose 'best_params_'. Try to fit, if ValueError is raised, look to
        # see that 'best_params_' is not exposed and go to the next test.
        try:
            AGSTCV.fit(X_np, y_np)
            assert isinstance(getattr(AGSTCV, 'best_params_'), dict)
        except ValueError:
            assert not hasattr(AGSTCV, 'best_params_')
            pytest.skip(reason=f'cant do any later tests without fit')
        except Exception as e:
            raise e

        # assertions ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        assert AGSTCV.total_passes >= _total_passes
        assert AGSTCV.total_passes_is_hard is _tpih
        assert AGSTCV.max_shifts == _max_shifts
        assert AGSTCV.agscv_verbose is False
        assert AGSTCV.scoring == _scorer
        assert AGSTCV.refit == _refit

        # cannot test MockEstimator for scoring or scorer_

        if _refit:
            assert isinstance(
                AGSTCV.best_estimator_,
                type(mock_estimator)
            )
        else:
            with pytest.raises(AttributeError):
                AGSTCV.best_estimator_


        best_params_ = AGSTCV.best_params_
        assert isinstance(best_params_, dict)
        assert sorted(list(best_params_)) == sorted(list(mock_estimator_params))
        assert all(map(
            isinstance,
            best_params_.values(),
            ((int, float, bool, str, np.int64) for _ in mock_estimator_params)
        ))

        # best_threshold_ should always be exposed with one scorer
        if isinstance(_refit, str) or callable(_scorer) or \
                isinstance(_scorer, str) or len(_scorer) == 1:
            best_threshold_ = AGSTCV.best_threshold_
            assert isinstance(best_threshold_, float)
            assert 0 <= best_threshold_ <= 1

        # END assertions ** * ** * ** * ** * ** * ** * ** * ** * ** * **







