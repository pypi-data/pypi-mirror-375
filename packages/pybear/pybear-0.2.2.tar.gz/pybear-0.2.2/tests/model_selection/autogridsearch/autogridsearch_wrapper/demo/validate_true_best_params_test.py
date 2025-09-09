# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.model_selection.autogridsearch._autogridsearch_wrapper._demo. \
    _validate_true_best import _validate_true_best



class TestValidateTrueBest:

    #     def _validate_true_best(
    #         _params,
    #         _IS_LOGSPACE,
    #         _true_best
    #     )


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
            'k': [['apple', 'banana', 'cherry'], [3, 3, 3], 'fixed_string']
        }


    @staticmethod
    @pytest.fixture
    def good_is_logspace():
        return {
            'a': False,
            'b': False,
            'c': False,
            'd': False,
            'e': False,
            'f': False,
            'g': 1.0,
            'h': False,
            'i': False,
            'j': False,
            'k': False
        }


    @staticmethod
    @pytest.fixture
    def good_true_best():
        return {
            'a': 'b',
            'b': 2.718,
            'c': 6,
            'd': 81.8234,
            'e': 4,
            'f': 49,
            'g': 16.2343,
            'h': 54.2,
            'i': 7,
            'j': 33,
            'k': 'cherry'
        }



    def test_rejects_not_full_set(
        self, good_params, good_is_logspace, good_true_best
    ):

        del good_true_best['k']

        with pytest.raises(ValueError):
            _validate_true_best(good_params, good_is_logspace, good_true_best)


    def test_rejects_unknown_param(
        self, good_params, good_is_logspace, good_true_best
    ):

        good_true_best['m'] = 'junk'

        with pytest.raises(ValueError):
            _validate_true_best(good_params, good_is_logspace, good_true_best)


    @pytest.mark.parametrize('junk_best',
        (False, True, None, [1,2], (1,2), {1,2}, int, {'a':1}, lambda x: x)
    )
    def test_rejects_non_str_best_for_str(
        self, good_params, good_is_logspace, good_true_best, junk_best
    ):

        bad_true_best = good_true_best
        bad_true_best['a'] = junk_best

        with pytest.raises(TypeError):
            _validate_true_best(good_params, good_is_logspace, bad_true_best)


    def test_rejects_bad_value_for_str(
        self, good_params, good_is_logspace, good_true_best
    ):

        bad_true_best = good_true_best
        bad_true_best['a'] = 'q'

        with pytest.raises(ValueError):
            _validate_true_best(good_params, good_is_logspace, bad_true_best)


    @pytest.mark.parametrize('param_key', list('bcdefghij'))
    @pytest.mark.parametrize('junk_num',
        ('junk', None, [1,2], (1,2), {1,2}, int, {'a':1}, lambda x: x)
    )
    def test_rejects_non_num_for_int_float(
        self, good_params, good_is_logspace, good_true_best, param_key, junk_num
    ):

        bad_true_best = good_true_best
        bad_true_best[param_key] = junk_num

        with pytest.raises(TypeError):
            _validate_true_best(good_params, good_is_logspace, bad_true_best)


    def test_rejects_neg_in_logspace(
        self, good_params, good_is_logspace, good_true_best
    ):

        bad_true_best = good_true_best
        bad_true_best['g'] = -234.9798

        with pytest.raises(ValueError):
            _validate_true_best(good_params, good_is_logspace, bad_true_best)


    @pytest.mark.parametrize('param_key', list('bc'))
    def test_rejects_fixed_num_not_in_grid(
        self, good_params, good_is_logspace, good_true_best, param_key
    ):

        bad_true_best = good_true_best
        bad_true_best[param_key] = 73843

        with pytest.raises(ValueError):
            _validate_true_best(good_params, good_is_logspace, bad_true_best)


    @pytest.mark.parametrize('param_key', list('def'))
    @pytest.mark.parametrize('bad_value', (3, 101))
    def test_rejects_hard_out_of_range(
        self, good_params, good_is_logspace, good_true_best, param_key, bad_value
    ):

        bad_true_best = good_true_best
        bad_true_best[param_key] = bad_value

        with pytest.raises(ValueError):
            _validate_true_best(good_params, good_is_logspace, bad_true_best)


    @pytest.mark.parametrize('param_key', list('efij'))
    @pytest.mark.parametrize('bad_value', (0, -1))
    def test_rejects_integer_lt_1(
        self, good_params, good_is_logspace, good_true_best, param_key, bad_value
    ):

        bad_true_best = good_true_best
        bad_true_best[param_key] = bad_value

        with pytest.raises(ValueError):
            _validate_true_best(good_params, good_is_logspace, bad_true_best)


    @pytest.mark.parametrize('param_key', list('bdgh'))
    def test_rejects_integer_lt_1(
        self, good_params, good_is_logspace, good_true_best, param_key
    ):

        bad_true_best = good_true_best
        bad_true_best[param_key] = -1

        with pytest.raises(ValueError):
            _validate_true_best(good_params, good_is_logspace, bad_true_best)








