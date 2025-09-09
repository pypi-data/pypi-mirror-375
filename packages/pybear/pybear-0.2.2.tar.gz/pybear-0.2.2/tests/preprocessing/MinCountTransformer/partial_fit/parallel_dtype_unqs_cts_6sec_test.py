# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.preprocessing._MinCountTransformer._partial_fit. \
    _parallel_dtypes_unqs_cts import _parallel_dtypes_unqs_cts



class TestParallelizedDtypeUnqsCts:


    # fixtures ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

    @staticmethod
    @pytest.fixture(scope='module')
    def _pool_size(_shape):
        return _shape[0] // 20


    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @staticmethod
    @pytest.fixture(scope='module')
    def float_chunk_no_nan(_pool_size, _shape):
        return np.random.uniform(0, _pool_size, _shape).astype(np.float64)


    @staticmethod
    @pytest.fixture(scope='module')
    def float_chunk_nan(float_chunk_no_nan, _shape):

        float_chunk_nan = float_chunk_no_nan.copy()

        _rows = np.arange(_shape[0])
        _num_nans = int(_shape[0] // 10)

        for _c_idx in range(_shape[1]):
            float_chunk_nan[
                np.random.choice(_rows, _num_nans, replace=False), _c_idx
            ] = np.nan

        del _rows, _num_nans

        return float_chunk_nan
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @staticmethod
    @pytest.fixture(scope='module')
    def int_chunk_no_nan(_pool_size, _shape):

        return np.random.randint(0, _pool_size, _shape)


    @staticmethod
    @pytest.fixture(scope='module')
    def int_chunk_nan(int_chunk_no_nan, _shape):

        # need to convert to float64 to put nans in
        int_chunk_nan = int_chunk_no_nan.copy().astype(np.float64)

        _rows = np.arange(_shape[0])
        _num_nans = int(_shape[0] // 10)

        for _c_idx in range(_shape[1]):

            int_chunk_nan[
                np.random.choice(_rows, _num_nans, replace=False), _c_idx
            ] = np.nan

        del _rows, _num_nans

        return int_chunk_nan
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @staticmethod
    @pytest.fixture(scope='module')
    def str_chunk_no_nan(_pool_size, _shape):

        pool = list('abcdefghijklmnopqrstuvwxyz')[:_pool_size]

        return np.random.choice(pool, _shape, replace=True)


    @staticmethod
    @pytest.fixture(scope='module')
    def str_chunk_nan(str_chunk_no_nan, _shape):

        # need to set as <U3 to take 'nan'
        str_chunk_nan = str_chunk_no_nan.copy().astype('<U3')

        _rows = np.arange(_shape[0])
        _num_nans = int(_shape[0] // 10)

        for _c_idx in range(_shape[1]):
            str_chunk_nan[
                np.random.choice(_rows, _num_nans, replace=False), _c_idx
            ] = 'nan'

        del _rows, _num_nans

        return str_chunk_nan
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    @staticmethod
    @pytest.fixture(scope='module')
    def good_unq_ct_dicts():

        def foo(any_chunk):

            list_of_dicts = []
            for _c_idx in range(any_chunk.shape[1]):
                list_of_dicts.append(
                    dict((zip(*np.unique(any_chunk[:, _c_idx], return_counts=True))))
                )

            return list_of_dicts

        return foo

    # END fixtures ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


    def test_accuracy_dtype_unq_ct__str(
        self, str_chunk_no_nan, str_chunk_nan, good_unq_ct_dicts
    ):

        for _exp_dtype, _chunk in \
                (('obj',str_chunk_no_nan), ('obj', str_chunk_nan)):

            out_dtypes_unq_ct_dicts = _parallel_dtypes_unqs_cts(_chunk)
            exp_unq_ct_dicts = good_unq_ct_dicts(_chunk)

            for _c_idx, (_out_dtype, _out_unq_ct_dict) in \
                    enumerate(out_dtypes_unq_ct_dicts):

                assert _out_dtype == _exp_dtype

                EXP = exp_unq_ct_dicts[_c_idx]
                EXP_KEYS = np.fromiter(EXP.keys(), dtype='<U1')
                EXP_VALUES = np.fromiter(EXP.values(), dtype=np.uint16)
                OUT_KEYS = np.fromiter(_out_unq_ct_dict.keys(), dtype='<U1')
                OUT_VALUES = np.fromiter(_out_unq_ct_dict.values(), dtype=np.uint16)

                assert np.array_equiv(OUT_KEYS, EXP_KEYS)
                assert np.array_equiv(OUT_VALUES, EXP_VALUES)


    def test_accuracy_dtype_unq_ct__float(
        self, float_chunk_no_nan, float_chunk_nan, good_unq_ct_dicts
    ):

        for _exp_dtype, _chunk in \
                (('float', float_chunk_no_nan), ('float', float_chunk_nan)):

            out_dtypes_unq_ct_dicts = _parallel_dtypes_unqs_cts(_chunk)
            exp_unq_ct_dicts = good_unq_ct_dicts(_chunk)

            for _c_idx, (_out_dtype, _out_unq_ct_dict) in \
                    enumerate(out_dtypes_unq_ct_dicts):

                assert _out_dtype == _exp_dtype

                EXP = exp_unq_ct_dicts[_c_idx]
                EXP_KEYS = np.fromiter(EXP.keys(), dtype=np.float64)
                EXP_VALUES = np.fromiter(EXP.values(), dtype=np.uint16)
                OUT_KEYS = np.fromiter(_out_unq_ct_dict.keys(), dtype=np.float64)
                OUT_VALUES = np.fromiter(_out_unq_ct_dict.values(), dtype=np.uint16)

                if any(np.isnan(EXP_KEYS)):
                    MASK = np.logical_not(np.isnan(EXP_KEYS))
                    EXP_KEYS = EXP_KEYS[MASK]
                    OUT_KEYS = OUT_KEYS[MASK]

                assert np.allclose(OUT_KEYS, EXP_KEYS, rtol=1e-6)

                assert np.array_equiv(OUT_VALUES, EXP_VALUES)


    def test_accuracy_dtype_unq_ct__int(
        self, int_chunk_no_nan, int_chunk_nan, good_unq_ct_dicts
    ):

        for _exp_dtype, _chunk in \
                (('int', int_chunk_no_nan), ('int', int_chunk_nan)):

            out_dtypes_unq_ct_dicts = _parallel_dtypes_unqs_cts(_chunk)
            exp_unq_ct_dicts = good_unq_ct_dicts(_chunk)

            for _c_idx, (_out_dtype, _out_unq_ct_dict) in \
                    enumerate(out_dtypes_unq_ct_dicts):

                assert _out_dtype == _exp_dtype

                EXP = exp_unq_ct_dicts[_c_idx]
                EXP_KEYS = np.fromiter(EXP.keys(), dtype=np.uint32)
                EXP_VALUES = np.fromiter(EXP.values(), dtype=np.uint16)
                OUT_KEYS = np.fromiter(_out_unq_ct_dict.keys(), dtype=np.uint32)
                OUT_VALUES = np.fromiter(_out_unq_ct_dict.values(), dtype=np.uint16)

                assert np.allclose(OUT_KEYS, EXP_KEYS, rtol=1e-6)

                assert np.array_equiv(OUT_VALUES, EXP_VALUES)


    def test_mixed_dtypes(self):

        # _columns_getter should only ever allow _pduc to see np.nan or
        # maybe str(np.nan) which is 'nan'
        _chunk = [
            [3.14, 1, np.nan, 'a'],
            [2.718, 3.14, np.nan, np.nan],
            [1, 2, np.nan, 3],
            [0, 1, 0, np.nan],
            ['a', 'b', 'c', 'nan']
        ]

        # transpose to get the rows above to represent columns
        _np_chunk = np.array(_chunk, dtype=object).transpose()

        out_dtypes_unq_ct_dicts = _parallel_dtypes_unqs_cts(_np_chunk)

        # too much complication with numpy turning py things into np
        # things and the nasty repr that comes along with that. instead
        # of comparing dictionaries directly, do it piecemeal.
        assert out_dtypes_unq_ct_dicts[0][0] == 'obj'
        _dict1 = out_dtypes_unq_ct_dicts[0][1]
        assert _dict1[1] == 1
        assert _dict1[3.14] == 1
        assert 'nan' in map(str, _dict1)
        assert _dict1['a'] == 1

        assert out_dtypes_unq_ct_dicts[1][0] == 'float'
        _dict2 = out_dtypes_unq_ct_dicts[1][1]
        assert _dict2[2.718] == 1
        assert _dict2[3.14] == 1
        assert 'nan' in map(str, _dict2)
        _dict2 = dict((zip(map(str, _dict2), map(int, _dict2.values()))))
        assert _dict2['nan'] == 2

        assert out_dtypes_unq_ct_dicts[2][0] == 'int'
        _dict3 = out_dtypes_unq_ct_dicts[2][1]
        assert _dict3[1] == 1
        assert _dict3[2] == 1
        assert 'nan' in map(str, _dict3)
        assert _dict3[3] == 1

        assert out_dtypes_unq_ct_dicts[3][0] == 'bin_int'
        _dict4 = out_dtypes_unq_ct_dicts[3][1]
        assert _dict4[0] == 2
        assert _dict4[1] == 1
        assert 'nan' in map(str, _dict4)

        assert out_dtypes_unq_ct_dicts[4][0] == 'obj'
        _dict5 = out_dtypes_unq_ct_dicts[4][1]
        assert _dict5['a'] == 1
        assert _dict5['b'] == 1
        assert _dict5['c'] == 1
        assert _dict5['nan'] == 1




