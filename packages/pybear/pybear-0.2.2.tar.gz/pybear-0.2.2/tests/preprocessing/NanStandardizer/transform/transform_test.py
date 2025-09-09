# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

from pybear.preprocessing._NanStandardizer._transform._transform import _transform

from pybear.utilities._nan_masking import nan_mask



class TestTransform:


    @pytest.mark.parametrize('_format', (list, tuple))
    @pytest.mark.parametrize('_dtype', ('num', 'str'))
    @pytest.mark.parametrize('_fill', (99, None, True, 'NaN', np.nan))
    def test_accuracy_py_builtin(self, _fill, _format, _dtype, _X_num, _X_str):


        if _dtype == 'num':
            _X = _X_num.tolist()
        elif _dtype == 'str':
            _X = _X_str.tolist()
        else:
            raise Exception

        _X = _format(map(_format, _X))

        out = _transform(_X, _fill)

        assert isinstance(out, type(_X))
        assert np.array(out).shape == np.array(_X).shape

        ref = np.array(_X).copy()
        ref[nan_mask(ref)] = _fill
        ref = _format(map(_format, ref))

        # assertions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if _dtype == 'str':
            for r_idx in range(len(out)):
                assert np.array_equal(list(out[r_idx]), list(ref[r_idx]))
        elif _dtype == 'num':
            for r_idx in range(len(out)):
                assert np.array_equal(
                    list(out[r_idx]), list(ref[r_idx]), equal_nan=True
                )


    @pytest.mark.parametrize('_dtype', ('num', 'str'))
    @pytest.mark.parametrize('_fill', (99, None, True, 'NaN', np.nan))
    def test_accuracy_np(self, _fill, _dtype, _X_num, _X_str):


        if _dtype == 'num':
            _X = _X_num
        elif _dtype == 'str':
            _X = _X_str
        else:
            raise Exception

        out = _transform(_X, _fill)

        assert isinstance(out, type(_X))
        assert out.shape == _X.shape

        ref = _X.copy()
        ref[nan_mask(ref)] = _fill

        # assertions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if (isinstance(_fill , str) or _dtype == 'str'):
            # fill was a str, which should coerce target object to str dtype
            # or target already was str dtype
            if len(out.shape) == 1:
                assert np.array_equal(
                    list(map(str, out)),
                    list(map(str, ref))
                )
            else:
                for r_idx in range(out.shape[0]):
                    assert np.array_equal(
                        list(map(str, out[r_idx])),
                        list(map(str, ref[r_idx]))
                    )
        else:
            assert all(map(np.array_equal, out, ref, (True for _ in out)))


    @pytest.mark.parametrize('X_format', ('pd_series', 'pd_df'))
    @pytest.mark.parametrize('_dtype', ('num', 'str'))
    @pytest.mark.parametrize('_fill', (99, None, True, 'NaN', np.nan))
    def test_accuracy_pd(self, X_format, _fill, _dtype, _X_num, _X_str):


        if _dtype == 'num':
            _X = _X_num
        elif _dtype == 'str':
            _X = _X_str
        else:
            raise Exception

        if X_format == 'pd_series':
            _X = pd.Series(_X[:, 0])
        elif X_format == 'pd_df':
            _X = pd.DataFrame(_X)
        else:
            raise Exception


        out = _transform(_X, _fill)

        assert isinstance(out, type(_X))
        assert out.shape == _X.shape

        ref = _X.copy()
        ref[nan_mask(ref)] = _fill

        # assertions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if (isinstance(_fill , str) or _dtype == 'str'):
            # fill was a str, which should coerce target object to str dtype
            # or target already was str dtype
            if len(out.shape) == 1:
                assert np.array_equal(
                    list(map(str, out)),
                    list(map(str, ref))
                )
            else:
                for r_idx in range(len(out)):
                    assert np.array_equal(
                        list(map(str, out.iloc[r_idx, :])),
                        list(map(str, ref.iloc[r_idx, :]))
                    )
        else:
            assert all(map(np.array_equal, out, ref, (True for _ in out)))


    @pytest.mark.parametrize('X_format',
        ('ss_csr_mat', 'ss_csr_arr', 'ss_csc_mat', 'ss_csc_arr', 'ss_coo_mat',
        'ss_coo_arr')
    )
    @pytest.mark.parametrize('_fill', (99, None, True, np.nan))
    def test_accuracy_ss(self, X_format, _fill, _X_num):

        # no strings!

        if X_format == 'ss_csr_mat':
            _X = ss.csr_matrix(_X_num)
        elif X_format == 'ss_csr_arr':
            _X = ss.csr_array(_X_num)
        elif X_format == 'ss_csc_mat':
            _X = ss.csc_matrix(_X_num)
        elif X_format == 'ss_csc_arr':
            _X = ss.csc_array(_X_num)
        elif X_format == 'ss_coo_mat':
            _X = ss.coo_matrix(_X_num)
        elif X_format == 'ss_coo_arr':
            _X = ss.coo_array(_X_num)
        else:
            raise Exception


        out = _transform(_X, _fill)

        assert isinstance(out, type(_X))
        assert out.shape == _X.shape


        ref = _X.data.copy()
        ref[nan_mask(ref)] = _fill

        # assertions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        assert np.array_equal(out.data, ref.data, equal_nan=True)


    @pytest.mark.parametrize('X_format', ('pl_series', 'pl_df'))
    @pytest.mark.parametrize('_dtype', ('num', 'str'))
    @pytest.mark.parametrize('_fill', (99, None, True, 'NaN', np.nan))
    def test_accuracy_pl(self, X_format, _fill, _dtype, _X_num, _X_str):


        if _dtype == 'num':
            _X = _X_num
        elif _dtype == 'str':
            _X = _X_str
        else:
            raise Exception


        if X_format == 'pl_series':
            _X = pl.Series(_X[:, 0])
        elif X_format == 'pl_df':
            _X = pl.DataFrame(_X)
        else:
            raise Exception

        # pl wont cast non-str to str, and vice versa.
        # this is a pl casting issue, not pybear.
        if _fill is None or _fill == 'NaN':
            out = _transform(_X, _fill)
        elif (isinstance(_fill , str) and _dtype != 'str') \
            or (not isinstance(_fill , str) and _dtype == 'str'):
            # there is some wack behavior in polars. sometimes it will
            # cast a value of different type to a df/series and other
            # times it wont.
            try:
                out = _transform(_X, _fill)
            except Exception as e:
                # this is handled by polars, let it raise whatever
                pytest.skip(reason=f'cant do more tests without transform')

        else:
            out = _transform(_X, _fill)
        assert isinstance(out, type(_X))
        assert out.shape == _X.shape

        ref = _X.to_numpy().copy()
        ref[nan_mask(ref)] = _fill

        # assertions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if _dtype == 'str':
            if len(out.shape) == 1:
                assert np.array_equal(
                    list(map(str, out.to_numpy())),
                    list(map(str, ref))
                )
            else:
                for r_idx in range(out.shape[0]):
                    assert np.array_equal(
                        list(map(str, out.to_numpy()[r_idx])),
                        list(map(str, ref[r_idx]))
                    )
        else:
            assert all(map(
                np.array_equal,
                out.to_numpy(),
                ref,
                (True for _ in out)
            ))




