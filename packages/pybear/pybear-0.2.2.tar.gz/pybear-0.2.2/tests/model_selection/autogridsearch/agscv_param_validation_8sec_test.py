# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



# This test module checks agscv arg/kwarg validation at the highest
# level. this should only need to be tested on one arbitrary valid wrapped
# GSCV, because this validation is only for agscv-only params, which
# would be common to all wrapped GSCVs.


import pytest

import numpy as np



class TestAGSCVValidation:

    # estimator,
    # params: ParamsType,
    # total_passes: int = 5,
    # total_passes_is_hard: bool = False,
    # max_shifts: None | int = None,
    # agscv_verbose: bool = False,
    # **parent_gscv_kwargs


    # parent GSCV ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @pytest.mark.parametrize('non_class',
        (0, 1, 3.14, [1,2], (1,2), {1,2}, {'a':1}, 'junk', lambda x: x)
    )
    def test_rejects_anything_not_an_estimator(
        self, SKAutoGridSearch, sk_params_1, X_np, y_np, non_class
    ):
        # this is raised by the parent GSCV, let it raise whatever
        # the parent GSCV wont check inputs until u try to fit
        with pytest.raises(Exception):
            SKAutoGridSearch(
                estimator=non_class,
                params=sk_params_1
            ).fit(X_np, y_np)


    def test_invalid_estimator(self, SKAutoGridSearch, X_np, y_np):

        class weird_estimator:

            def __init__(cls, crazy_param):
                cls.crazy_param = crazy_param

            def train(cls):
                return cls

            def run(cls):
                return cls.crazy_param


        # this is raised by the parent GSCV, let it raise whatever
        # the parent GSCV wont check inputs until u try to fit
        with pytest.raises(Exception):
            SKAutoGridSearch(
                estimator=weird_estimator(crazy_param=float('inf')),
                params={'crazy_param': [[True, False], 2, 'fixed_bool']}
            ).fit(X_np, y_np)

        del weird_estimator


    def test_rejects_bad_sklearn_GSCV_kwargs(
        self, SKAutoGridSearch, sk_estimator_1, sk_params_1, X_np, y_np
    ):

        # this is raised by the parent GSCV, let it raise whatever
        # the parent GSCV wont check inputs until u try to fit
        with pytest.raises(Exception):
            SKAutoGridSearch(
                estimator=sk_estimator_1,
                params=sk_params_1,
                aaa=True,
                bbb=1.5
            ).fit(X_np, y_np)

    # END parent GSCV ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # params ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    @pytest.mark.parametrize('junk_params',
        (2, np.pi, False, None, [1,2], (1,2), {1,2}, min, lambda x: x, 'junk')
    )
    def test_rejects_junk_params(
        self, SKAutoGridSearch, sk_estimator_1, junk_params, X_np, y_np
    ):
        with pytest.raises(TypeError):
            SKAutoGridSearch(
                sk_estimator_1,
                junk_params
            ).fit(X_np, y_np)


    @pytest.mark.parametrize('bad_params',
        (
            {'a': ['more_junk']},
            {0: [1,2,3,4]},
            {'junk': [1, 2, 'what?!']},
            {'b': {1,2,3,4}},
            {'qqq': {'rrr': [[1,2,3], 3, 'fixed_string']}}
        )
    )
    def test_rejects_bad_params(
        self, SKAutoGridSearch, sk_estimator_1, bad_params, X_np, y_np
    ):
        # this would be raised by agscv or the estimator, let is raise
        # whatever
        with pytest.raises(Exception):
            SKAutoGridSearch(
                sk_estimator_1,
                bad_params
            ).fit(X_np, y_np)


    # cant have duplicate params because 'params' is a dict


    # END params ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # total_passes ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @pytest.mark.parametrize('junk_passes',
        (True, None, np.pi, 'junk', min, [1,], (1,), {1,2}, lambda x: x)
    )
    def test_rejects_junk_total_passes(
        self, junk_passes, SKAutoGridSearch, sk_estimator_1,
        sk_params_1, X_np, y_np
    ):
        with pytest.raises(TypeError):
            SKAutoGridSearch(
                sk_estimator_1,
                sk_params_1,
                total_passes=junk_passes
            ).fit(X_np, y_np)


    @pytest.mark.parametrize('bad_tp', (-1, 0))
    def test_rejects_bad_total_passes(
        self, bad_tp, SKAutoGridSearch, sk_estimator_1, sk_params_1, X_np, y_np
    ):
        with pytest.raises(ValueError):
            SKAutoGridSearch(
                sk_estimator_1,
                sk_params_1,
                total_passes=bad_tp
            ).fit(X_np, y_np)

    # END total_passes ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # tpih ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # must be bool
    @pytest.mark.parametrize('_tpih',
        (1, 2, np.pi, None, 'junk', min, [1,], (1,), {1,2}, lambda x: x)
    )
    def test_tpih_rejects_non_bool(
        self, _tpih, SKAutoGridSearch, sk_estimator_1, sk_params_1,
        X_np, y_np
    ):

        with pytest.raises(TypeError):
            SKAutoGridSearch(
                sk_estimator_1,
                sk_params_1,
                total_passes_is_hard=_tpih
            ).fit(X_np, y_np)

    # END tpih ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    # max_shifts ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('junk_max_shifts',
        (np.pi, 'junk', min, [1,], (1,), {1,2}, lambda x: x)
    )
    def test_rejects_junk_max_shifts(
        self, junk_max_shifts, SKAutoGridSearch, sk_estimator_1,
        sk_params_1, X_np, y_np
    ):
        with pytest.raises(TypeError):
            SKAutoGridSearch(
                sk_estimator_1,
                sk_params_1,
                max_shifts=junk_max_shifts
            ).fit(X_np, y_np)


    @pytest.mark.parametrize('bad_max_shifts', (-1, 0))
    def test_rejects_bad_max_shifts(
        self, bad_max_shifts, SKAutoGridSearch, sk_estimator_1,
        sk_params_1, X_np, y_np
    ):
        with pytest.raises(ValueError):
            SKAutoGridSearch(
                sk_estimator_1,
                sk_params_1,
                max_shifts=bad_max_shifts
            ).fit(X_np, y_np)

    # END max_shifts ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # agscv_verbose ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    # must be bool

    @pytest.mark.parametrize('_verbose',
        (1, 2, np.pi, None, 'junk', min, [1,], (1,), {1,2}, lambda x: x)
    )
    def test_verbose_rejects_non_bool(
        self, _verbose, SKAutoGridSearch, sk_estimator_1,
        sk_params_1, X_np, y_np
    ):

        with pytest.raises(TypeError):
            SKAutoGridSearch(
                sk_estimator_1,
                sk_params_1,
                agscv_verbose=_verbose
            ).fit(X_np, y_np)

    # END agscv_verbose ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    # good_tp must match good_sk_params
    # 5 is the default init for total_passes
    @pytest.mark.parametrize('agscv_verbose,good_max_shifts,tpih,good_tp',
        (
            (True, None, True, 5),
            (False, 3, False, 5)
        )
    )
    def test_accepts_good_everything(
        self, SKAutoGridSearch, sk_estimator_1, sk_params_1,
        X_np, y_np, agscv_verbose, good_max_shifts, tpih, good_tp,
    ):

        # sklearn_GSCV_kwargs, estimator, params, total_passes,
        # total_passes_is_hard, max_shifts, agscv_verbose

        # the parent GSCV wont check inputs until u try to fit
        _gscv = SKAutoGridSearch(
            estimator=sk_estimator_1,
            params=sk_params_1,
            total_passes=good_tp,
            total_passes_is_hard=tpih,
            max_shifts=good_max_shifts,
            agscv_verbose=agscv_verbose,
            scoring='accuracy',
            n_jobs=None,
            cv=3
        )

        _gscv.fit(X_np, y_np)


        assert _gscv.total_passes_is_hard is tpih
        if _gscv.total_passes_is_hard:
            assert _gscv.total_passes == good_tp
        elif not _gscv.total_passes_is_hard:
            assert _gscv.total_passes >= good_tp
        assert _gscv.max_shifts == good_max_shifts
        assert _gscv.agscv_verbose is agscv_verbose


class TestBoolInFixedIntegerFixedFloat:


    def test_bool_in_fixed_integer(
        self, SKAutoGridSearch, sk_estimator_1, X_np, y_np
    ):

        # must use this special param grid
        _params = {
            'C': [np.logspace(-4, 4, 3), [3, 3, 3], 'soft_float'],
            'fit_intercept': [[True, False], [2, 1, 1], 'fixed_integer']
        }

        with pytest.raises(TypeError):
            SKAutoGridSearch(
                sk_estimator_1,
                _params,
                total_passes=3,
                total_passes_is_hard=True,
                max_shifts=2,
                agscv_verbose=False
            ).fit(X_np, y_np)


    def test_bool_in_fixed_float(
        self, SKAutoGridSearch, sk_estimator_1, X_np, y_np
    ):

        # must use this special param grid
        _params = {
            'C': [np.logspace(-4, 4, 3), [3, 3, 3], 'soft_float'],
            'fit_intercept': [[True, False], [2, 1, 1], 'fixed_float']
        }

        with pytest.raises(TypeError):
            SKAutoGridSearch(
                sk_estimator_1,
                _params,
                total_passes=3,
                total_passes_is_hard=True,
                max_shifts=2,
                agscv_verbose=False
            ).fit(X_np, y_np)


class TestZeroAndNegativeGrid:


    def test_fixed_accepts_zero_and_negative(
        self, SKAutoGridSearch, mock_estimator, mock_estimator_params, X_np, y_np
    ):

        # should be allowed by agscv

        agscv = SKAutoGridSearch(
            estimator=mock_estimator,
            params=mock_estimator_params,
            total_passes=2,
            total_passes_is_hard=True,
            agscv_verbose=False
        )

        agscv.fit(X_np, y_np)


    @pytest.mark.parametrize('type1',
        ('soft_float', 'hard_float', 'soft_integer', 'hard_integer')
    )
    @pytest.mark.parametrize('type2',
        ('soft_float', 'hard_float', 'soft_integer', 'hard_integer')
    )
    def test_soft_hard_rejects_zero_and_negative(
        self, SKAutoGridSearch, mock_estimator, type1, type2, X_np, y_np
    ):

        # should be allowed by agscv at init, but raise at fit

        # must use this special param grid with negative values
        agscv = SKAutoGridSearch(
            estimator=mock_estimator,
            params={
                'param_a': [[-1e-6, -1e-5, -1e-4], 3, type1],
                'param_b': [[-1, 0, 1], 3, type2]
            },
            total_passes=2,
            total_passes_is_hard=True,
            agscv_verbose=False
        )

        with pytest.raises(ValueError):
            agscv.fit(X_np, y_np)







