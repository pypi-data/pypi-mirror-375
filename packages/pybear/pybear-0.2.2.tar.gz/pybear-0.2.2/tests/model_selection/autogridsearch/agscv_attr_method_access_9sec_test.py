# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numbers

from pybear.base._is_fitted import is_fitted



# this test should only need to be done on one arbitrary valid gscv to
# prove out access to agscv attrs and methods. that should be sufficient
# to show agscv does / does not expose them appropriately for any valid
# wrapped GSCV. tests for wrapped dask GSCVS (in particular those in
# pybear-dask) should not need to be tested again.


# FIXTURES ^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
class Fixtures:


    @staticmethod
    @pytest.fixture(scope='module')
    def _total_passes():
        return 3


    @staticmethod
    @pytest.fixture(scope='module')
    def TestCls(SKAutoGridSearch, sk_estimator_1, sk_params_1, _total_passes):

        return SKAutoGridSearch(
            estimator=sk_estimator_1,
            params=sk_params_1,
            total_passes=_total_passes,
            total_passes_is_hard=True,
            max_shifts=2,
            agscv_verbose=False
        )

# END fixtures ^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^



# ACCESS ATTR BEFORE AND AFTER FIT
class TestAttrAccessBeforeAndAfterFit(Fixtures):


    def test_attr_access_before_fit(self, TestCls):

        # BEFORE FIT ***************************************************

        _attrs = [
            'best_score_'
            'best_params_',
            'GRIDS_',
            'RESULTS_',
            'params_'
        ]

        # SHOULD GIVE AttributeError
        for attr in _attrs:
            with pytest.raises(AttributeError):
                getattr(TestCls, attr)

        # END BEFORE FIT ***********************************************


    def test_attr_access_after_fit(self, X_np, y_np, TestCls, _total_passes):

        # AFTER FIT ****************************************************

        TestCls.fit(X_np, y_np)

        # 'best_score_',
        # 'best_params_',
        # 'GRIDS_',
        # 'RESULTS_',
        # 'params_',

        # after fit, should have access to everything

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _best_score = getattr(TestCls, 'best_score_')
        assert isinstance(_best_score, numbers.Real)
        # setting of best_score_ is controlled by parent GSCV
        # would rather that this could not be set
        setattr(TestCls, 'best_score_', 1)
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _best_params = getattr(TestCls, 'best_params_')
        assert isinstance(_best_params, dict)
        assert len(_best_params) == 2
        assert isinstance(_best_params['C'], numbers.Real)
        assert isinstance(_best_params['fit_intercept'], bool)
        # setting of best_params_ is controlled by parent GSCV
        # would rather that this could not be set
        setattr(TestCls, 'best_params_', {})
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _GRIDS = getattr(TestCls, 'GRIDS_')
        assert isinstance(_GRIDS, dict)
        assert all(map(
            isinstance,
            _GRIDS.keys(),
            (numbers.Integral for _ in _GRIDS.keys())
        ))
        assert len(_GRIDS) == _total_passes
        assert isinstance(_GRIDS[_total_passes - 1]['C'], list)
        assert isinstance(_GRIDS[_total_passes - 1]['C'][0], numbers.Real)
        assert isinstance(_GRIDS[_total_passes - 1]['fit_intercept'], list)
        assert isinstance(_GRIDS[_total_passes - 1]['fit_intercept'][0], bool)
        # GRIDS_ cannot be set
        with pytest.raises(AttributeError):
            setattr(TestCls, 'GRIDS_', {})
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _RESULTS = getattr(TestCls, 'RESULTS_')
        assert isinstance(_RESULTS, dict)
        assert all(map(
            isinstance,
            _RESULTS.keys(),
            (numbers.Integral for _ in _RESULTS.keys())
        ))
        assert len(_RESULTS) == _total_passes
        assert isinstance(_RESULTS[_total_passes - 1]['C'], numbers.Real)
        assert isinstance(_RESULTS[_total_passes - 1]['fit_intercept'], bool)
        # RESULTS_ cannot be set
        with pytest.raises(AttributeError):
            setattr(TestCls, 'RESULTS_', {})
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _params = getattr(TestCls, 'params_')
        assert isinstance(_params, dict)
        assert len(_params) == len(TestCls.params)
        for _key, _value in _params.items():
            assert isinstance(_key, str)
            assert isinstance(_value[0], list)
            assert isinstance(_value[1], list)
            assert all(map(
                isinstance, _value[1], (numbers.Integral for i in _value[1])
            ))
            assert isinstance(_value[2], str)
        # params_ cannot be set
        with pytest.raises(AttributeError):
            setattr(TestCls, 'params_', {})
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # END AFTER FIT ************************************************


# END ACCESS ATTR BEFORE AND AFTER FIT


# ACCESS METHODS BEFORE AND AFTER FIT ***
class TestMethodAccessBeforeAndAfterFit(Fixtures):


    def test_access_methods_before_fit(self, X_np, y_np, TestCls):

        # **************************************************************
        # vvv BEFORE FIT vvv *******************************************

        # fit()
        assert not is_fitted(TestCls)
        assert isinstance(TestCls.fit(X_np, y_np), type(TestCls))
        assert is_fitted(TestCls)

        # get_params()
        out = TestCls.get_params(True)
        assert isinstance(out, dict)
        # the wrapper
        assert 'agscv_verbose' in out
        assert isinstance(out['agscv_verbose'], bool)
        # the parent
        assert 'n_jobs' in out
        assert isinstance(out['n_jobs'], (numbers.Integral, type(None)))

        # set_params()
        # the wrapper
        assert isinstance(
            TestCls.set_params(agscv_verbose=True), type(TestCls)
        )
        assert TestCls.agscv_verbose is True
        assert isinstance(
            TestCls.set_params(agscv_verbose=False), type(TestCls)
        )
        assert TestCls.agscv_verbose is False
        # the parent
        assert isinstance(
            TestCls.set_params(scoring='balanced_accuracy'), type(TestCls)
        )
        assert TestCls.scoring == 'balanced_accuracy'
        assert isinstance(TestCls.set_params(scoring='accuracy'), type(TestCls))
        assert TestCls.scoring == 'accuracy'

        # END ^^^ BEFORE FIT ^^^ ***************************************
        # **************************************************************


    def test_access_methods_after_fit(self, X_np, y_np, TestCls):

        # **************************************************************
        # vvv AFTER FIT vvv ********************************************

        FittedTestCls = TestCls

        # fit()
        assert isinstance(FittedTestCls.fit(X_np, y_np), type(TestCls))

        assert hasattr(FittedTestCls, 'GRIDS_')
        assert hasattr(FittedTestCls, 'RESULTS_')

        # get_params()
        out = FittedTestCls.get_params(True)
        # the wrapper
        assert 'total_passes_is_hard' in out
        assert isinstance(out['total_passes_is_hard'], bool)
        # the parent
        assert 'n_jobs' in out
        assert isinstance(out['n_jobs'], (numbers.Integral, type(None)))

        # set_params()
        # the wrapper
        assert isinstance(
            FittedTestCls.set_params(agscv_verbose=True), type(TestCls)
        )
        assert FittedTestCls.agscv_verbose is True
        assert isinstance(
            FittedTestCls.set_params(agscv_verbose=False), type(TestCls)
        )
        assert FittedTestCls.agscv_verbose is False
        # the parent
        assert isinstance(FittedTestCls.set_params(refit=True), type(TestCls))
        assert FittedTestCls.refit is True
        assert isinstance(FittedTestCls.set_params(refit=None), type(TestCls))
        assert FittedTestCls.refit is None

        del FittedTestCls

        # END ^^^ AFTER FIT ^^^ ****************************************
        # **************************************************************

# END ACCESS METHODS BEFORE AND AFTER FIT








