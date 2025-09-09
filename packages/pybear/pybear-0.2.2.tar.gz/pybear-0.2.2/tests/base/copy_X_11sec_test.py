# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numbers

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

from pybear.base._copy_X import copy_X



class TestCopyX:


    # fixtures v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

    @staticmethod
    @pytest.fixture(scope='function')
    def _X_list_1D(_shape):
        return np.random.randint(0, 10, (_shape[0],)).tolist()


    @staticmethod
    @pytest.fixture(scope='function')
    def _X_list_2D(_shape):
        return np.random.randint(0, 10, _shape).tolist()


    @staticmethod
    @pytest.fixture(scope='function')
    def _container_maker(_X_list_1D, _X_list_2D):

        def foo(_container, _dim):

            assert _dim in [1,2]

            if _dim == 1:
                _X = _X_list_1D
                assert all(map(isinstance, _X, (numbers.Number for _ in _X)))
                if hasattr(_container, 'toarray'):
                    raise TypeError(f"container cant be scipy when 1D")
                elif _container in [pd.DataFrame, pl.DataFrame]:
                    raise TypeError(f"container cant be {_container} when 1D")
                else:
                    out = _container(list(_X))

                # validate object was built correctly -- -- -- -- -- --
                if _container is np.array:
                    assert isinstance(out, np.ndarray)
                elif _container is np.ma.masked_array:
                    assert isinstance(out, np.ma.MaskedArray)
                else:
                    assert isinstance(out, _container)

                assert all(map(isinstance, out, (numbers.Number for _ in out)))
                # END validate object was built correctly -- -- -- -- --
            else:   # is 2D
                _X = _X_list_2D
                if _container is [set, pd.Series, pl.Series]:
                    raise TypeError(f"container cant be {_container} when 2D")
                elif _container in [list, tuple]:
                    out = _container(map(_container, _X))
                else:
                    out = _container(_X)

                # validate object was built correctly -- -- -- -- -- --
                if _container is np.array:
                    assert isinstance(out, np.ndarray)
                elif _container is np.ma.masked_array:
                    assert isinstance(out, np.ma.MaskedArray)
                else:
                    assert isinstance(out, _container)

                if hasattr(out, 'toarray') \
                        or isinstance(out, (pd.DataFrame, pl.DataFrame)):
                    # scipy sparse, pd df, pl df can only be 2D, so dont
                    # need to prove is 2D
                    pass
                else:
                    assert not any(map(isinstance, out, (numbers.Number for _ in out)))
                # END validate object was built correctly -- -- -- -- --

            return out


        return foo


    @staticmethod
    @pytest.fixture(scope='function')
    def _value_getter():

        # return the upper-left-most value in a container

        def foo(_X):

            if hasattr(_X, 'shape'):
                _is_1D = (len(_X.shape) == 1)
            else:
                _is_1D = all(map(isinstance, _X, (numbers.Number for _ in _X)))

            if _is_1D:
                if hasattr(_X, 'toarray'):
                    raise TypeError(f"container cant be scipy when 1D")
                elif isinstance(_X, (pd.DataFrame, pl.DataFrame)):
                    raise TypeError(f"container cant be {_X} when 1D")
                elif isinstance(_X, set):
                    out = sorted(list(_X))[0]
                else:
                    # could be list, tuple, ndarray, masked array
                    # pd/pl Series
                    out = _X[0]

            else:   # is 2D
                if isinstance(_X, (set, pd.Series, pl.Series)):
                    raise TypeError(f"container cant be {_X} when 2D")
                elif isinstance(_X, pd.DataFrame):
                    out = _X.iloc[0, 0]
                elif isinstance(_X, pl.DataFrame):
                    out = _X.item(0, 0)
                elif hasattr(_X, 'toarray'):
                    out = _X.tocsc()[0, 0]
                elif isinstance(_X, tuple):
                    out = list(_X)[0][0]
                else:
                    out = _X[0][0]

            assert isinstance(out, numbers.Number)


            return out


        return foo


    @staticmethod
    @pytest.fixture(scope='function')
    def _value_setter():

        # set the upper-left-most value in a container

        def foo(_X, _value):

            if hasattr(_X, 'shape'):
                _is_1D = (len(_X.shape)==1)
            else:
                _is_1D = all(map(isinstance, _X, (numbers.Number for _ in _X)))

            if _is_1D:
                if hasattr(_X, 'toarray'):
                    raise TypeError(f"container cant be scipy when 1D")
                elif isinstance(_X, (pd.DataFrame, pl.DataFrame)):
                    raise TypeError(f"container cant be {_X} when 1D")
                elif isinstance(_X, set):
                    _X = list(_X)
                    _X[0] = _value
                    _X = set(_X)
                elif isinstance(_X, tuple):
                    _X = list(_X)
                    _X[0] = _value
                    _X = tuple(_X)
                else:
                    # could be list, ndarray, masked array, pd/pl Series
                    _X[0] = _value
            else:   # is 2D
                if isinstance(_X, (set, pd.Series, pl.Series)):
                    raise TypeError(f"container cant be {_X} when 2D")
                elif isinstance(_X, pd.DataFrame):
                    _X.iloc[0, 0] = _value
                elif hasattr(_X, 'toarray'):
                    _og_dtype = type(_X)
                    _X = _X.tocsc()
                    _X[0, 0] = _value
                    _X = _og_dtype(_X)
                    del _og_dtype
                elif isinstance(_X, tuple):
                    _X = list(map(list, _X))
                    _X[0][0] = _value
                    _X = tuple(map(tuple, _X))
                elif hasattr(_X, 'clone'):
                    _X[0, 0] = _value
                else:
                    _X[0][0] = _value


            return _X


        return foo

    # END fixtures v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v


    @pytest.mark.parametrize('junk_X',
        (-2.7, -1, 0, 1, 2.7, True, False, None, lambda x: x)
    )
    def test_rejects_junk_X(self, junk_X):

        with pytest.raises(TypeError):
            copy_X(junk_X)


    @pytest.mark.parametrize('_dim', (1,2))
    @pytest.mark.parametrize('_container',
        (list, tuple, set, np.array, np.ma.masked_array, pd.Series, pd.DataFrame,
         pl.Series, pl.DataFrame,
         ss.csr_matrix, ss.csr_array, ss.csc_matrix, ss.csc_array, ss.coo_matrix,
         ss.coo_array, ss.dia_matrix, ss.dia_array, ss.dok_matrix, ss.dok_array,
         ss.lil_matrix, ss.lil_array, ss.bsr_matrix, ss.bsr_array)
    )
    @pytest.mark.parametrize('_value', (-99, -1))
    def test_does_not_mutate_original(
        self, _container_maker, _value_getter, _value_setter, _dim, _container,
        _value
    ):

        # the _value number is rigged. set always sorts, so need to make _value
        # be something that will always sort to the first position

        # skip impossible conditions -- -- -- -- -- -- -- -- -- -- -- --
        if _dim == 1 and _container in [pd.DataFrame, pl.DataFrame]:
            pytest.skip(f'impossible condition')
        if _dim == 1 and hasattr(_container, 'toarray'):
            pytest.skip(f'impossible condition')
        if _dim == 2 and _container in [set, pd.Series, pl.Series]:
            pytest.skip(f'impossible condition')

        # END skip impossible conditions -- -- -- -- -- -- -- -- -- --

        # build X
        _X = _container_maker(_container, _dim)

        # get the original upper-left-most value in X
        _og_value = _value_getter(_X)

        # make a pybear copy of X
        _copy_of_X = copy_X(_X)

        # set a new value in the copy of X
        _copy_of_X = _value_setter(_copy_of_X, _value)

        # verify the new value has been set
        assert _value_getter(_copy_of_X) == _value, f"{_og_value=}"

        # the value in the original X should be unchanged
        assert _value_getter(_X) == _og_value





