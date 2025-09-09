# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
import numpy as np

from pybear.model_selection.autogridsearch._autogridsearch_wrapper._validation. \
    _params_string import _val_string_param_value



class TestStringParamKey:


    def test_accepts_str(self):
        assert _val_string_param_value(
            'some_string', [['a','b'], 8, 'fixed_string']
        ) is None


class TestStringParamValueOuterContainer:


    @pytest.mark.parametrize('_container', (list, tuple, np.ndarray))
    def test_accepts_list_like(self, _container):
        _base = [['a', 'b'], 10, 'fixed_string']
        if _container in [list, tuple]:
            list_like = _container(_base)
        elif _container is np.ndarray:
            list_like = np.array(_base, dtype=object)
        else:
            raise Exception

        assert isinstance(list_like, _container)
        assert _val_string_param_value('good_key', list_like) is None


class TestStringListOfSearchPoints:


    @pytest.mark.parametrize('non_str_non_none',
        (0, np.pi, True, min, lambda x: x, {'a': 1}, [1,2], (1,2), {1,2})
    )
    def test_rejects_non_strings_non_none_in_grid(self, non_str_non_none):
        with pytest.raises(TypeError):
            _val_string_param_value(
                'good_key',
                [[non_str_non_none, 'b'], None, 'fixed_string']
            )


    @pytest.mark.parametrize('str_or_none', ('a', None))
    def test_accept_strings_or_none_inside(self, str_or_none):
        assert _val_string_param_value(
            'good_key', ((str_or_none, 'b'), 5, 'fixed_string')
        ) is None


class TestPoints:


    @pytest.mark.parametrize('int_or_seq', (3, [3,3,3]))
    def test_accepts_integer_or_sequence(self, int_or_seq):

        assert _val_string_param_value(
            'good_key',
            [['y','z'], int_or_seq, 'fixed_string']
        ) is None


class TestType:


    @pytest.mark.parametrize('_type',
        ('fixed_bool', 'fixed_string', 'soft_float')
    )
    def test_rejects_bad_accepts_good_type(self, _type):

        _value = [list('abcde'), [5,5,5], _type]

        if _type == 'fixed_string':
            assert _val_string_param_value('param_1', _value) is None
        else:
            with pytest.raises(AssertionError):
                _val_string_param_value('param_1', _value)

