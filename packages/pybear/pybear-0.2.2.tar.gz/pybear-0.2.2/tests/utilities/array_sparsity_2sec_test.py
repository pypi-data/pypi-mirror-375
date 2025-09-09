# Authors:
#
#       Bill Sousa
#
# License: BSD 3 clause



import pytest

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss


from pybear.utilities._array_sparsity import array_sparsity



class TestValidation:

    # TypeError for not an array-like
    # TypeError if cant be converted by list()
    # ValueError if size==0


    # raises TypeError for not an array-like
    @pytest.mark.parametrize('a', ('junk', None, {'a':1, 'b':2}))
    def test_not_an_array_like(self, a):
        with pytest.raises(TypeError):
            array_sparsity(a)


    # raises TypeError if cant be converted by list()
    @pytest.mark.parametrize('a', (3, np.pi, float('inf')))
    def test_cannot_be_converted_by_py_list(self, a):
        with pytest.raises(TypeError):
            array_sparsity(a)


    # raises ValueError for empty array-like
    def test_empty_array(self):

        with pytest.raises(ValueError):
            array_sparsity([])

        with pytest.raises(ValueError):
            array_sparsity(())

        with pytest.raises(ValueError):
            array_sparsity(np.array([]))

        with pytest.raises(ValueError):
            array_sparsity(pd.DataFrame(np.array([])))

        with pytest.raises(ValueError):
            array_sparsity(pl.from_numpy(np.array([])))

        with pytest.raises(ValueError):
            array_sparsity(ss.csc_array(np.array([])))


# remember cant have 1D ss
@pytest.mark.parametrize('_sparsity', (0, 10, 50, 100))
@pytest.mark.parametrize('_format', ('py_list', 'py_tup', 'np', 'pd', 'pl'))
class TestAccuracy1D:

    # fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @staticmethod
    @pytest.fixture
    def _shape():
        return (100,)


    @staticmethod
    @pytest.fixture
    def good_array(_format, _sparsity, _shape):

        _base_X = np.random.randint(1, 100, _shape, dtype=np.uint8)
        _base_X = _base_X.astype(np.float64).ravel()
        # sprinkle nans
        _base_X[np.random.choice(range(_shape[0]//10), (_shape[0]//10,))] = np.nan

        if _sparsity == 0:
            pass
        elif _sparsity == 10:
            _base_X[:10] = 0
        elif _sparsity == 50:
            _base_X[:50] = 0
        elif _sparsity == 100:
            _base_X[:] = 0
        else:
            raise Exception

        if _format == 'py_list':
            _X = _base_X.tolist()
        elif _format == 'py_tup':
            _X = tuple(_base_X.tolist())
        elif _format == 'np':
            _X = _base_X
        elif _format == 'pd':
            _X = pd.Series(_base_X)
        elif _format == 'pl':
            _X = pl.Series(_base_X)
        else:
            raise Exception

        return _X

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    def test_accuracy(self, good_array, _sparsity, _shape):

        if hasattr(good_array, 'shape'):
            assert good_array.shape == _shape

        if _sparsity == 0:
            assert int(array_sparsity(good_array)) == 0
        elif _sparsity == 10:
            assert int(array_sparsity(good_array)) == 10
        elif _sparsity == 50:
            assert int(array_sparsity(good_array)) == 50
        elif _sparsity == 100:
            assert int(array_sparsity(good_array)) == 100
        else:
            raise Exception


@pytest.mark.parametrize('_sparsity', (0, 10, 50, 100))
@pytest.mark.parametrize('_format',
    ('py_list', 'py_tup', 'np', 'pd', 'pl', 'csc', 'csr', 'coo', 'dok',
     'lil', 'dia')    # not bsr!
)
class TestAccuracy2D:

    # fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @staticmethod
    @pytest.fixture
    def good_array(_format, _sparsity, _shape):

        _base_X = np.random.randint(1, 100, _shape, dtype=np.uint8).astype(np.float64)
        # sprinkle nans
        for i in range(np.prod(_shape)//10):
            _r_idx = np.random.randint(0, _shape[0])
            _c_idx = np.random.randint(0, _shape[1])
            _base_X[_r_idx, _c_idx] = np.nan

        if _sparsity == 0:
            pass
        elif _sparsity == 10:
            _base_X[0:100:10, :] = 0
        elif _sparsity == 50:
            _base_X[0:100:2, :] = 0
        elif _sparsity == 100:
            _base_X[:] = 0
        else:
            raise Exception

        if _format == 'py_list':
            _X = list(map(list, map(lambda j: map(float, j), _base_X)))
        elif _format == 'py_tup':
            _X = tuple(map(tuple, map(lambda j: map(float, j), _base_X)))
        elif _format == 'np':
            _X = _base_X
        elif _format == 'pd':
            _X = pd.DataFrame(_base_X)
        elif _format == 'pl':
            _X = pl.from_numpy(_base_X)
        elif _format == 'csc':
            _X = ss.csc_array(_base_X)
        elif _format == 'csr':
            _X = ss.csr_array(_base_X)
        elif _format == 'coo':
            _X = ss.coo_array(_base_X)
        elif _format == 'dia':
            _X = ss.dia_array(_base_X)
        elif _format == 'lil':
            _X = ss.lil_array(_base_X)
        elif _format == 'dok':
            _X = ss.dok_array(_base_X)
        # does not accept bsr array
        # elif _format == 'bsr':
        #     _X = ss.bsr_array(_base_X)
        else:
            raise Exception

        return _X

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    def test_accuracy(self, good_array, _sparsity, _shape):

        if hasattr(good_array, 'shape'):
            assert good_array.shape == _shape

        if _sparsity == 0:
            assert int(array_sparsity(good_array)) == 0
        elif _sparsity == 10:
            assert int(array_sparsity(good_array)) == 10
        elif _sparsity == 50:
            assert int(array_sparsity(good_array)) == 50
        elif _sparsity == 100:
            assert int(array_sparsity(good_array)) == 100
        else:
            raise Exception






