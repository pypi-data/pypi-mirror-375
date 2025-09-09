# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.model_selection.autogridsearch._autogridsearch_wrapper._demo.\
    _mock_gscv import _mock_gscv



class TestMockGscv:


    @staticmethod
    @pytest.fixture
    def good_grids():
        return {
            0: {
                'a': ['x', 'y', 'z'],
                'b': [1, 2, 3, 4],
                'c': [20, 30, 40]
            },
            1: {
                'a': ['x', 'y', 'z'],
                'b': [1, 2, 3, 4],
                'c': [25, 30, 35]
            }
        }


    @staticmethod
    @pytest.fixture
    def good_params():
        return {
            'a': [['x', 'y', 'z'], [3, 3, 3], 'fixed_string'],
            'b': [[1, 2, 3, 4], [4, 4, 4], 'fixed_integer'],
            'c': [[25, 30, 35], [3, 3, 6], 'soft_float']
        }


    @staticmethod
    @pytest.fixture
    def good_true_best():
        return {
            'a': 'x',
            'b': 4,
            'c': 28.8205373
        }


    @staticmethod
    @pytest.fixture
    def _best_params_round_zero():
        return {}


    @staticmethod
    @pytest.fixture
    def _best_params_round_one():
        return {
            'a': 'x',
            'b': 4,
            'c': 30
        }

    # END fixtures -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    def test_accuracy_best_params(self, good_grids, good_params,
        good_true_best, _best_params_round_zero, _best_params_round_one):

        # 10% chance mock_gscv will give wrong best for str variable
        # (by design) run this 100 times see if it is wrong 10 +/- 10%
        # of the time

        _ct_wrong = 0
        for _ in range(100):

            _pass = 0

            _best_params_ = _mock_gscv(
                good_grids,
                good_params,
                good_true_best,
                _best_params_round_zero,
                _pass,
                _pause_time=0
            )

            try:
                assert _best_params_ == {'a': 'x', 'b': 4, 'c': 30}
            except:
                _ct_wrong += 1

        assert 0 < _ct_wrong < 20





        _ct_wrong = 0
        for _ in range(100):

            _pass = 1

            _best_params_ = _mock_gscv(
                good_grids,
                good_params,
                good_true_best,
                _best_params_round_one,
                _pass,
                _pause_time=0
            )

            try:
                assert _best_params_ == {'a': 'x', 'b': 4, 'c': 30}
            except:
                _ct_wrong += 1

        assert 0 < _ct_wrong < 20







