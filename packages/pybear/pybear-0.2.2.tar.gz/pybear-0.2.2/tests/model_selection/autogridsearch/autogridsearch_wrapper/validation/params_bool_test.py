# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
import numpy as np

from pybear.model_selection.autogridsearch._autogridsearch_wrapper._validation. \
    _params_bool import _val_bool_param_value



class TestBoolParamKey:

    def test_accepts_str(self):
        assert _val_bool_param_value(
            'some_string', [[True, False], 8, 'fixed_bool']
        ) is None


class TestBoolParamValueOuterContainer:

    @pytest.mark.parametrize('_container', (list, tuple, np.ndarray))
    def test_accepts_list_like(self, _container):
        _base = [[True, False, None], 10, 'fixed_bool']
        if _container in [list, tuple]:
            list_like = _container(_base)
        elif _container is np.ndarray:
            list_like = np.array(_base, dtype=object)
        else:
            raise Exception

        assert isinstance(list_like, _container)
        assert _val_bool_param_value('good_key', list_like) is None


class TestBoolListOfSearchPoints:

    @pytest.mark.parametrize('non_bool',
        (0, 2.7, np.pi, min, 'trash', lambda x: x, {'a': 1}, [1,2], (1,2), {1,2})
    )
    def test_rejects_non_bool_non_None_in_grid(self, non_bool):
        with pytest.raises(TypeError):
            _val_bool_param_value(
                'good_key',
                [[non_bool, False], None, 'fixed_bool']
            )


    @pytest.mark.parametrize('_bool', (True, False, None))
    def test_accepts_bool_None_inside(self, _bool):
        assert _val_bool_param_value(
            'good_key', ([_bool, False], 5, 'fixed_bool')
        ) is None


class TestPoints:

    @pytest.mark.parametrize('int_or_seq', (3, [3,3,3]))
    def test_accepts_integer_or_sequence(self, int_or_seq):

        assert _val_bool_param_value(
            'good_key',
            [[True,False], int_or_seq, 'fixed_bool']
        ) is None


class TestType:

    @pytest.mark.parametrize('_type',
        ('fixed_bool', 'fixed_string', 'soft_float')
    )
    def test_rejects_bad_accepts_good_type(self, _type):

        _value = [[True, False], [2,2,2], _type]

        if _type == 'fixed_bool':
            assert _val_bool_param_value('param_1', _value) is None
        else:
            with pytest.raises(AssertionError):
                _val_bool_param_value('param_1', _value)




