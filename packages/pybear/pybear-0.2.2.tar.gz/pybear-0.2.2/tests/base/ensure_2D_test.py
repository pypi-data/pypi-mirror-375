# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.base._ensure_2D import ensure_2D

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

import pytest




class TestEnsure2D:


    # fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    @staticmethod
    @pytest.fixture(scope='module')
    def build_scipy_sparse():

        def foo(_base_X, X_format: str):

            if X_format == 'csr_array':
                _X = ss.csr_array(_base_X)
            elif X_format == 'csc_array':
                _X = ss.csc_array(_base_X)
            elif X_format == 'coo_array':
                _X = ss.coo_array(_base_X)
            elif X_format == 'dia_array':
                _X = ss.dia_array(_base_X)
            elif X_format == 'lil_array':
                _X = ss.lil_array(_base_X)
            elif X_format == 'dok_array':
                _X = ss.dok_array(_base_X)
            elif X_format == 'bsr_array':
                _X = ss.bsr_array(_base_X)
            elif X_format == 'csr_matrix':
                _X = ss.csr_matrix(_base_X)
            elif X_format == 'csc_matrix':
                _X = ss.csc_matrix(_base_X)
            elif X_format == 'coo_matrix':
                _X = ss.coo_matrix(_base_X)
            elif X_format == 'dia_matrix':
                _X = ss.dia_matrix(_base_X)
            elif X_format == 'lil_matrix':
                _X = ss.lil_matrix(_base_X)
            elif X_format == 'dok_matrix':
                _X = ss.dok_matrix(_base_X)
            elif X_format == 'bsr_matrix':
                _X = ss.bsr_matrix(_base_X)
            else:
                raise Exception

            return _X

        return foo

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    @pytest.mark.parametrize('junk_object',
        (-2.7, -1, 0, 1, 2.7, True, None, 'trash', {'a': 1}, lambda x: x, min)
    )
    def test_rejects_non_array_like(self, junk_object):
        with pytest.raises(ValueError):
            ensure_2D(junk_object)


    def test_rejects_does_not_have_shape_attr(self):

        with pytest.raises(ValueError):
            ensure_2D(
                [[0,1,2], [3,4,5], [6,7,8]]
            )

        with pytest.raises(ValueError):
            ensure_2D(
                ((0,1,2), (3,4,5), (6,7,8))
            )


    @pytest.mark.parametrize('X_format',
        ('np', 'pd', 'pl', 'csr_array', 'csr_matrix', 'csc_array', 'csc_matrix',
         'coo_array', 'coo_matrix', 'dia_array', 'dia_matrix', 'lil_array',
         'lil_matrix', 'dok_array', 'dok_matrix', 'bsr_array', 'bsr_matrix')
    )
    def test_accepts_array_like(self, build_scipy_sparse, X_format):

        _base_X = np.random.randint(0, 10, (10, 5))

        if X_format == 'np':
            _X = _base_X
        elif X_format == 'pd':
            _X = pd.DataFrame(data=_base_X)
        elif X_format == 'pl':
            _X = pl.from_numpy(_base_X)
        elif 'array' in X_format or 'matrix' in X_format:
            _X = build_scipy_sparse(_base_X, X_format)
        else:
            raise Exception

        ensure_2D(_X)


    @pytest.mark.parametrize('junk_copy_X',
        (-2.7, -1, 0, 1, 2.7, None, 'trash', {'a': 1}, lambda x: x, min)
    )
    def test_rejects_non_bool_copy_X(self, junk_copy_X):
        with pytest.raises(TypeError):
            ensure_2D(
                np.random.randint(0, 10, (37,13)),
                copy_X=junk_copy_X
            )


    @pytest.mark.parametrize('bool_copy_X', (True, False))
    def test_accepts_bool_copy_X(self, bool_copy_X):

        out = ensure_2D(
            np.random.randint(0, 10, (37,13)),
            copy_X=bool_copy_X
        )
        assert isinstance(out, np.ndarray)


    @pytest.mark.parametrize('dim', (0, 3, 4))
    def test_blocks_0_dim_and_3_or_more_dim(self, dim):

        # build shape tuple
        _shape = tuple(np.random.randint(2, 5, dim).tolist())

        _X = np.random.randint(0, 10, _shape)

        with pytest.raises(ValueError):
            ensure_2D(_X)


    @pytest.mark.parametrize('X_format',
        ('np', 'pd', 'pl', 'csr_array', 'csr_matrix', 'csc_array', 'csc_matrix',
         'coo_array', 'coo_matrix', 'dia_array', 'dia_matrix', 'lil_array',
         'lil_matrix', 'dok_array', 'dok_matrix', 'bsr_array', 'bsr_matrix')
    )
    @pytest.mark.parametrize('dim', (1, 2))
    def test_accuracy(self, X_format, dim, build_scipy_sparse):

        # skip impossible conditions - - - - - - - - - - - - - - - - - -
        if any(i in X_format for i in ['array', 'matrix']) and dim == 1:
            pytest.skip(f"scipy sparse can only be 2D")
        # END skip impossible conditions - - - - - - - - - - - - - - - -


        # stay on the rails
        if dim not in [1,2]:
            raise Exception


        # build shape tuple
        _shape = tuple(np.random.randint(2, 10, dim).tolist())

        _base_X = np.random.randint(0, 10, _shape)

        if X_format == 'np':
            _X = _base_X
        elif X_format == 'pd':
            if dim == 1:
                _X = pd.Series(data=_base_X)
            elif dim == 2:
                _X = pd.DataFrame(data=_base_X)
        elif X_format == 'pl':
            if dim == 1:
                _X = pl.Series(_base_X)
            elif dim == 2:
                _X = pl.from_numpy(data=_base_X)
        elif 'array' in X_format or 'matrix' in X_format:
            _X = build_scipy_sparse(_base_X, X_format)
            if dim == 1:
                X = _X.squeeze()
        else:
            raise Exception


        out = ensure_2D(_X)

        if X_format == 'pd':
            # anything 2D in pandas is always DF
            assert isinstance(out, pd.DataFrame)
        elif X_format == 'pl':
            # anything 2D in polars is always DF
            assert isinstance(out, pl.DataFrame)
        else:
            assert type(out) == type(_X)

        assert len(out.shape) == 2

        # v v v v v verify data is in OBJECT is unchanged v v v v v v

        # convert out to np for array_equal
        if X_format == 'np':
            pass
        elif X_format in ['pd', 'pl']:
            out = out.to_numpy()
        elif hasattr(out, 'toarray'):   # scipy sparse
            out = out.toarray()
        else:
            raise Exception

        assert isinstance(out, np.ndarray)

        if dim == 1:
            assert np.array_equiv(out.ravel(), _base_X)
        elif dim == 2:
            assert np.array_equiv(out, _base_X)




