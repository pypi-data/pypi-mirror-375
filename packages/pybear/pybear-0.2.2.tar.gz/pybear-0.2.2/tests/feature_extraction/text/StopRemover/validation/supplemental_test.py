# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd
import polars as pl

from pybear.feature_extraction.text._StopRemover._validation._supplemental \
    import _val_supplemental



class TestSupplemental:


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
            _base_supp = np.random.choice(list('abcdef'), _shape)
        elif _dtype == 'num':
            _base_supp = X_np
        else:
            raise Exception

        if _container in (list, tuple, set):
            if _dim == 1:
                _supp = _container(_base_supp[:, 0])
                assert isinstance(_supp, _container)
            elif _dim == 2:
                _supp = _container(map(_container, _base_supp))
                assert isinstance(_supp, _container)
        elif _container is np.array:
            if _dim == 1:
                _supp = _container(_base_supp[:, 0])
                assert isinstance(_supp, np.ndarray)
            elif _dim == 2:
                _supp = _container(_base_supp)
                assert isinstance(_supp, np.ndarray)
        elif _container is pd.DataFrame:
            if _dim == 1:
                _supp = pd.Series(_base_supp[:, 0])
                assert isinstance(_supp, pd.Series)
            elif _dim == 2:
                _supp = pd.DataFrame(_base_supp)
                assert isinstance(_supp, pd.DataFrame)
        elif _container is pl.DataFrame:
            if _dim == 1:
                _supp = pl.Series(_base_supp[:, 0])
                assert isinstance(_supp, pl.Series)
            elif _dim == 2:
                _supp = pl.from_numpy(_base_supp)
                assert isinstance(_supp, pl.DataFrame)
        else:
            raise Exception


        _will_raise = False
        if _dtype == 'num':
            _will_raise = True
        if _dim == 2:
            _will_raise = True
            
        
        if _will_raise:
            with pytest.raises(Exception):
                _val_supplemental(_supp)
        else:
            assert _val_supplemental(_supp) is None



