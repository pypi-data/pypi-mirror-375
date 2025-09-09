# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy

import numpy as np

from pybear.preprocessing._MinCountTransformer._make_instructions. \
    _three_or_more_uniques_not_hab import _three_or_more_uniques_not_hab



class TestValidation:


    @pytest.mark.parametrize('_nan_key', ('NAN', np.nan, 'nan'))
    @pytest.mark.parametrize('_nan_ct', (4, 7))
    @pytest.mark.parametrize('_dtype', ('int', 'float', 'obj'))
    def test_rejects_nan_in_unq_ct_dict(self, _nan_key, _nan_ct, _dtype):
        if _dtype == 'int':
            _unq_ct_dict = {_nan_key: _nan_ct, 0: 235, 1: 92, 2: 5}
        elif _dtype == 'float':
            _unq_ct_dict = {_nan_key: _nan_ct, 2.718: 34, 3.14: 7, 8.834: 3}
        elif _dtype == 'obj':
            _unq_ct_dict = {_nan_key: _nan_ct, 'a': 634, 'b': 312, 'c': 4}

        with pytest.raises(ValueError):
            _three_or_more_uniques_not_hab(
                _threshold=5,
                _nan_key=_nan_key,
                _nan_ct=_nan_ct,
                _COLUMN_UNQ_CT_DICT=_unq_ct_dict
            )


    @pytest.mark.parametrize('_unq_ct_dict',
        (
            {0:235, 1: 92, 2: 83},
            {2.718: 34, 3.14: 7, 8.834: 51},
            {'a': 634, 'b': 312, 'c': 188}
        )
    )
    def test_accepts_good_unq_ct_dict(self, _unq_ct_dict):

        _three_or_more_uniques_not_hab(
            _threshold=5,
            _nan_key=False,
            _nan_ct=False,
            _COLUMN_UNQ_CT_DICT=_unq_ct_dict
        )


class TestThreeOrMoreUniquesNotHandleAsBool:

    # always deletes rows

    @pytest.mark.parametrize('_threshold', (3, 6, 10))
    @pytest.mark.parametrize('_nan_key', ('NAN', np.nan, 'nan', False))
    @pytest.mark.parametrize('_nan_ct', (2, 4, 7, False))
    @pytest.mark.parametrize('_dtype, _unq_ct_dict',
        (
                ('int', {0: 9, 1: 6, 2: 4}),
                ('float', {2.14: 5, 3.14: 7, 4.14: 9}),
                ('obj', {'a': 5, 'b': 8, 'c': 9})
        )
    )
    def test_three_or_more_uniques_not_handle_as_bool(self,
        _threshold, _nan_key, _nan_ct, _dtype, _unq_ct_dict):

        if (_nan_key is False) + (_nan_ct is False) == 1:
            pytest.skip(reason=f"disallowed condition")

        _copy_unq_ct_dict = deepcopy(_unq_ct_dict)

        out = _three_or_more_uniques_not_hab(
            _threshold=_threshold,
            _nan_key=_nan_key,
            _nan_ct=_nan_ct,
            _COLUMN_UNQ_CT_DICT=_copy_unq_ct_dict
        )


        _instr_list = []
        _UNQS = np.fromiter(_unq_ct_dict.keys(), dtype=object)
        _CTS = np.fromiter(_unq_ct_dict.values(), dtype=np.uint32)
        if np.all((_CTS < _threshold)):
            _instr_list.append('DELETE ALL')
        else:
            for unq, ct in _unq_ct_dict.items():
                if ct < _threshold:
                    _instr_list.append(unq)
        del _UNQS, _CTS

        _delete_column = False
        if 'DELETE ALL' in _instr_list or \
                len(_instr_list) >= len(_unq_ct_dict) - 1:
            _delete_column = True

        if 'DELETE ALL' not in _instr_list and _nan_ct and _nan_ct < _threshold:
            _instr_list.append(_nan_key)

        if _delete_column:
            _instr_list.append('DELETE COLUMN')

        assert out == _instr_list




