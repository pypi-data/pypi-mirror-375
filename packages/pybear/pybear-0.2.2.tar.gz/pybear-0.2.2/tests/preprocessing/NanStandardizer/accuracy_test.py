# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd
import polars as pl

from pybear.preprocessing._NanStandardizer.NanStandardizer import \
    NanStandardizer

from pybear.utilities._nan_masking import nan_mask



class TestAccuracy:


    def test_empty_X(self):

        # 1D
        TestCls = NanStandardizer()

        out = TestCls.transform(np.zeros((0,)))

        assert isinstance(out, np.ndarray)
        assert len(out) == 0

        # 2D
        TestCls = NanStandardizer()

        out = TestCls.transform(np.zeros((1,0)))

        assert isinstance(out, np.ndarray)
        assert len(out) == 1
        assert len(out[0]) == 0


    def test_accuracy(self, _X_num):

        # default fill = np.nan

        TestCls = NanStandardizer()

        out = TestCls.transform(_X_num, copy=True)
        assert isinstance(out, np.ndarray)
        assert all(map(isinstance, out, (np.ndarray for _ in out)))

        ref = _X_num.copy()
        ref[nan_mask(ref)] = np.nan
        assert np.array_equal(out, ref, equal_nan=True)


    def test_various_input_containers(self, _X_num):

        TestCls = NanStandardizer()

        # python 1D list accepted
        out = TestCls.transform(list(_X_num[:, 0]), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, _X_num[:, 0], equal_nan=True)

        # python 1D tuple accepted
        out = TestCls.transform(tuple(_X_num[:, 0]), copy=True)
        assert isinstance(out, tuple)
        assert np.array_equal(out, _X_num[:, 0], equal_nan=True)

        # python 1D set rejected
        with pytest.raises(TypeError):
            TestCls.transform(set(_X_num[:, 0]), copy=True)

        # np 1D accepted
        out = TestCls.transform(np.array(_X_num[:, 0]), copy=True)
        assert isinstance(out, np.ndarray)
        assert np.array_equal(out, _X_num[:, 0], equal_nan=True)

        # pd series accepted
        out = TestCls.transform(pd.Series(_X_num[:, 0]), copy=True)
        assert isinstance(out, pd.Series)
        assert np.array_equal(out, _X_num[:, 0], equal_nan=True)

        # polars series accepted
        out = TestCls.transform(pl.Series(_X_num[:, 0]), copy=True)
        assert isinstance(out, pl.Series)
        assert np.array_equal(out, _X_num[:, 0], equal_nan=True)

        # python 2D list accepted
        out = TestCls.transform(list(map(list, _X_num)), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, _X_num, equal_nan=True)

        # python 2D tuple accepted
        out = TestCls.transform(tuple(map(tuple, _X_num)), copy=True)
        assert isinstance(out, tuple)
        assert np.array_equal(out, _X_num, equal_nan=True)

        # np 2D accepted
        out = TestCls.transform(_X_num, copy=True)
        assert isinstance(out, np.ndarray)
        assert np.array_equal(out, _X_num, equal_nan=True)

        # pd DataFrame accepted
        out = TestCls.transform(pd.DataFrame(_X_num, copy=True))
        assert isinstance(out, pd.DataFrame)
        assert np.array_equal(out.to_numpy(), _X_num, equal_nan=True)

        # polars 2D accepted
        out = TestCls.transform(pl.DataFrame(_X_num), copy=True)

        assert isinstance(out, pl.DataFrame)
        assert all(map(
            np.array_equal,
            out.to_numpy(),
            _X_num,
            (True for _ in out)
        ))





