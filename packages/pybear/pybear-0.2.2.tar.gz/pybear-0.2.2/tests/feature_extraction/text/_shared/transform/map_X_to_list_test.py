# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import random
from string import (
    ascii_lowercase,
    ascii_uppercase
)

import numpy as np
import pandas as pd
import polars as pl

from pybear.feature_extraction.text.__shared._transform._map_X_to_list import \
    _map_X_to_list

from pybear.utilities import nan_mask



class TestMapXToListAccuracy:


    # def _map_X_to_list(
    #     _X: Dim1Types | Dim2Types
    # ) -> list[str] | list[list[str]]:


    @pytest.mark.parametrize('_container',
        ('py_list', 'py_tuple', 'py_set', 'np', 'pd_w_name', 'pd_wo_name',
         'pl_w_name', 'pl_wo_name')
    )
    def test_accuracy_1D(self, _container):

        _shape = (10, )

        while True:
            # all unique strings so set does not shrink
            _base_X = np.random.choice(list(ascii_lowercase), _shape, replace=True)
            if len(np.unique(_base_X)) == _shape[0]:
                break

        if _container == 'py_list':
            _X = list(map(str, _base_X.tolist()))
        elif _container == 'py_tuple':
            _X = tuple(map(str, _base_X.tolist()))
        elif _container == 'py_set':
            _X = set(map(str, _base_X.tolist()))
        elif _container == 'np':
            _X = _base_X.copy()
        elif _container == 'pd_w_name':
            _X = pd.Series(data=_base_X.copy(), name='TEXT')
        elif _container == 'pd_wo_name':
            _X = pd.Series(data=_base_X.copy())
        elif _container == 'pl_w_name':
            _X = pl.Series(name='TEXT', values=_base_X.copy())
        elif _container == 'pl_wo_name':
            _X = pl.Series(values=_base_X.copy())
        else:
            raise Exception


        out = _map_X_to_list(_X)

        assert isinstance(out, list)
        assert np.array(out).shape == _shape
        assert all(map(isinstance, out, (str for _ in out)))
        if _container == 'py_set':
            assert np.array_equal(sorted(out), sorted(list(_X)))
        else:
            assert np.array_equal(out, _base_X)


    @pytest.mark.parametrize('_container',
        ('py_list', 'py_tuple', 'np', 'pd_w_header', 'pd_wo_header',
         'pl_w_header', 'pl_wo_header')
    )
    def test_accuracy_2D(self, _container):

        _shape = (37, 1)

        _base_X = np.random.choice(list(ascii_lowercase), _shape, replace=True)
        _columns = list(ascii_uppercase)[:_shape[1]]

        if _container == 'py_list':
            _X = list(map(list, _base_X))
        elif _container == 'py_tuple':
            _X = tuple(map(tuple, _base_X))
        elif _container == 'np':
            _X = _base_X.copy()
        elif _container == 'pd_wo_header':
            _X = pd.DataFrame(_base_X.copy())
        elif _container == 'pd_w_header':
            _X = pd.DataFrame(_base_X.copy(), columns=_columns)
        elif _container == 'pl_wo_header':
            _X = pl.DataFrame(_base_X.copy())
        elif _container == 'pl_w_header':
            _X = pl.DataFrame(_base_X.copy(), schema=list(_columns))
        else:
            raise Exception

        out = _map_X_to_list(_X)

        assert isinstance(out, list)

        # shape of py lists must be identical to given
        assert len(out) == _shape[0]
        lens = list(map(len, out))
        unq_lens = np.unique(lens)
        assert len(unq_lens) == 1
        assert unq_lens[0] == _shape[1]

        for idx, row in enumerate(out):
            assert isinstance(row, list)
            assert all(map(isinstance, row, (str for _ in row)))
            assert np.array_equal(row, _base_X[idx])



class TestMapXToListNanHandling:


    @pytest.mark.parametrize('_container',
        ('py_list', 'py_tuple', 'np', 'pd_w_name', 'pd_wo_name',
         'pl_w_name', 'pl_wo_name')
    )
    @pytest.mark.parametrize(f'nan_type', (np.nan, pd.NA, 'nan', None))
    def test_nan_handling_1D(self, _container, nan_type):

        # not testing py_set, because of the sorting

        # only pass None as nan-like to polars
        if 'pl_w' in _container and nan_type is not None:
            pytest.skip(reason=f'only use None as nan-like in polars')


        _base_X = [
            'First line.',
            'Second line.',
            'Third line.',
            nan_type
        ]

        if _container == 'py_list':
            _X = _base_X
        elif _container == 'py_tuple':
            _X = tuple(_base_X)
        elif _container == 'py_set':
            _X = set(_base_X)
        elif _container == 'np':
            _X = np.array(_base_X)
        elif _container == 'pd_w_name':
            _X = pd.Series(data=_base_X, name='TEXT')
        elif _container == 'pd_wo_name':
            _X = pd.Series(data=_base_X)
        elif _container == 'pl_w_name':
            _X = pl.Series(name='TEXT', values=_base_X)
        elif _container == 'pl_wo_name':
            _X = pl.Series(values=_base_X)
        else:
            raise Exception

        assert np.array_equal(
            nan_mask(_X),
            [False, False, False, True]
        )

        out = _map_X_to_list(_X)

        assert np.array_equiv(
            nan_mask(out),
            [False, False, False, True]
        )

        assert all(map(isinstance, out, (str for i in out)))


    @pytest.mark.parametrize('_container',
        ('py_list', 'py_tuple', 'np', 'pd_w_hdr', 'pd_wo_hdr',
         'pl_w_hdr', 'pl_wo_hdr')
    )
    @pytest.mark.parametrize(f'nan_type', (np.nan, pd.NA, 'nan', None))
    def test_nan_handling_2D(self, _container, nan_type):

        # only pass None as nan-like to polars
        if 'pl_w' in _container and nan_type is not None:
            pytest.skip(reason=f'only use None as nan-like in polars')

        _shape = (37, 1)

        _base_X = np.random.choice(
            list(ascii_lowercase), _shape, replace=True
        ).astype(object)
        _columns = list(ascii_uppercase)[:_shape[1]]

        # random splatter some nans
        for n in range(5):
            _row_idx = random.choice(range(_shape[0]))
            _col_idx = random.choice(range(_shape[1]))
            _base_X[_row_idx, _col_idx] = nan_type


        if _container == 'py_list':
            _X = _base_X
        elif _container == 'py_tuple':
            _X = tuple(map(tuple, _base_X))
        elif _container == 'np':
            _X = np.array(_base_X)
        elif _container == 'pd_w_hdr':
            _X = pd.DataFrame(data=_base_X, columns=_columns)
        elif _container == 'pd_wo_hdr':
            _X = pd.DataFrame(data=_base_X)
        elif _container == 'pl_w_hdr':
            _X = pl.from_numpy(data=_base_X, schema=list(_columns))
        elif _container == 'pl_wo_hdr':
            _X = pl.from_numpy(data=_base_X)
        else:
            raise Exception

        og_nan_mask = nan_mask(_X)

        out = _map_X_to_list(_X)

        out_nan_mask = nan_mask(out)

        assert np.array_equal(og_nan_mask, out_nan_mask)

        assert all(map(lambda y: map(isinstance, y, (str for i in y)), out))





