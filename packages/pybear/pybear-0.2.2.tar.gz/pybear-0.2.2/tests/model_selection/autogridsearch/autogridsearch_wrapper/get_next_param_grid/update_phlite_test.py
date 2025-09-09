# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._update_phlite import _update_phlite



class TestUpdatePhlite:


    @staticmethod
    @pytest.fixture
    def _params():
        return {
            'a': [[1, 2, 3, 4], [4, 4, 4], 'soft_integer'],
            'b': [[1e-2, 1e-1, 1e0, 1e1], [4, 4, 4], 'soft_float'],
            'c': [[1, 10, 100, 1000], [4, 4, 4], 'soft_float'],
            'd': [[2, 3, 4, 5], [4, 4, 4], 'fixed_integer'],
            'e': [[1.1, 1.2, 1.3, 1.4], [4, 4, 4], 'fixed_float'],
            'f': [[0, 0.25, 0.5, 0.75, 1.0], [5, 5, 5], 'hard_float'],
            'g': [[1, 10, 100, 1000], [4, 4, 4], 'soft_float'],
            'h': [[1, 2, 3, 4], [4, 4, 4], 'soft_integer'],
            'i': [[1, 2, 3, 4], [4, 4, 4], 'soft_integer'],
            'j': [[0, 0.25, 0.5, 0.75, 1.0], [5, 5, 5], 'hard_float'],
            'k': [[1, 10, 100, 1000], [4, 4, 4], 'soft_float'],
        }


    @staticmethod
    @pytest.fixture
    def param_grid():
        return {
            'a': [1, 2, 3, 4],  # 1 is int hard bound
            'b': [1e-2, 1e-1, 1e0, 1e1],
            'c': [1, 10, 100, 1000],
            'd': [2, 3, 4, 5],
            'e': [1.1, 1.2, 1.3, 1.4],
            'f': [0, 0.25, 0.5, 0.75, 1.0],  # 0 is float hard bound
            'g': [1, 10, 100, 1000],
            'h': [1, 2, 3, 4],
            'i': [1, 2, 3, 4],
            'j': [0, 0.25, 0.5, 0.75, 1.0],
            'k': [1, 10, 100, 1000]
        }


    @staticmethod
    @pytest.fixture
    def _best_params():
        return {
            'a': 1,  # [0], soft, 1 is int hard bound  TRUE
            'b': 1e1,  # [-1] soft, FALSE
            'c': 1000,  # [-1] soft, FALSE
            'd': 5,  # [-1] fixed, TRUE
            'e': 1.1,  # [0] fixed, TRUE
            'f': 0,  # [0] hard, 0 is float hard bound   # TRUE
            'g': 100,  # [-2] soft, TRUE
            'h': 2,  # [1] soft, TRUE
            'i': 4,  # [-1] soft, FALSE
            'j': 0.5,  # [2] hard, TRUE
            'k': 1,  # [0] soft, FALSE
        }


    @staticmethod
    @pytest.fixture
    def start_phlite_1():
        # arbitrary
        return {
            'a': False,
            'b': False,
            'c': True,
            'g': False,
            'h': True,
            'i': False,
            'k': False
        }


    @staticmethod
    @pytest.fixture
    def start_phlite_2():
        # arbitrary
        return {
            'a': True,
            'b': True,
            'c': True,
            'g': True,
            'h': True,
            'i': True,
            'k': True
        }


    @staticmethod
    @pytest.fixture
    def start_phlite_3():
        # arbitrary
        return {
            'a': True,
            'b': False,
            'c': False,
            'g': True,
            'h': True,
            'i': False,
            'k': False
        }


    @staticmethod
    @pytest.fixture
    def start_phlite_4():
        # arbitrary
        return {
            'a': False,
            'b': True,
            'c': True,
            'g': False,
            'h': False,
            'i': True,
            'k': True
        }


    @staticmethod
    @pytest.fixture
    def start_phlite_5():
        # arbitrary
        return {
            'a': True,
            'b': False,
            'c': False,
            'g': True,
            'h': False,
            'i': False,
            'k': False
        }


    @staticmethod
    @pytest.fixture
    def final_phlite():
        # not arbitrary! based on best params
        return {
            'a': True,
            'b': False,
            'c': False,
            'g': True,
            'h': True,
            'i': False,
            'k': False
        }



    def test_rejects_bad_phlite(
        self, _params, param_grid, _best_params, start_phlite_1, final_phlite
    ):

        bad_phlite = start_phlite_1 | {'d': True, 'e': False, 'f': True, 'j': False}

        with pytest.raises(ValueError):

            _update_phlite(bad_phlite, param_grid, _params, _best_params)


    def test_accuracy_1(
        self, _params, param_grid, _best_params, start_phlite_1, final_phlite
    ):

        out = _update_phlite(start_phlite_1, param_grid, _params, _best_params)

        assert out == final_phlite


    def test_accuracy_2(
        self, _params, param_grid, _best_params, start_phlite_2, final_phlite
    ):

        out = _update_phlite(start_phlite_2, param_grid, _params, _best_params)

        assert out == final_phlite


    def test_accuracy_3(
        self, _params, param_grid, _best_params, start_phlite_3, final_phlite
    ):

        out = _update_phlite(start_phlite_3, param_grid, _params, _best_params)

        assert out == final_phlite


    def test_accuracy_4(
        self, _params, param_grid, _best_params, start_phlite_4, final_phlite
    ):

        out = _update_phlite(start_phlite_4, param_grid, _params, _best_params)

        assert out == final_phlite


    def test_accuracy_5(
        self, _params, param_grid, _best_params, start_phlite_5, final_phlite
    ):

        out = _update_phlite(start_phlite_5, param_grid, _params, _best_params)

        assert out == final_phlite







