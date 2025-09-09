# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy

from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._string._string import _string



# (zero-indexed) pass must be >= 1... on pass 0 param_grid is built by
# _build, only sees _get after that


class TestString:


    @staticmethod
    @pytest.fixture
    def _param_value():
        return [['saga', 'lbfgs'], [2, 2, 1, 1], 'fixed_string']


    @staticmethod
    @pytest.fixture
    def _grids():
        return {0: {'a': ['saga', 'lbfgs'], 'b': [1, 2, 3]}, 1: {}}


    @staticmethod
    @pytest.fixture
    def _best_params():
        return {'a': 'saga', 'b': 2}


    def test_accuracy_1(self, _param_value, _grids, _best_params):

        # _pass (zero-indexed) is still full set of strings

        out = _string(_param_value, _grids[0]['a'], 1, _best_params['a'])

        assert out == ['saga', 'lbfgs']


    @pytest.mark.parametrize('_pass', (2, 3))
    def test_accuracy_2(self, _param_value, _grids, _best_params, _pass):

        # num points for _pass (zero-indexed) has been set to 1 by user

        _grids[1] = deepcopy(_grids[0])
        _grids[2] = {}

        out = _string(_param_value, _grids[0]['a'], _pass, _best_params['a'])

        assert out == ['saga']






