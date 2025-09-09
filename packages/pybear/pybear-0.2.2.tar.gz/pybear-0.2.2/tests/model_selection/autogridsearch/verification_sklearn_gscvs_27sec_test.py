# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



# This test module verifies that agscv works for all sklearn GSCV modules.



import pytest

from pybear.model_selection import autogridsearch_wrapper

from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import (
    GridSearchCV as SklearnGridSearchCV,
    RandomizedSearchCV as SklearnRandomizedSearchCV,
    HalvingGridSearchCV,
    HalvingRandomSearchCV
)



class TestSklearnGSCVS:

    #         estimator,
    #         params: ParamsType,
    #         total_passes: int = 5,
    #         total_passes_is_hard: bool = False,
    #         max_shifts: None | int = None,
    #         agscv_verbose: bool = False,
    #         **parent_gscv_kwargs


    @pytest.mark.parametrize('SKLEARN_GSCV',
        (
            SklearnGridSearchCV,
            SklearnRandomizedSearchCV,
            HalvingGridSearchCV,
            HalvingRandomSearchCV
        )
    )
    @pytest.mark.parametrize('_total_passes', (2, 3, 4))
    @pytest.mark.parametrize('_scorer',
        ('accuracy', ['accuracy', 'balanced_accuracy'])
    )
    @pytest.mark.parametrize('_tpih', (True, ))
    @pytest.mark.parametrize('_max_shifts', (2, ))
    @pytest.mark.parametrize('_refit', ('accuracy', False, lambda x: 0))
    def test_sklearn_gscvs(
        self, sk_estimator_1, sk_params_1, SKLEARN_GSCV, _total_passes, _scorer,
        _tpih, _max_shifts, _refit, X_np, y_np
    ):

        # the 'halving' grid searches cannot take multiple scorers
        if SKLEARN_GSCV in (HalvingGridSearchCV, HalvingRandomSearchCV) \
                and len(_scorer) > 1:
            pytest.skip(
                reason=f"the 'halving' grid searches cannot take multiple scorers"
            )

        AGSCV_params = {
            'estimator': sk_estimator_1,
            'params': sk_params_1,
            'total_passes': _total_passes,
            'total_passes_is_hard': _tpih,
            'max_shifts': _max_shifts,
            'agscv_verbose': False,
            'scoring': _scorer,
            'n_jobs': -1,    # -1 is fastest 25_04_18_10_00_00
            'cv': 4,
            'error_score': 'raise',
            'return_train_score': False,
            'refit': _refit,
            'pre_dispatch': '2*n_jobs',
            'verbose': 0
        }

        AutoGridSearch = autogridsearch_wrapper(SKLEARN_GSCV)(**AGSCV_params)

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
            AutoGridSearch.fit(X_np, y_np)
            assert isinstance(getattr(AutoGridSearch, 'best_params_'), dict)
        except ValueError:
            assert not hasattr(AutoGridSearch, 'best_params_')
            pytest.skip(reason=f'cant do any later tests without fit')
        except Exception as hell:
            raise hell

        # assertions ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        assert AutoGridSearch.total_passes >= _total_passes
        assert AutoGridSearch.total_passes_is_hard is _tpih
        assert AutoGridSearch.max_shifts == _max_shifts
        assert AutoGridSearch.agscv_verbose is False
        assert AutoGridSearch.scoring == _scorer
        assert AutoGridSearch.refit == _refit

        if _refit:
            assert isinstance(
                AutoGridSearch.best_estimator_, type(sk_estimator_1)
            )
        elif not _refit:
            with pytest.raises(AttributeError):
                AutoGridSearch.best_estimator_


        best_params_ = AutoGridSearch.best_params_
        assert isinstance(best_params_, dict)
        assert sorted(list(best_params_)) == sorted(list(sk_params_1))
        assert all(map(
            isinstance,
            best_params_.values(),
            ((int, float, bool, str) for _ in sk_params_1)
        ))

        # END assertions ** * ** * ** * ** * ** * ** * ** * ** * ** * **





