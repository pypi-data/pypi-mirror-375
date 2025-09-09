# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

from pybear.base._cast_to_ndarray import cast_to_ndarray
from pybear.utilities._nan_masking import nan_mask



class TestCastToNDArray:

    # shape must be preserved
    # original dtype must be preserved

    # test validation v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

    @pytest.mark.parametrize('junk_copy_X',
        (-2.7, -1, 0, 1, 2.7, None, 'trash', [0,1], (0,1), {'A':1}, lambda x: x)
    )
    def test_copy_X_rejects_non_bool(self, junk_copy_X):
        with pytest.raises(TypeError):
            cast_to_ndarray(
                np.random.randint(0, 10, (10,3)),
                copy_X=junk_copy_X
            )


    @pytest.mark.parametrize('_copy_X',  (True, False))
    def test_copy_X_accepts_bool(self, _copy_X):

        out = cast_to_ndarray(
            np.random.randint(0, 10, (10,3)),
            copy_X=_copy_X
        )

        assert isinstance(out, np.ndarray)


    @pytest.mark.parametrize('junk_X',
        (-2.7, -1, 0, 1, 2, True, False, None, 'junk', {'a': 1}, lambda x: x)
    )
    def test_blocks_non_array_like(self, junk_X):

        with pytest.raises(TypeError):
            cast_to_ndarray(junk_X)


    def test_blocks_oddball_containers(self):

        with pytest.raises(TypeError):
            cast_to_ndarray(np.recarray((1,2,3), dtype=np.float64))

    # END test validation v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^


    @pytest.mark.parametrize('_dim', (1,2))
    @pytest.mark.parametrize('_container', (list, tuple, set))
    @pytest.mark.parametrize('_dtype', ('flt', 'int', 'str'))
    @pytest.mark.parametrize('_has_nan', (True, False))
    def test_python_builtins(
        self, _X_factory, _shape, _dim, _container, _dtype, _has_nan
    ):

        # skip impossible -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        if _container is set and _dim == 2:
            pytest.skip(f'cant have 2D sets')
        # END skip impossible -- -- -- -- -- -- -- -- -- -- -- -- -- --

        _X_base_np = _X_factory(
            _dupl=None,
            _has_nan=_has_nan,
            _format='np',
            _dtype=_dtype,
            _columns=None,
            _constants=None,
            _zeros=None,
            _shape=_shape
        )

        if _dim == 1:
            _X = _X_base_np[:, 0].tolist()
            _X = _container(list(_X))
            assert isinstance(_X, _container)
            _ref_X = deepcopy(_X)
        elif _dim == 2:
            _X = _container(map(_container, _X_base_np))
            assert isinstance(_X, _container)
            assert all(map(isinstance, _X, (_container for _ in _X)))
            _ref_X = deepcopy(_X)
        else:
            raise Exception

        _ref_X = np.array(list(_ref_X))

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        # convert nans in _ref_X to np.nan, which is what cast_to_ndarray
        # should be doing.
        # _ref_X must be np
        assert isinstance(_ref_X, np.ndarray)
        try:
            _og_dtype = _ref_X.dtype
            _ref_X = _ref_X.astype(np.float64)
            _ref_X[nan_mask(_ref_X)] = np.nan
            _ref_X = _ref_X.astype(_og_dtype)
            del _og_dtype
        except:
            # can only kick out to here if non-numeric
            try:
                _ref_X[nan_mask(_ref_X)] = np.nan
            except:
                pass
        # END # convert nans in _ref_X to np.nan ** * ** * ** * ** * **

        out = cast_to_ndarray(_X)

        # assertions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        assert isinstance(out, np.ndarray)

        if _dim == 1:
            assert len(out.shape) == 1
        elif _dim == 2:
            assert len(out.shape) == 2

        if _dtype in ['flt', 'int']:
            if _dtype == 'flt' or _has_nan:
                assert out.dtype == np.float64
            elif _dtype == 'int':  # and not _has_nan
                assert 'int' in str(out.dtype).lower()

            if _container is set:
                assert np.array_equal(
                    sorted(list(out)),
                    sorted(list(_ref_X)),
                    equal_nan=True
                )
            else:
                assert np.array_equal(out, _ref_X, equal_nan=True)
        elif _dtype == 'str':
            assert '<U' in str(out.dtype).upper()
            if _container is set:
                assert np.array_equal(
                    sorted(list(out)),
                    sorted(list(_ref_X))
                )
            else:
                assert np.array_equal(out, _ref_X)
        else:
            raise Exception


    @pytest.mark.parametrize('_container', (list, tuple))
    @pytest.mark.parametrize('_dtype', ('flt', 'int', 'str'))
    @pytest.mark.parametrize('_has_nan', (True, False))
    def test_ragged_python_builtins(
        self, _X_factory, _shape, _container, _dtype, _has_nan
    ):

        # can only be 2D

        _X_base_np = _X_factory(
            _dupl=None,
            _has_nan=_has_nan,
            _format='np',
            _dtype=_dtype,
            _columns=None,
            _constants=None,
            _zeros=None,
            _shape=_shape
        )

        _X = list(map(list, _X_base_np))
        for row_idx in range(len(_X)):
            rand_len = np.random.randint(_shape[1]//2, _shape[1]+1)
            _X[row_idx] = _X[row_idx][:rand_len]

        _X = _container(map(_container, _X))
        assert isinstance(_X, _container)
        assert all(map(isinstance, _X, (_container for _ in _X)))

        with pytest.raises(ValueError):
            cast_to_ndarray(_X)


    @pytest.mark.parametrize('_dim', (1,2))
    @pytest.mark.parametrize('_container', (np.array, np.ma.masked_array))
    @pytest.mark.parametrize('_dtype', ('flt', 'int', 'str'))
    @pytest.mark.parametrize('_has_nan', (True, False))
    def test_numpy(
        self, _X_factory, _shape, _dim, _container, _dtype, _has_nan
    ):

        # skip impossible ** * ** * ** * ** * ** * ** * ** * ** * ** *
        if _has_nan and _dtype == 'int':
            pytest.skip(reason=f'int dtypes cant take nan')
        # END skip impossible ** * ** * ** * ** * ** * ** * ** * ** * **

        _X_base_np = _X_factory(
            _dupl=None,
            _has_nan=_has_nan,
            _format='np',
            _dtype=_dtype,
            _columns=None,
            _constants=None,
            _zeros=None,
            _shape=_shape
        )

        if _dim == 1:
            _ref_X = _X_base_np[:, 0].copy()
            _X = _X_base_np[:, 0]
            _X = _container(_X)
        elif _dim == 2:
            _ref_X = _X_base_np.copy()
            _X = _X_base_np
        else:
            raise Exception


        if _container is np.array:
            assert isinstance(_X, np.ndarray)
        elif _container is np.array:
            assert isinstance(_X, np.ma.MaskedArray)

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        # convert nans in _ref_X to np.nan, which is what cast_to_ndarray
        # should be doing.
        # _ref_X must be np
        assert isinstance(_ref_X, np.ndarray)
        try:
            _og_dtype = _ref_X.dtype
            _ref_X = _ref_X.astype(np.float64)
            _ref_X[nan_mask(_ref_X)] = np.nan
            _ref_X = _ref_X.astype(_og_dtype)
            del _og_dtype
        except:
            # can only kick out to here if non-numeric
            try:
                _ref_X[nan_mask(_ref_X)] = np.nan
            except:
                pass
        # END # convert nans in _ref_X to np.nan ** * ** * ** * ** * **


        out = cast_to_ndarray(_X)

        # assertions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        assert isinstance(out, np.ndarray)
        assert not isinstance(out, np.ma.MaskedArray)

        if _dim == 1:
            assert len(out.shape) == 1
        elif _dim == 2:
            assert len(out.shape) == 2

        assert out.shape == _ref_X.shape

        if _dtype in ['flt', 'int']:
            if _dtype == 'flt' or _has_nan:
                assert out.dtype == np.float64
                assert np.array_equal(out, _ref_X, equal_nan=True)
            elif _dtype == 'int':   # and not _has_nan
                assert 'int' in str(out.dtype).lower()
                assert np.array_equal(out, _ref_X, equal_nan=True)
        elif _dtype == 'str':
            assert '<U' in str(out.dtype).upper()
            assert np.array_equal(out, _ref_X)
        else:
            raise Exception


    @pytest.mark.parametrize('_container',
        (ss.csc_matrix, ss.csc_array, ss.csr_matrix, ss.csr_array,
         ss.coo_matrix, ss.coo_array, ss.dia_matrix, ss.dia_array,
         ss.lil_matrix, ss.lil_array, ss.dok_matrix, ss.dok_array,
         ss.bsr_matrix, ss.bsr_array)
    )
    @pytest.mark.parametrize('_dtype', ('flt', 'int'))
    @pytest.mark.parametrize('_has_nan', (True, False))
    def test_scipy(self, _X_factory, _shape, _container, _dtype, _has_nan):

        # can only be 2D, can only be numeric

        # skip impossible ** * ** * ** * ** * ** * ** * ** * ** * ** *
        if _has_nan and _dtype == 'int':
            pytest.skip(reason=f'int dtypes cant take nan')
        # END skip impossible ** * ** * ** * ** * ** * ** * ** * ** * **

        _X_base_np = _X_factory(
            _dupl=None,
            _has_nan=_has_nan,
            _format='np',
            _dtype=_dtype,
            _columns=None,
            _constants=None,
            _zeros=None,
            _shape=_shape
        )

        _ref_X = _X_base_np.copy()

        _X = _container(_X_base_np)

        assert isinstance(_X, _container)

        out = cast_to_ndarray(_X)

        # assertions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        assert isinstance(out, np.ndarray)

        assert len(out.shape) == 2

        if _dtype == 'flt' or _has_nan:
            assert out.dtype == np.float64
        elif _dtype == 'int':
            assert 'int' in str(out.dtype).lower()
        else:
            raise Exception

        assert np.array_equal(out, _ref_X, equal_nan=True)


    @pytest.mark.parametrize('_dim', (1,2))
    @pytest.mark.parametrize('_dtype', ('flt', 'int', 'str'))
    @pytest.mark.parametrize('_has_nan', (True, False))
    def test_pandas(self, _X_factory, _shape, _dim, _dtype, _has_nan):

        # skip impossible ** * ** * ** * ** * ** * ** * ** * ** * ** *
        if _has_nan and _dtype == 'int':
            pytest.skip(reason=f'int dtypes cant take nan')
        # END skip impossible ** * ** * ** * ** * ** * ** * ** * ** * **

        _X_base_pd = _X_factory(
            _dupl=None,
            _has_nan=_has_nan,
            _format='pd',
            _dtype=_dtype,
            _columns=None,
            _constants=None,
            _zeros=None,
            _shape=_shape
        )

        if _dim == 1:
            _ref_X = _X_base_pd.iloc[:, 0].copy().squeeze().to_numpy()
            _X = _X_base_pd.iloc[:, 0].squeeze()
        elif _dim == 2:
            _ref_X = _X_base_pd.copy().to_numpy()
            _X = _X_base_pd.copy()
        else:
            raise Exception

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        # convert nans in _ref_X to np.nan, which is what cast_to_ndarray
        # should be doing.
        # _ref_X must be np
        assert isinstance(_ref_X, np.ndarray)
        try:
            _og_dtype = _ref_X.dtype
            _ref_X.astype(np.float64)
            _ref_X[nan_mask(_ref_X)] = np.nan
            _ref_X.dtype = _og_dtype
            del _og_dtype
        except:
            # only kicks out to here if non-numeric
            try:
                _ref_X[nan_mask(_ref_X)] = np.nan
            except:
                pass
        # END # convert nans in _ref_X to np.nan ** * ** * ** * ** * **


        if _dim == 1:
            assert isinstance(_X, pd.Series)
        elif _dim == 2:
            assert isinstance(_X, pd.DataFrame)

        out = cast_to_ndarray(_X)

        # assertions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        assert isinstance(out, np.ndarray)

        if _dim == 1:
            assert len(out.shape) == 1
        elif _dim == 2:
            assert len(out.shape) == 2

        assert out.shape == _ref_X.shape

        if _dtype in ['flt', 'int']:
            if _dtype == 'flt' or _has_nan:
                assert out.dtype == np.float64
            elif _dtype == 'int':
                assert 'int' in str(out.dtype).lower()
            assert np.array_equal(out, _ref_X.astype(np.float64), equal_nan=True)
        elif _dtype == 'str':
            assert out.dtype == object
            assert np.array_equal(
                list(map(str, out)),
                list(map(str, _ref_X))
            )
        else:
            raise Exception


    @pytest.mark.parametrize('_dim', (1,2))
    @pytest.mark.parametrize('_dtype', ('flt', 'int', 'str'))
    @pytest.mark.parametrize('_has_nan', (True, False))
    def test_polars(self, _X_factory, _shape, _dim, _dtype, _has_nan):

        # skip impossible ** * ** * ** * ** * ** * ** * ** * ** * ** *
        if _has_nan and _dtype == 'int':
            pytest.skip(reason=f'int dtypes cant take nan')
        # END skip impossible ** * ** * ** * ** * ** * ** * ** * ** * **

        _X_base_pl = _X_factory(
            _dupl=None,
            _has_nan=_has_nan,
            _format='pl',
            _dtype=_dtype,
            _columns=None,
            _constants=None,
            _zeros=None,
            _shape=_shape
        )

        if _dim == 1:
            _ref_X = _X_base_pl[:, 0].to_numpy()
            assert isinstance(_ref_X, np.ndarray)
            _X = _X_base_pl[:, 0]
            assert isinstance(_X, pl.Series)
        elif _dim == 2:
            _ref_X = _X_base_pl.clone().to_numpy()
            assert isinstance(_ref_X, np.ndarray)
            _X = _X_base_pl
            assert isinstance(_X, pl.DataFrame)
        else:
            raise Exception

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        # convert nans in _ref_X to np.nan, which is what cast_to_ndarray
        # should be doing.
        # _ref_X must be np
        assert isinstance(_ref_X, np.ndarray)
        try:
            _og_dtype = _ref_X.dtype
            _ref_X = _ref_X.astype(np.float64)
            _ref_X[nan_mask(_ref_X)] = np.nan
            _ref_X = _ref_X.astype(_og_dtype)
            del _og_dtype
        except:
            # only kicks into here if non-numeric
            try:
                _ref_X[nan_mask(_ref_X)] = np.nan
            except:
                pass
        # END # convert nans in _ref_X to np.nan ** * ** * ** * ** * **

        if _dim == 1:
            assert isinstance(_X, pl.Series)
        elif _dim == 2:
            assert isinstance(_X, pl.DataFrame)

        out = cast_to_ndarray(_X)

        # assertions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        assert isinstance(out, np.ndarray)

        if _dim == 1:
            assert len(out.shape) == 1
        elif _dim == 2:
            assert len(out.shape) == 2

        assert out.shape == _ref_X.shape

        if _dtype in ['flt', 'int']:
            if _dtype == 'flt':
                assert out.dtype == np.float64
            elif _dtype == 'int':
                assert 'int' in str(_dtype).lower()
            assert np.array_equal(out, _ref_X.astype(np.float64), equal_nan=True)
        elif _dtype == 'str':
            assert out.dtype == object
            assert np.array_equal(
                list(map(str, out)),
                list(map(str, _ref_X))
            )
        else:
            raise Exception






