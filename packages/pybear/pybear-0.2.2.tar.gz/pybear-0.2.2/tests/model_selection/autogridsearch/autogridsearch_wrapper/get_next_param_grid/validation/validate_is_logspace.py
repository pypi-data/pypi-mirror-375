# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._validation._validate_is_logspace import \
    _validate_is_logspace



class TestIsLogspace:


    @pytest.mark.parametrize('non_dict',
        (0, np.pi, True, None, min, (1,), [1, ], {1, 2}, lambda x: x, 'junk')
    )
    def test_rejects_non_dict(self, non_dict):

        with pytest.raises(TypeError):
            _validate_is_logspace(
                non_dict,
                {'a': [['a','b','c'], [3,3,3], 'fixed_string']}
            )


    @pytest.mark.parametrize('key_1',
        (1, np.pi, True, False, None, min, (1,), lambda x: x, 'junk1', 'junk2')
    )
    @pytest.mark.parametrize('key_2',
        (1, np.pi, True, False, None, min, (1,), lambda x: x, 'junk1', 'junk2')
    )
    def test_rejects_non_str_keys(self, key_1, key_2):

        if key_1 == key_2:
            pytest.skip(reason=f"redundant combination")

        if isinstance(key_1, str) and isinstance(key_2, str):
            pytest.skip(reason=f"expected to pass")

        _params = {
            key_1: [[1,2,3], [3,3,3], 'fixed_integer'],
            key_2: [[1e3, 1e4, 1e5], [3, 11, 11], 'soft_float']
        }

        bad_IS_LOGSPACE = {key_1: True, key_2: False}

        with pytest.raises(TypeError):
            _validate_is_logspace(bad_IS_LOGSPACE, _params)


    @pytest.mark.parametrize('bad_logspace',
        (None, min, (1,), [1,2], {'a': 1}, {1,2}, lambda x: x, 'more_junk')
    )
    def test_rejects_non_bool_non_float_values(self, bad_logspace):

        with pytest.raises(TypeError):
            bad_logspace({'a': bad_logspace}, {'a': [[1,2],[2,2],'fixed_integer']})


    def test_rejects_is_logspace_not_in_params(self):

        _IS_LOGSPACE = {'a': 1.0, 'b': False, 'c': 2.0}

        _params = {
            'a': [[1e1, 1e2, 1e3], [3,3,3], 'soft_float'],
            'b': [['q', 'r'], [2,2], 'fixed_string']
        }

        with pytest.raises(ValueError):
            _validate_is_logspace(_IS_LOGSPACE, _params)


    def test_rejects_params_not_in_is_logspace(self):

        _IS_LOGSPACE = {'a': 1.0, 'b': False}

        _params = {
            'a': [[1e1, 1e2, 1e3], [3,3,3], 'soft_float'],
            'b': [['q', 'r'], [2,2], 'fixed_string'],
            'c': [[1e0, 1e2, 1e4], [3,3,3], 'soft_float']
        }

        with pytest.raises(ValueError):
            _validate_is_logspace(_IS_LOGSPACE, _params)


    def test_accepts_bool_and_float_rejects_negative(self):

        _params = {'a': [[1,2], 2, 'fixed_integer']}

        _validate_is_logspace({'a': True}, _params)
        _validate_is_logspace({'a': False}, _params)
        _validate_is_logspace({'a': 1.5}, _params)
        _validate_is_logspace({'a': 1.0}, _params)

        with pytest.raises(ValueError):
            _validate_is_logspace({'a': -1.5}, _params)







