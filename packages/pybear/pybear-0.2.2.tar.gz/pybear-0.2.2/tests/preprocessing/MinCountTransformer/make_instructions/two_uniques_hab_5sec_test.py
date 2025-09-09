# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy

import numpy as np

from pybear.preprocessing._MinCountTransformer._make_instructions. \
    _two_uniques_hab import _two_uniques_hab



class TestValidation:


    @pytest.mark.parametrize('_nan_key', ('NAN', np.nan, 'nan'))
    @pytest.mark.parametrize('_nan_ct', (4, 7))
    @pytest.mark.parametrize('_delete_axis_0', (True, False))
    @pytest.mark.parametrize('_dtype', ('int', 'float'))
    def test_rejects_nan_in_unq_ct_dict(self,
        _nan_key, _nan_ct, _delete_axis_0, _dtype):

        if _dtype == 'int':
            _unq_ct_dict = {_nan_key: _nan_ct, 0:235, 1: 92}
        elif _dtype == 'float':
            _unq_ct_dict = {_nan_key: _nan_ct, 2.718: 34, 3.14: 7}

        with pytest.raises(ValueError):
            _two_uniques_hab(
                _threshold=5,
                _nan_key=_nan_key,
                _nan_ct=_nan_ct,
                _COLUMN_UNQ_CT_DICT=_unq_ct_dict,
                _delete_axis_0=_delete_axis_0
            )


    @pytest.mark.parametrize('_delete_axis_0', (True, False))
    @pytest.mark.parametrize('_dtype', ('int', 'float'))
    def test_accepts_good_unq_ct_dict(self, _delete_axis_0, _dtype):

        if _dtype == 'int':
            _unq_ct_dict = {0: 235, 1: 92}
        elif _dtype == 'float':
            _unq_ct_dict = {2.718: 34, 3.14: 7}

        _two_uniques_hab(
            _threshold=5,
            _nan_key=False,
            _nan_ct=False,
            _COLUMN_UNQ_CT_DICT=_unq_ct_dict,
            _delete_axis_0=_delete_axis_0
        )


    @pytest.mark.parametrize('_delete_axis_0', (True, False))
    def test_rejects_str_data(self, _delete_axis_0):

        # this is bounced by map(float, _COLUMN_UNQ_CT_DICT.keys())
        with pytest.raises(ValueError):
            _two_uniques_hab(
                _threshold=5,
                _nan_key=False,
                _nan_ct=False,
                _COLUMN_UNQ_CT_DICT={'a':25, 'b':38},
                _delete_axis_0=_delete_axis_0
            )


class TestTwoUniquesHAB:


    @pytest.mark.parametrize('_threshold', (3, 6, 10))
    @pytest.mark.parametrize('_nan_key', ('NAN', np.nan, 'nan', False))
    @pytest.mark.parametrize('_nan_ct', (2, 4, 7, False))
    @pytest.mark.parametrize('_dtype, _unq_ct_dict',
        (('float', {2.14: 5, 3.14: 7}), ('float', {0: 5, 3.14: 7}))
    )
    @pytest.mark.parametrize('_delete_axis_0', (True, False))
    def test_two_uniques_hab_float(self,
        _threshold, _nan_key, _nan_ct, _dtype, _unq_ct_dict, _delete_axis_0
    ):

        if (_nan_key is False) + (_nan_ct is False) == 1:
            pytest.skip(reason=f"disallowed condition")

        _copy_unq_ct_dict = deepcopy(_unq_ct_dict)

        out = _two_uniques_hab(
            _threshold=_threshold,
            _nan_key=_nan_key,
            _nan_ct=_nan_ct,
            _COLUMN_UNQ_CT_DICT=_copy_unq_ct_dict,
            _delete_axis_0=_delete_axis_0
        )


        _zero_ct = 0
        _non_zero_ct = 0
        for unq, ct in _unq_ct_dict.items():
            if unq == 0:
                _zero_ct += ct
            elif unq != 0:
                _non_zero_ct += ct

        _instr_list = []
        _delete_column = False
        if _zero_ct and _zero_ct < _threshold:
            _delete_column = True
            if _delete_axis_0:
                _instr_list.append(0)
        elif not _zero_ct:
            _delete_column = True

        if _non_zero_ct and _non_zero_ct < _threshold:
            _delete_column = True
            if _delete_axis_0:
                for k, v in _copy_unq_ct_dict.items():
                    if k != 0:
                        _instr_list.append(k)
        elif not _non_zero_ct:
            _delete_column = True

        if _nan_ct is not False and _nan_ct < _threshold:
            if _delete_axis_0:
                _instr_list.append(_nan_key)
            elif not _delete_axis_0 and min(_zero_ct, _non_zero_ct) > _threshold:
                _instr_list.append(_nan_key)

        if _delete_column:
            _instr_list.append('DELETE COLUMN')

        assert out == _instr_list


    @pytest.mark.parametrize('_threshold', (3, 6, 10))
    @pytest.mark.parametrize('_nan_key', ('NAN', np.nan, 'nan', False))
    @pytest.mark.parametrize('_nan_ct', (2, 4, 7, False))
    @pytest.mark.parametrize('_dtype, _unq_ct_dict',
        (('float', {'2.14': 5, '3.14': 7}), ('float', {'0': 5, '3.14': 7}))
    )
    @pytest.mark.parametrize('_delete_axis_0', (True, False))
    def test_two_uniques_hab_float_as_str(self,
        _threshold, _nan_key, _nan_ct, _dtype, _unq_ct_dict, _delete_axis_0
    ):

        if (_nan_key is False) + (_nan_ct is False) == 1:
            pytest.skip(reason=f"disallowed condition")

        _copy_unq_ct_dict = deepcopy(_unq_ct_dict)

        out = _two_uniques_hab(
            _threshold=_threshold,
            _nan_key=_nan_key,
            _nan_ct=_nan_ct,
            _COLUMN_UNQ_CT_DICT=_copy_unq_ct_dict,
            _delete_axis_0=_delete_axis_0
        )


        _zero_ct = 0
        _non_zero_ct = 0
        for unq, ct in _unq_ct_dict.items():
            if float(unq) == 0:
                _zero_ct += ct
            elif float(unq) != 0:
                _non_zero_ct += ct

        _instr_list = []
        _delete_column = False
        if _zero_ct and _zero_ct < _threshold:
            _delete_column = True
            if _delete_axis_0:
                for k in _unq_ct_dict:
                    if float(k) == 0:
                        _instr_list.append(k)
        elif not _zero_ct:
            _delete_column = True

        if _non_zero_ct and _non_zero_ct < _threshold:
            _delete_column = True
            if _delete_axis_0:
                for k in _copy_unq_ct_dict:
                    if float(k) != 0:
                        _instr_list.append(k)
        elif not _non_zero_ct:
            _delete_column = True

        if _nan_ct is not False and _nan_ct < _threshold:
            if _delete_axis_0:
                _instr_list.append(_nan_key)
            elif not _delete_axis_0 and min(_zero_ct, _non_zero_ct) > _threshold:
                _instr_list.append(_nan_key)

        if _delete_column:
            _instr_list.append('DELETE COLUMN')

        assert out == _instr_list


    @pytest.mark.parametrize('_threshold', (3, 6, 10))
    @pytest.mark.parametrize('_nan_key', ('NAN', np.nan, 'nan', False))
    @pytest.mark.parametrize('_nan_ct', (2, 4, 7, False))
    @pytest.mark.parametrize('_dtype, _unq_ct_dict',
        (
            ('bin_int', {0: 5, 1: 7}), ('bin_int', {0: 7, 1: 5}),
            ('bin_int', {1: 5, 2: 7})
        )
    )
    @pytest.mark.parametrize('_delete_axis_0', (True, False))
    def test_two_uniques_hab_bin_int(self,
        _threshold, _nan_key, _nan_ct, _dtype, _unq_ct_dict, _delete_axis_0
    ):

        if (_nan_key is False) + (_nan_ct is False) == 1:
            pytest.skip(reason=f"disallowed condition")

        _copy_unq_ct_dict = deepcopy(_unq_ct_dict)

        out = _two_uniques_hab(
            _threshold=_threshold,
            _nan_key=_nan_key,
            _nan_ct=_nan_ct,
            _COLUMN_UNQ_CT_DICT=_copy_unq_ct_dict,
            _delete_axis_0=_delete_axis_0,
        )


        _instr_list = []
        _delete_column = False
        _zero_ct = 0
        _non_zero_ct = 0
        for unq, ct in _unq_ct_dict.items():
            if unq == 0:
                _zero_ct += ct
            else:
                _non_zero_ct += ct

        if _zero_ct and _zero_ct < _threshold:
            _delete_column = True
            if _delete_axis_0:
                _instr_list.append(0)
        elif not _zero_ct:
            # no zeros in when handling as bool would mean all the same number
            _delete_column = True


        if _non_zero_ct and _non_zero_ct < _threshold:
            _delete_column = True
            if _delete_axis_0:
                for unq, ct in _unq_ct_dict.items():
                    if unq != 0:
                        _instr_list.append(unq)
        elif not _non_zero_ct:
            # a column of all zeroes
            _delete_column = True


        if _nan_ct is not False and _nan_ct < _threshold:
            if _delete_axis_0:
                _instr_list.append(_nan_key)
            elif not _delete_axis_0:
                if min(_zero_ct, _non_zero_ct) >= _threshold:
                    _instr_list.append(_nan_key)


        if _delete_column:
            _instr_list.append('DELETE COLUMN')

        assert out == _instr_list




