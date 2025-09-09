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

from pybear.preprocessing._NanStandardizer._validation._X import _val_X



class TestValX:


    @pytest.mark.parametrize('junk_X',
        (-2.7, -1, 0, 1, 2.7, True, False, None, 'garbage', {1,2,3}, {'A':1},
         lambda x: x)
    )
    def test_rejects_junk(self, junk_X):

        # includes sets

        with pytest.raises(TypeError):
            _val_X(junk_X)


    def test_rejects_dok_lil(self, X_np):

        _X = ss.dok_matrix(X_np)
        with pytest.raises(TypeError):
            _val_X(_X)


        _X = ss.dok_array(X_np)
        with pytest.raises(TypeError):
            _val_X(_X)


        _X = ss.lil_matrix(X_np)
        with pytest.raises(TypeError):
            _val_X(_X)


        _X = ss.lil_array(X_np)
        with pytest.raises(TypeError):
            _val_X(_X)


    @pytest.mark.parametrize('_dim', (1,2))
    @pytest.mark.parametrize('X_format',
        ('py_list', 'py_tuple', 'ndarray', 'pd', 'pl', 'ss_csr_mat',
         'ss_csr_arr', 'ss_csc_mat', 'ss_csc_arr', 'ss_coo_mat', 'ss_coo_arr')
    )
    def test_accepts_good_X(self, _dim, X_format, X_np):

        # skip impossible -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        if _dim == 1 and 'ss' in X_format:
            pytest.skip(reason=f'cant have 1D scipy sparse')
        # END skip impossible -- -- -- -- -- -- -- -- -- -- -- -- -- -- -

        if X_format == 'py_list':
            if _dim == 1:
                _X = list(X_np[:, 0])
            elif _dim == 2:
                _X = list(map(list, X_np))
        elif X_format == 'py_tuple':
            if _dim == 1:
                _X = tuple(X_np[:, 0])
            elif _dim == 2:
                _X = tuple(map(tuple, X_np))
        elif X_format == 'ndarray':
            if _dim == 1:
                _X = X_np[:, 0]
            elif _dim == 2:
                _X = X_np
        elif X_format == 'pd':
            if _dim == 1:
                _X = pd.Series(X_np[:, 0])
            elif _dim == 2:
                _X = pd.DataFrame(X_np)
        elif X_format == 'pl':
            if _dim == 1:
                _X = pl.Series(X_np[:, 0])
            elif _dim == 2:
                _X = pl.DataFrame(X_np)
        elif X_format == 'ss_csr_mat':
            _X = ss.csr_matrix(X_np)
        elif X_format == 'ss_csr_arr':
            _X = ss.csr_array(X_np)
        elif X_format == 'ss_csc_mat':
            _X = ss.csc_matrix(X_np)
        elif X_format == 'ss_csc_arr':
            _X = ss.csc_array(X_np)
        elif X_format == 'ss_coo_mat':
            _X = ss.coo_matrix(X_np)
        elif X_format == 'ss_coo_arr':
            _X = ss.coo_array(X_np)
        else:
            raise Exception

        assert _val_X(_X) is None





