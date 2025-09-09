# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._validation._validate_best_params import \
    _validate_best_params



class TestValidation:


    @staticmethod
    @pytest.fixture
    def good_grids():
        return {
            0: {'a': [1, 2, 3], 'b': [True, False]},
            1: {'a': [1, 2, 3], 'b': [True, False]}
        }


    @staticmethod
    @pytest.fixture
    def bad_grids_1():
        return {
            0: {'a': [1, 2, 3], 'b': [True, False], 'c': [1, 2, 3]},
            1: {'a': [1, 2, 3], 'b': [True, False], 'c': [1, 2, 3]}
        }


    @staticmethod
    @pytest.fixture
    def bad_grids_2():
        return {
            0: {'a': [1, 2, 3], 'b': [True, False]},
            1: {'a': [1, 2, 3], 'z': [True, False]}
        }


    @staticmethod
    @pytest.fixture
    def good_best_params():
        return {'a': 1, 'b': False}


    @staticmethod
    @pytest.fixture
    def bad_best_params_1():
        return {'a': 1, 'y': False}


    @staticmethod
    @pytest.fixture
    def bad_best_params_2():
        return {'a': 1, 'b': 99}


    # END FIXTURES -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    def test_passes_good(self, good_grids, good_best_params):
        _validate_best_params(good_grids, 2, good_best_params)


    def test_rejects_best_params_not_dict(self, good_grids):
        with pytest.raises(TypeError):
            _validate_best_params(good_grids, 2, [1,2,3,4,5])


    def test_rejects_for_bad_count(self, bad_grids_1, good_best_params):
        with pytest.raises(ValueError):
            _validate_best_params(bad_grids_1, 2, good_best_params)


    def test_rejects_best_param_not_in_grids(self, good_grids, bad_best_params_1):
        with pytest.raises(ValueError):
            _validate_best_params(good_grids, 2, bad_best_params_1)


    def test_rejects_best_param_not_in_search_space(self, good_grids,
                                                    bad_best_params_2):
        with pytest.raises(ValueError):
            _validate_best_params(good_grids, 2, bad_best_params_2)


    def test_rejects_grid_not_in_best_params(self, bad_grids_2, good_best_params):

        with pytest.raises(ValueError):
            _validate_best_params(bad_grids_2, 2, good_best_params)






