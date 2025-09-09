# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd
import polars as pl

from pybear.feature_extraction.text._StopRemover._validation._validation \
    import _validation


class TestValidation:

    # the brunt of the testing is done on the individual modules, just
    # make sure the hub passes all good


    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_container', ('list', 'tuple', 'np', 'pd', 'pl'))
    @pytest.mark.parametrize('_dtype', ('str', 'num'))
    @pytest.mark.parametrize('_match_callable', (lambda x,y: f"{x}{y}", None, 'abc'))
    @pytest.mark.parametrize('_delete_empty_rows', (True, False, 'abc'))
    @pytest.mark.parametrize('_exempt', (list('abc'), None))
    @pytest.mark.parametrize('_supplemental', (list('abc'), None))
    @pytest.mark.parametrize('_n_jobs', (1, None))
    def test_accuracy(
        self, _dim, _container, _dtype, _match_callable, _delete_empty_rows,
        _exempt, _supplemental, _n_jobs, X_np, _shape
    ):

        if _dtype == 'str':
            _base_X = np.random.choice(list('abcde'), _shape, replace=True)
        elif _dtype == 'num':
            _base_X = X_np
        else:
            raise Exception

        assert _dim in [1,2]

        if _container == 'list':
            if _dim == 1:
                _X = list(_base_X[:, 0])
            elif _dim == 2:
                _X = list(map(list, _base_X))
        elif _container == 'tuple':
            if _dim == 1:
                _X = tuple(_base_X[:, 0])
            elif _dim == 2:
                _X = tuple(map(tuple, _base_X))
        elif _container == 'np':
            if _dim == 1:
                _X = _base_X[:, 0]
            elif _dim == 2:
                _X = _base_X.copy()
        elif _container == 'pd':
            if _dim == 1:
                _X = pd.Series(_base_X[:, 0])
            elif _dim == 2:
                _X = pd.DataFrame(_base_X)
        elif _container == 'pl':
            if _dim == 1:
                _X = pl.Series(_base_X[:, 0])
            elif _dim == 2:
                _X = pl.from_numpy(_base_X)
        else:
            raise Exception


        _will_raise = False
        if _dim == 1:
            _will_raise = True
        if _dtype == 'num':
            _will_raise = True
        if not _match_callable is None and not callable(_match_callable):
            _will_raise = True
        if not isinstance(_delete_empty_rows, bool):
            _will_raise = True


        if _will_raise:
            with pytest.raises(Exception):
                _validation(
                    _X,
                    _match_callable,
                    _delete_empty_rows,
                    _exempt,
                    _supplemental,
                    _n_jobs
                )
        else:
            out = _validation(
                    _X,
                    _match_callable,
                    _delete_empty_rows,
                    _exempt,
                    _supplemental,
                    _n_jobs
                )
            assert out is None






