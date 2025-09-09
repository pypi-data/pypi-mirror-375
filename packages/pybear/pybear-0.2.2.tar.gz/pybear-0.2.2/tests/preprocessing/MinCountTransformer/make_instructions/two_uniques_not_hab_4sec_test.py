# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy

import numpy as np

from pybear.preprocessing._MinCountTransformer._make_instructions. \
    _two_uniques_not_hab import _two_uniques_not_hab



class TestValidation:

    @pytest.mark.parametrize('_nan_key', ('NAN', np.nan, 'nan'))
    @pytest.mark.parametrize('_nan_ct', (4, 7))
    @pytest.mark.parametrize('_dtype', ('int', 'float', 'obj'))
    def test_rejects_nan_in_unq_ct_dict(self, _nan_key, _nan_ct, _dtype):

        if _dtype == 'int':
            _unq_ct_dict = {_nan_key: _nan_ct, 0:235, 1: 92}
        elif _dtype == 'float':
            _unq_ct_dict = {_nan_key: _nan_ct, 2.718: 34, 3.14: 7}
        elif _dtype == 'obj':
            _unq_ct_dict = {_nan_key: _nan_ct, 'a': 634, 'b': 312}

        with pytest.raises(ValueError):
            _two_uniques_not_hab(
                _threshold=5,
                _nan_key=_nan_key,
                _nan_ct=_nan_ct,
                _COLUMN_UNQ_CT_DICT=_unq_ct_dict
            )


    @pytest.mark.parametrize('_dtype', ('int', 'float', 'obj'))
    def test_accepts_good_unq_ct_dict(self, _dtype):

        if _dtype == 'int':
            _unq_ct_dict = {0: 235, 1: 92}
        elif _dtype == 'float':
            _unq_ct_dict = {2.718: 34, 3.14: 7}
        elif _dtype == 'obj':
            _unq_ct_dict = {'a': 634, 'b': 312}

        _two_uniques_not_hab(
            _threshold=5,
            _nan_key=False,
            _nan_ct=False,
            _COLUMN_UNQ_CT_DICT=_unq_ct_dict
        )


class TestTwoUniquesNonInt:

    # always deletes rows

    @pytest.mark.parametrize('_threshold', (3, 6, 10))
    @pytest.mark.parametrize('_nan_key', ('NAN', np.nan, 'nan', False))
    @pytest.mark.parametrize('_nan_ct', (2, 4, 7, False))
    @pytest.mark.parametrize('_unq_ct_dict',
        ({2.14: 5, 3.14: 7}, {'a': 5, 'b': 8})
    )
    def test_two_uniques_non_int(
        self, _threshold, _nan_key, _nan_ct, _unq_ct_dict
    ):

        # if one is False, both must be False
        if (_nan_key is False) + (_nan_ct is False) == 1:
            pytest.skip(reason=f"disallowed condition")

        # do not put the nans and nan cts into here!
        _copy_unq_ct_dict = deepcopy(_unq_ct_dict)

        out = _two_uniques_not_hab(
            _threshold=_threshold,
            _nan_key=_nan_key,
            _nan_ct=_nan_ct,
            _COLUMN_UNQ_CT_DICT=_copy_unq_ct_dict
        )


        _instr_list = []
        _delete_column = False
        for unq, ct in _unq_ct_dict.items():
            if ct < _threshold:
                _delete_column = True
                _instr_list.append(unq)

        if _nan_ct and _nan_ct < _threshold:
            _instr_list.append(_nan_key)

        if _delete_column:
            _instr_list.append('DELETE COLUMN')

        assert out == _instr_list


class TestTwoUniquesBinInt:

    @pytest.mark.parametrize('_threshold', (3, 6, 10))
    @pytest.mark.parametrize('_nan_key', ('NAN', np.nan, 'nan', False))
    @pytest.mark.parametrize('_nan_ct', (2, 4, 7, False))
    @pytest.mark.parametrize('_unq_ct_dict',
        ({0: 5, 1: 7}, {0: 7, 1: 5}, {1: 5, 2: 7})
    )
    def test_two_uniques_bin_int(
        self, _threshold, _nan_key, _nan_ct, _unq_ct_dict
    ):

        # even though bin int is being used to test, in practice they
        # cannot get into this module

        # if one is False, both must be False
        if (_nan_key is False) + (_nan_ct is False) == 1:
            pytest.skip(reason=f"disallowed condition")

        # do not put the nans and nan cts into here!
        _copy_unq_ct_dict = deepcopy(_unq_ct_dict)

        out = _two_uniques_not_hab(
            _threshold=_threshold,
            _nan_key=_nan_key,
            _nan_ct=_nan_ct,
            _COLUMN_UNQ_CT_DICT=_copy_unq_ct_dict
        )


        _instr_list = []
        _delete_column = False
        for unq, ct in _unq_ct_dict.items():
            if ct < _threshold:
                _delete_column = True
                _instr_list.append(unq)

        if _nan_ct is not False and _nan_ct < _threshold:
            _instr_list.append(_nan_key)

        if _delete_column:
            _instr_list.append('DELETE COLUMN')

        assert out == _instr_list



