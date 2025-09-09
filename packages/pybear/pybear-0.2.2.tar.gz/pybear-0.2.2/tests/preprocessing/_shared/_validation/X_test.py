# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd
import polars as pl

from pybear.preprocessing.__shared._validation._X import _val_X



class TestValX:

    # fixture ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    @staticmethod
    @pytest.fixture(scope='module')
    def _shape():
        return (200, 37)


    @staticmethod
    @pytest.fixture(scope='module')
    def _X_np(_X_factory, _shape):

        return _X_factory(
            _format='np',
            _dtype='flt',
            _shape=_shape
        )

    # END fixture ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    def test_X_cannot_be_none(self):

        with pytest.raises(TypeError):
            _val_X(None)


    @pytest.mark.parametrize('junk_X',
        (0, 1, True, 'junk', [1, 2], (1, 2), {1, 2}, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk(self, junk_X):

        with pytest.raises(TypeError):
            _val_X(junk_X)


    @pytest.mark.parametrize('X_format', (list, tuple))
    def test_rejects_py_builtin(self, _X_np, X_format):

        _X = X_format(map(X_format, _X_np))

        with pytest.raises(TypeError):
            _val_X(_X)


    def test_rejects_bad_container(self, _X_np, _columns, _shape):

        with pytest.raises(TypeError):
            assert _val_X(pd.Series(_X_np[:, 0]))

        with pytest.raises(TypeError):
            assert _val_X(pl.Series(_X_np[:, 0]))


    def test_numpy_recarray(self, _X_np, _shape):

        _columns = list('abcdefghijklmnopqrstuv')[:_shape[1]]
        _dtypes1 = [np.uint8 for _ in range(_shape[1]//2)]
        _dtypes2 = ['<U1' for _ in range(_shape[1]//2)]
        _formats = [list(zip(_columns, _dtypes1 + _dtypes2))]

        X_REC = np.recarray(
            (_shape[0],), names=_columns, formats=_formats, buf=_X_np
        )
        del _dtypes1, _dtypes2, _formats

        with pytest.raises(TypeError):
            _val_X(X_REC)

        del _X_np, X_REC


    def test_numpy_masked_array(self, _X_np):
        with pytest.warns():
            _val_X(np.ma.array(_X_np))


    @pytest.mark.parametrize('X_format',
        ('np', 'pd', 'pl', 'csr_array', 'csr_matrix', 'csc_array', 'csc_matrix',
        'coo_array', 'coo_matrix', 'dia_array', 'dia_matrix', 'lil_array',
        'lil_matrix', 'dok_array', 'dok_matrix', 'bsr_array', 'bsr_matrix')
    )
    def test_accepts_np_pd_pl_ss(self, _X_factory, _shape, X_format):

        _X = _X_factory(
            _format=X_format,
            _dtype='flt',
            _shape=_shape
        )

        _val_X(_X)







