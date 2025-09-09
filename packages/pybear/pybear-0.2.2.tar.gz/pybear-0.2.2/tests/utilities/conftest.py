# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from typing import (
    Any,
    Iterable,
    Literal,
    TypeAlias
)
import numpy.typing as npt

from uuid import uuid4
import warnings

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss


XContainer: TypeAlias = Literal[
    'np', 'pd', 'pl', 'csr_matrix', 'csc_matrix', 'coo_matrix',
    'dia_matrix', 'lil_matrix', 'bsr_matrix', 'csr_array', 'csc_array',
    'coo_array', 'dia_array', 'lil_array', 'bsr_array'
]


# these fixtures are identical to those in ColumnDeduplicator
# these are for diagnosing nan detection issues with nan_masking modules


@pytest.fixture(scope='session')
def _shape():
    return (10, 10)


@pytest.fixture(scope='session')
def _master_columns():
    _cols = 200
    while True:
        _ = [str(uuid4())[:8] for _ in range(_cols)]
        if len(np.unique(_)) == len(_):
            return np.array(_, dtype='<U4')


@pytest.fixture(scope='module')
def _columns(_master_columns, _shape):

    return _master_columns.copy()[:_shape[1]]


@pytest.fixture(scope='module')
def _X_factory(_shape):


    def _idx_getter(_rows, _zeros):
        return np.random.choice(range(_rows), int(_rows*_zeros), replace=False)


    def foo(
        _dupl:list[list[int]] = None,
        _has_nan:int | bool = False,
        _format:XContainer = 'np',
        _dtype:Literal['flt','int','str','obj','hybrid'] = 'flt',
        _columns:Iterable[str] | None = None,
        _zeros:float | None = 0,
        _shape:tuple[int,int] = (20,5)
    ) -> npt.NDArray[Any]:

        # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        assert isinstance(_dupl, (list, type(None)))
        if _dupl is not None:
            for idx, _set in enumerate(_dupl):
                assert isinstance(_set, list)
                assert all(map(isinstance, _set, (int for _ in _set)))
                assert len(_set) >= 2, f'_dupl sets must have at least 2 entries'

            # make sure sets are sorted ascending, and first entries are asc
            __ = {_set[0]: sorted(_set) for _set in _dupl}
            _dupl = [__[k] for k in sorted(list(__.keys()))]
            del __

        assert isinstance(_has_nan, (bool, int, float))
        if not isinstance(_has_nan, bool):
            assert int(_has_nan) == _has_nan, \
                f"'_has_nan' must be bool or int >= 0"
        assert _has_nan >= 0, f"'_has_nan' must be bool or int >= 0"
        assert _format in ['np', 'pd', 'pl', 'csr_matrix', 'csc_matrix',
            'coo_matrix', 'dia_matrix', 'lil_matrix', 'bsr_matrix', 'dok_matrix',
            'csr_array', 'csc_array', 'coo_array', 'dia_array', 'lil_array',
            'bsr_array', 'dok_array'
        ], f"'_format' must be 'np', 'pd', 'pl', or any scipy sparse except dok"
        assert _dtype in ['flt','int','str','obj','hybrid']
        assert isinstance(_columns, (list, np.ndarray, type(None)))
        if _columns is not None:
            assert all(map(isinstance, _columns, (str for _ in _columns)))

        if _zeros is None:
            _zeros = 0
        assert not isinstance(_zeros, bool)
        assert isinstance(_zeros, (float, int))
        assert 0 <= _zeros <= 1, f"zeros must be 0 <= x <= 1"

        if _format not in ('np', 'pd', 'pl', 'lil_matrix', 'dok_matrix',
            'lil_array', 'dok_array') and _dtype in ('str', 'obj', 'hybrid'):
            raise ValueError(
                f"cannot create scipy sparse with str, obj, or hybrid dtypes"
            )

        assert isinstance(_shape, tuple)
        assert all(map(isinstance, _shape, (int for _ in _shape)))
        if _shape[0] < 1:
            raise AssertionError(f"'shape' must have at least one example")
        if _shape[1] < 2:
            raise AssertionError(f"'shape' must have at least 2 columns")

        assert _has_nan <= _shape[0], f"'_has_nan' must be <= n_rows"
        # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        if _dtype == 'flt':
            X = np.random.uniform(0, 1, _shape)
            if _zeros:
                for _col_idx in range(_shape[1]):
                    X[_idx_getter(_shape[0], _zeros), _col_idx] = 0
        elif _dtype == 'int':
            X = np.random.randint(0, 10, _shape)
            if _zeros:
                for _col_idx in range(_shape[1]):
                    X[_idx_getter(_shape[0], _zeros), _col_idx] = 0
        elif _dtype == 'str':
            X = np.random.choice(list('abcdefghijk'), _shape, replace=True)
            X = X.astype('<U10')
        elif _dtype == 'obj':
            X = np.random.choice(list('abcdefghijk'), _shape, replace=True)
            X = X.astype(object)
        elif _dtype == 'hybrid':
            _col_shape = (_shape[0], 1)
            X = np.random.uniform(0, 1, _col_shape).astype(object)
            if _zeros:
                X[_idx_getter(_shape[0], _zeros), 0] = 0
            for _cidx in range(1, _shape[1]):
                if _cidx % 3 == 0:
                    _ = np.random.uniform(0, 1, _col_shape)
                    if _zeros:
                        _[_idx_getter(_shape[0], _zeros), 0] = 0
                elif _cidx % 3 == 1:
                    _ = np.random.randint(0, 10, _col_shape)
                    if _zeros:
                        _[_idx_getter(_shape[0], _zeros), 0] = 0
                elif _cidx % 3 == 2:
                    _ = np.random.choice(list('abcdefghijk'), _col_shape)
                else:
                    raise Exception
                X = np.hstack((X, _))
            del _col_shape, _, _cidx
        else:
            raise Exception

        if _dupl is not None:
            for _set in _dupl:
                for _idx in _set[1:]:
                    X[:, _idx] = X[:, _set[0]]
            try:
                del _set, _idx
            except:
                pass


        if _format == 'pd':
            X = pd.DataFrame(data=X, columns=_columns)
        # do conversion to sparse/polars after nan sprinkle


        if _has_nan:

            if _format == 'pd':
                if _dtype in ['flt', 'int']:
                    _choices = [np.nan, pd.NA, None, 'nan', 'NaN', 'NAN', '<NA>']
                else:
                    _choices = [np.nan, pd.NA, None, 'nan', 'NaN', 'NAN', '<NA>']
            else:
                if _dtype == 'flt':
                    _choices = [np.nan, None, 'nan', 'NaN', 'NAN']
                elif _dtype == 'int':
                    warnings.warn(
                        f"attempting to put nans into an integer dtype, "
                        f"converted to float"
                    )
                    X = X.astype(np.float64)
                    _choices = [np.nan, None, 'nan', 'NaN', 'NAN']
                else:
                    _choices = [np.nan, pd.NA, None, 'nan','NaN','NAN']


            # determine how many nans to sprinkle based on _shape and _has_nan
            if _has_nan is True:
                _sprinkles = max(3, _shape[0] // 10)
            else:
                _sprinkles = _has_nan

            for _c_idx in range(_shape[1]):
                _r_idxs = np.random.choice(
                    range(_shape[0]), _sprinkles, replace=False
                )
                for _r_idx in _r_idxs:
                    if _format == 'pd':
                        X.iloc[_r_idx, _c_idx] = np.random.choice(_choices)
                    else:
                        if _dtype in ('str', 'obj'):
                            # it is important to do the str()
                            X[_r_idx, _c_idx] = str(np.random.choice(_choices))
                        else:
                            X[_r_idx, _c_idx] = np.random.choice(_choices)

            del _sprinkles

        # do this after sprinkling the nans
        if _format == 'np':
            pass
        elif _format == 'pd':
            pass
        elif _format == 'pl':
            X = pl.from_numpy(X, schema={None: None}.get(_columns, list(_columns)))
        elif _format == 'csr_matrix':
            X = ss._csr.csr_matrix(X)
        elif _format == 'csc_matrix':
            X = ss._csc.csc_matrix(X)
        elif _format == 'coo_matrix':
            X = ss._coo.coo_matrix(X)
        elif _format == 'dia_matrix':
            X = ss._dia.dia_matrix(X)
        elif _format == 'lil_matrix':
            X = ss._lil.lil_matrix(X)
        elif _format == 'bsr_matrix':
            X = ss._bsr.bsr_matrix(X)
        elif _format == 'dok_matrix':
            X = ss._dok.dok_matrix(X)
        elif _format == 'csr_array':
            X = ss._csr.csr_array(X)
        elif _format == 'csc_array':
            X = ss._csc.csc_array(X)
        elif _format == 'coo_array':
            X = ss._coo.coo_array(X)
        elif _format == 'dia_array':
            X = ss._dia.dia_array(X)
        elif _format == 'lil_array':
            X = ss._lil.lil_array(X)
        elif _format == 'bsr_array':
            X = ss._bsr.bsr_array(X)
        elif _format == 'dok_array':
            X = ss._dok.dok_array(X)
        else:
            raise Exception

        return X


    return foo




