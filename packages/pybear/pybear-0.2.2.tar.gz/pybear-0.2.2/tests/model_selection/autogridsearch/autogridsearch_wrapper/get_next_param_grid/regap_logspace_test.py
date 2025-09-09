# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._regap_logspace import _regap_logspace



class TestRegapLogspace:


    @staticmethod
    @pytest.fixture
    def good_params():
        return {
            'a': [['a', 'b', 'c', 'd'], 3, 'fixed_string'],
            'b': [[1, 2, 3, 4], [4, 4, 4], 'fixed_integer'],
            'c': [[10, 20, 30, 40], [4, 4, 4], 'fixed_float'],
            'd': [[1, 100, 10000], [3, 3, 3], 'soft_integer'],
            'e': [[25, 50, 75], [3, 3, 3], 'soft_integer'],
            'f': [[0, 0.5, 1.0], [3, 3, 3], 'hard_float'],
            'g': [[0, 2, 4, 6], [4, 4, 4], 'hard_integer'],
            'h': [[1, 10, 100, 1000], [4, 4, 4], 'soft_float'],
            'i': [[20, 40, 60, 80], [4, 4, 4], 'soft_float'],
            'j': [[1e0, 1e4, 1e8, 1e12, 1e16], [5, 5, 5], 'soft_float'],
            'k': [[1e0, 1e2, 1e4, 1e6], [4, 4, 4], 'hard_integer'],
            'l': [[1e0, 1e4, 1e8, 1e12, 1e16], [5, 5, 5], 'hard_float']
        }


    @staticmethod
    @pytest.fixture
    def good_is_logspace():
        return {
            'a': False,
            'b': False,
            'c': False,
            'd': 2.0,
            'e': False,
            'f': False,
            'g': False,
            'h': 1.0,
            'i': False,
            'j': 4.0,
            'k': 2.0,
            'l': 4.0
        }


    @staticmethod
    @pytest.fixture
    def good_grids():
        return {
            0: {
                'a': ['a', 'b', 'c', 'd'],
                'b': [1, 2, 3, 4],
                'c': [10, 20, 30, 40],
                'd': [1, 100, 10000],
                'e': [25, 50, 75],
                'f': [0, 0.5, 1.0],
                'g': [0, 2, 4, 6],
                'h': [1, 10, 100, 1000],
                'i': [20, 40, 60, 80],
                'j': [1e0, 1e4, 1e8, 1e12, 1e16],
                'k': [1e0, 1e2, 1e4, 1e6],
                'l': [1e0, 1e4, 1e8, 1e12, 1e16],
            },
            1: {
                'a': ['a', 'b', 'c', 'd'],
                'b': [1, 2, 3, 4],
                'c': [10, 20, 30, 40],
                'd': [1, 100, 10000],
                'e': [25, 50, 75],
                'f': [0, 0.5, 1.0],
                'g': [0, 2, 4, 6],
                'h': [1, 10, 100, 1000],
                'i': [20, 40, 60, 80],
                'j': [1e0, 1e4, 1e8, 1e12, 1e16],
                'k': [1e0, 1e2, 1e4, 1e6],
                'l': [1e0, 1e4, 1e8, 1e12, 1e16],
            }
        }


    @staticmethod
    @pytest.fixture
    def best_params():
        return {
            'a': 'a',  # [0], 'fixed_string'
            'b': 2,  # [1], 'fixed_integer'
            'c': 20,  # [1], 'fixed_float'
            'd': 100,  # [1], 'soft_integer'
            'e': 50,  # [1], 'soft_integer'
            'f': 0.5,  # [1], 'hard_float'
            'g': 2,  # [1], 'hard_integer'
            'h': 100,  # [2], 'soft_float'
            'i': 40,  # [1], 'soft_float'
            'j': 1e16,  # [-1], 'soft_float'
            'k': 1e0,  # [0], 'hard_integer'
            'l': 1e16  # [0], 'hard_integer'
        }


    @staticmethod
    @pytest.fixture
    def new_params():
        return {
            'a': [['a', 'b', 'c', 'd'], 3, 'fixed_string'],
            'b': [[1, 2, 3, 4], [4, 4, 4], 'fixed_integer'],
            'c': [[10, 20, 30, 40], [4, 4, 4], 'fixed_float'],
            'd': [[1, 100, 10000], [3, 5, 3], 'soft_integer'],
            'e': [[25, 50, 75], [3, 3, 3], 'soft_integer'],
            'f': [[0, 0.5, 1.0], [3, 3, 3], 'hard_float'],
            'g': [[0, 2, 4, 6], [4, 4, 4], 'hard_integer'],
            'h': [[1, 10, 100, 1000], [4, 4, 4], 'soft_float'],
            'i': [[20, 40, 60, 80], [4, 4, 4], 'soft_float'],
            'j': [[1e0, 1e4, 1e8, 1e12, 1e16], [5, 9, 5], 'soft_float'],
            'k': [[1e0, 1e2, 1e4, 1e6], [4, 3, 4], 'hard_integer'],
            'l': [[1e0, 1e4, 1e8, 1e12, 1e16], [5, 5, 5], 'hard_float'],
        }


    @staticmethod
    @pytest.fixture
    def new_is_logspace():
        return {
            'a': False,
            'b': False,
            'c': False,
            'd': 1.0,
            'e': False,
            'f': False,
            'g': False,
            'h': 1.0,
            'i': False,
            'j': 1.0,
            'k': 1.0,
            'l': 1.0
        }


    @staticmethod
    @pytest.fixture
    def new_grids():
        return {
            0: {
                'a': ['a', 'b', 'c', 'd'],
                'b': [1, 2, 3, 4],
                'c': [10, 20, 30, 40],
                'd': [1, 100, 10000],
                'e': [25, 50, 75],
                'f': [0, 0.5, 1.0],
                'g': [0, 2, 4, 6],
                'h': [1, 10, 100, 1000],
                'i': [20, 40, 60, 80],
                'j': [1e0, 1e4, 1e8, 1e12, 1e16],
                'k': [1e0, 1e2, 1e4, 1e6],
                'l': [1e0, 1e4, 1e8, 1e12, 1e16],
            },
            1: {
                'a': ['a', 'b', 'c', 'd'],
                'b': [1, 2, 3, 4],
                'c': [10, 20, 30, 40],
                'd': [1e0, 1e1, 1e2, 1e3, 1e4],
                'e': [25, 50, 75],
                'f': [0, 0.5, 1.0],
                'g': [0, 2, 4, 6],
                'h': [1, 10, 100, 1000],
                'i': [20, 40, 60, 80],
                'j': [1e12, 1e13, 1e14, 1e15, 1e16, 1e17, 1e18, 1e19, 1e20],
                'k': [1e0, 1e1, 1e2],
                'l': [1e12, 1e13, 1e14, 1e15, 1e16],
            }
        }

    # END FIXTURES -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # no _validation

    @pytest.mark.parametrize('key', list('abdcdefghijkl'))
    def test_accuracy(
        self, good_grids, good_is_logspace, good_params, best_params,
        new_grids, new_is_logspace, new_params, key
    ):

        out_grid, out_param, out_is_logspace = \
            _regap_logspace(
                _param_name=key,
                _grid=good_grids[1][key],
                _is_logspace=good_is_logspace[key],
                _param_value=good_params[key],
                _pass=1,
                _best_param_from_previous_pass=best_params[key],
                _hard_min=good_grids[0][key][0],
                _hard_max=good_grids[0][key][-1]
            )

        assert out_grid == new_grids[1][key]
        assert out_param == new_params[key]
        assert out_is_logspace == new_is_logspace[key]







