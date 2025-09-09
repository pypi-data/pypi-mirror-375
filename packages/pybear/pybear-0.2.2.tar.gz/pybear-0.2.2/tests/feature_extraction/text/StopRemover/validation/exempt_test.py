# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd
import polars as pl

from pybear.feature_extraction.text._StopRemover._validation._exempt import \
    _val_exempt



class TestExempt:


    @pytest.mark.parametrize('_dim', (1,2))
    @pytest.mark.parametrize('_dtype', ('str', 'num'))
    @pytest.mark.parametrize('_container',
        (list, tuple, set, np.array, pd.DataFrame, pl.DataFrame)
    )
    def test_accuracy(self, _dim, _dtype, _container, X_np, _shape):


        assert _dim in [1, 2]

        if _dim == 2 and _container is set:
            pytest.skip(reason=f"cannot have 2D set")

        if _dtype == 'str':
            _base_exempt = np.random.choice(list('abcdef'), _shape)
        elif _dtype == 'num':
            _base_exempt = X_np
        else:
            raise Exception

        if _container in (list, tuple, set):
            if _dim == 1:
                _exempt = _container(_base_exempt[:, 0])
                assert isinstance(_exempt, _container)
            elif _dim == 2:
                _exempt = _container(map(_container, _base_exempt))
                assert isinstance(_exempt, _container)
        elif _container is np.array:
            if _dim == 1:
                _exempt = _container(_base_exempt[:, 0])
                assert isinstance(_exempt, np.ndarray)
            elif _dim == 2:
                _exempt = _container(_base_exempt)
                assert isinstance(_exempt, np.ndarray)
        elif _container is pd.DataFrame:
            if _dim == 1:
                _exempt = pd.Series(_base_exempt[:, 0])
                assert isinstance(_exempt, pd.Series)
            elif _dim == 2:
                _exempt = pd.DataFrame(_base_exempt)
                assert isinstance(_exempt, pd.DataFrame)
        elif _container is pl.DataFrame:
            if _dim == 1:
                _exempt = pl.Series(_base_exempt[:, 0])
                assert isinstance(_exempt, pl.Series)
            elif _dim == 2:
                _exempt = pl.from_numpy(_base_exempt)
                assert isinstance(_exempt, pl.DataFrame)
        else:
            raise Exception


        _will_raise = False
        if _dtype == 'num':
            _will_raise = True
        if _dim == 2:
            _will_raise = True
            
        
        if _will_raise:
            with pytest.raises(Exception):
                _val_exempt(_exempt)
        else:
            assert _val_exempt(_exempt) is None



