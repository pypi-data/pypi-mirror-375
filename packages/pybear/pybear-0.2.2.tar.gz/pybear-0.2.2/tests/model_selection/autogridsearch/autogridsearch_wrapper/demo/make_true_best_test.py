# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.model_selection.autogridsearch._autogridsearch_wrapper._demo. \
    _make_true_best import _make_true_best



class TestMakeTrueBestParams:


    @staticmethod
    @pytest.fixture
    def good_params():
        return {
            'a': [['a', 'b', 'c'], 3, 'fixed_string'],
            'b': [[2.718, 3.1415, 8.834], [3, 3, 3], 'fixed_float'],
            'c': [[4, 5, 6], [3, 3, 3], 'fixed_integer'],
            'd': [[50, 100], [2, 3, 3], 'hard_float'],
            'e': [[4, 5, 6], [3, 3, 3], 'hard_integer'],
            'f': [[40, 50, 60], [3, 3, 3], 'hard_integer'],
            'g': [[1, 10, 100], [3, 3, 3], 'soft_float'],
            'h': [[40, 50, 60], [3, 3, 3], 'soft_float'],
            'i': [[4, 5, 6], [3, 3, 3], 'soft_integer'],
            'j': [[40, 50, 60], [3, 3, 3], 'soft_integer'],
            'k': [['apple', 'banana', 'cherry'], 3, 'fixed_string'],
        }


    # no _validation


    def test_accuracy(self, good_params):

        true_best_params = _make_true_best(good_params)

        for _param in good_params:

            assert _param in true_best_params

            _grid = _param[0]
            _type = _param[-1]
            _best = true_best_params[_param]

            if _type == 'fixed_string':
                assert _best in _grid

            elif _type == 'hard_float':
                assert _best >= min(_grid)
                assert _best <= max(_grid)

            elif _type == 'hard_integer':
                assert _best in range(min(_grid), max(_grid) + 1, 1)

            elif _type == 'fixed_float':
                assert _best in _grid

            elif _type == 'fixed_integer':
                assert _best in _grid

            elif _type == 'soft_float':
                _new_min = _grid[0] - (_grid[1] - _grid[0])
                _new_max = _grid[-1] + (_grid[-1] - _grid[-2])
                assert _best >= _new_min
                assert _best <= _new_max

            elif _type == 'soft_integer':
                _new_min = _grid[0] - (_grid[1] - _grid[0])
                _new_max = _grid[-1] + (_grid[-1] - _grid[-2])
                assert _best in range(_new_min, _new_max + 1, 1)





