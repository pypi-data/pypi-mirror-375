# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd
import scipy.sparse as ss
import polars as pl

from pybear.utilities._nan_masking import (
    nan_mask_numerical,
    nan_mask_string,
    nan_mask
)



# 'nan_mask' is tested alongside 'nan_mask_numerical' and
# 'nan_mask_string', it should replicate the behavior of both

# tests python built-ins, numpy arrays, pandas dataframes, and scipy.sparse
# with various nan-like representations (np.nan, 'nan', 'pd.NA', None),
# for float, int, str, and object dtypes.



@pytest.fixture(scope='module')
def truth_mask_1(_shape):
    """Random mask for building containers with nans in them."""
    while True:
        M = np.random.randint(0, 2, _shape).astype(bool)
        # make sure that there are both trues and falses in all columns
        # so that pandas columns all have same dtype
        for c_idx in range(_shape[1]):
            if not 0 < np.sum(M[:, c_idx]) / _shape[0] < 1:
                break
        else:
            return M


@pytest.fixture(scope='module')
def truth_mask_2(_shape):
    """Random mask for building containers with nans in them."""
    while True:
        M = np.random.randint(0,2, _shape).astype(bool)
        # make sure that there are both trues and falses in all columns
        # so that pandas columns all have same dtype
        for c_idx in range(_shape[1]):
            if not 0 < np.sum(M[:, c_idx]) / _shape[0] < 1:
                break
        else:
            return M


@pytest.fixture(scope='module')
def pd_assnmt_handle():
    """Wrap nan assignments to pd dataframes in try except block."""
    # 24_10_28 pandas future warnings about casting incompatible
    # dtypes. put assignments under a try/except, if OK, return new
    # X, if bad return None. in the test functions, if X comes back
    # as None, skip the test.

    def foo(X: pd.DataFrame, MASK: np.ndarray, value: any):
        try:
            X[MASK] = value
            return X
        except:
            return None

    return foo



class TestNanMaskNumeric:


    @pytest.mark.parametrize('_container', (list, tuple, set))
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_nan_type',
        ('npnan', 'strnan', 'any string', 'pdNA', 'none')
    )
    def test_python_builtins_num(
        self, _shape, truth_mask_1, truth_mask_2, _container, _dim, _trial,
        _nan_type
    ):

        # skip impossible -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if _container is set:
            if _dim == 2:
                pytest.skip(reason=f"cant have 2D set")
            if _trial != 'trial_3':
                # the masks have multiple inf values and set is screwing
                # up the count, just do the empty mask trial and
                # see that it passes thru.
                pytest.skip(reason=f"sets mess up the inf count")

        # END skip impossible -- -- -- -- -- -- -- -- -- -- -- -- -- --

        X = np.random.uniform(0, 1, _shape)

        if _trial == 1:
            MASK = truth_mask_1
        elif _trial == 2:
            MASK = truth_mask_2
        elif _trial == 3:
            MASK = np.zeros(_shape).astype(bool)
        else:
            raise Exception

        if _nan_type == 'npnan':
            X[MASK] = np.nan
        elif _nan_type == 'strnan':
            X[MASK] = 'nan'
        elif _nan_type == 'any string':
            with pytest.raises(ValueError):
                X[MASK] = 'any string'
            pytest.skip()
        elif _nan_type == 'pdNA':
            with pytest.raises(TypeError):
                X[MASK] = pd.NA
            pytest.skip()
        elif _nan_type == 'none':
            X[MASK] = None
        else:
            raise Exception

        if _dim == 1:
            X = _container(X[:, 0].tolist())
            MASK = MASK[:, 0]
            _shape = (_shape[0], )
        elif _dim == 2:
            X = _container(map(_container, X))
        else:
            raise Exception

        out = nan_mask_numerical(X)

        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool
        assert np.array_equal(out, MASK)

        out_2 = nan_mask(X)

        assert isinstance(out_2, np.ndarray)
        assert out_2.shape == _shape
        assert out_2.dtype == bool
        assert np.array_equal(out_2, MASK)


    # the only np numerical that can take nan is np ndarray.astype(float64)
    # and it must be np.nan, 'nan' (not case sensitive), or None (not pd.NA!)
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_nan_type',
        ('npnan', 'strnan', 'any string', 'pdNA', 'none')
    )
    def test_np_float_array(
        self, _shape, truth_mask_1, truth_mask_2, _dim, _trial, _nan_type
    ):

        X = np.random.uniform(0,1,_shape)

        if _trial == 1:
            MASK = truth_mask_1
        elif _trial == 2:
            MASK = truth_mask_2
        elif _trial == 3:
            MASK = np.zeros(_shape).astype(bool)
        else:
            raise Exception

        if _nan_type == 'npnan':
            X[MASK] = np.nan
        elif _nan_type == 'strnan':
            X[MASK] = 'nan'
        elif _nan_type == 'any string':
            with pytest.raises(ValueError):
                X[MASK] = 'any string'
            pytest.skip()
        elif _nan_type == 'pdNA':
            with pytest.raises(TypeError):
                X[MASK] = pd.NA
            pytest.skip()
        elif _nan_type == 'none':
            X[MASK] = None
        else:
            raise Exception

        out = nan_mask_numerical(X)

        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool
        assert np.array_equal(out, MASK)

        out_2 = nan_mask(X)

        assert isinstance(out_2, np.ndarray)
        assert out_2.shape == _shape
        assert out_2.dtype == bool
        assert np.array_equal(out_2, MASK)


    # numpy integer array cannot take any representation of nan.
    # would need to convert X to float64
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2))
    @pytest.mark.parametrize('_nan_type',
        ('npnan', 'strnan', 'any string', 'pdNA', 'none')
    )
    def test_np_int_array(
        self, _shape, truth_mask_1, truth_mask_2, _dim, _trial, _nan_type
    ):

        # all inf-likes raise exception when casting into int dtypes

        # this is also testing an int dtype with no infs to see if
        # nan_mask() can take int dtype (and return a mask of all Falses).

        X = np.random.randint(0,10, _shape)

        if _trial == 1:
            MASK = truth_mask_1
        elif _trial == 2:
            MASK = truth_mask_2
        else:
            raise Exception

        if _dim == 1:
            X = X[:, 0]
            MASK = MASK[:, 0]
            _shape = (_shape[0], )

        # everything here raises an except
        if _nan_type == 'npnan':
            with pytest.raises(ValueError):
                X[MASK] = np.nan
            pytest.skip()
        elif _nan_type == 'strnan':
            with pytest.raises(ValueError):
                X[MASK] = 'nan'
            pytest.skip()
        elif _nan_type == 'any string':
            with pytest.raises(ValueError):
                X[MASK] = 'any string'
            pytest.skip()
        elif _nan_type == 'pdNA':
            with pytest.raises(TypeError):
                X[MASK] = pd.NA
            pytest.skip()
        elif _nan_type == 'none':
            with pytest.raises(TypeError):
                X[MASK] = None
            pytest.skip()
        else:
            raise Exception

        out = nan_mask_numerical(X)

        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool
        assert np.array_equal(out, MASK)

        out_2 = nan_mask(X)

        assert isinstance(out_2, np.ndarray)
        assert out_2.shape == _shape
        assert out_2.dtype == bool
        assert np.array_equal(out_2, MASK)


    # all scipy sparses return np float array np.nans correctly
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_format',
        (
            'csr_matrix', 'csc_matrix', 'coo_matrix', 'dia_matrix',
            'lil_matrix', 'dok_matrix', 'bsr_matrix', 'csr_array', 'csc_array',
            'coo_array', 'dia_array', 'lil_array', 'dok_array', 'bsr_array',
        )
    )
    @pytest.mark.parametrize('_nan_type',
        ('npnan', 'strnan', 'any string', 'pdNA', 'none')
    )
    def test_scipy_sparse_via_np_float_array(
        self, _shape, truth_mask_1, truth_mask_2, _trial, _format, _nan_type
    ):

        # can only be 2D and numeric

        X = np.random.uniform(0, 1 ,_shape)

        # make a lot of sparsity so that converting to sparse reduces
        for _col_idx in range(_shape[1]):
            _row_idxs = np.random.choice(
                range(_shape[0]),
                _shape[0]//4,
                replace=False
            )
            X[_row_idxs, _col_idx] = 0


        if _trial == 1:
            MASK = truth_mask_1
        elif _trial == 2:
            MASK = truth_mask_2
        elif _trial == 3:
            MASK = np.zeros(_shape).astype(bool)
        else:
            raise Exception

        if _nan_type == 'npnan':
            X[MASK] = np.nan
        elif _nan_type == 'strnan':
            X[MASK] = 'nan'
        elif _nan_type == 'any string':
            with pytest.raises(ValueError):
                X[MASK] = 'any string'
            pytest.skip()
        elif _nan_type == 'pdNA':
            with pytest.raises(TypeError):
                X[MASK] = pd.NA
            pytest.skip()
        elif _nan_type == 'none':
            X[MASK] = None
        else:
            raise Exception


        assert X.dtype == np.float64

        if _format == 'csr_matrix':
            X_wip = ss._csr.csr_matrix(X)
        elif _format == 'csc_matrix':
            X_wip = ss._csc.csc_matrix(X)
        elif _format == 'coo_matrix':
            X_wip = ss._coo.coo_matrix(X)
        elif _format == 'dia_matrix':
            X_wip = ss._dia.dia_matrix(X)
        elif _format == 'lil_matrix':
            X_wip = ss._lil.lil_matrix(X)
        elif _format == 'dok_matrix':
            X_wip = ss._dok.dok_matrix(X)
        elif _format == 'bsr_matrix':
            X_wip = ss._bsr.bsr_matrix(X)
        elif _format == 'csr_array':
            X_wip = ss._csr.csr_array(X)
        elif _format == 'csc_array':
            X_wip = ss._csc.csc_array(X)
        elif _format == 'coo_array':
            X_wip = ss._coo.coo_array(X)
        elif _format == 'dia_array':
            X_wip = ss._dia.dia_array(X)
        elif _format == 'lil_array':
            X_wip = ss._lil.lil_array(X)
        elif _format == 'dok_array':
            X_wip = ss._dok.dok_array(X)
        elif _format == 'bsr_array':
            X_wip = ss._bsr.bsr_array(X)
        else:
            raise Exception

        # get the inf mask as ss (dok & lil should raise)
        if 'lil' in _format or 'dok' in _format:
            with pytest.raises(TypeError):
                nan_mask_numerical(X_wip)

            with pytest.raises(TypeError):
                nan_mask(X_wip)
        else:
            out = nan_mask_numerical(X_wip)

            assert isinstance(out, np.ndarray)
            assert out.shape == X_wip.data.shape
            assert out.dtype == bool

            out_2 = nan_mask(X_wip)

            assert isinstance(out_2, np.ndarray)
            assert out_2.shape == X_wip.data.shape
            assert out_2.dtype == bool

        # covert back to np to see if nan mask was affected
        X = X_wip.toarray()

        np_out = nan_mask(X)
        assert isinstance(np_out, np.ndarray)
        assert np_out.shape == _shape
        assert np_out.dtype == bool

        assert np.array_equal(np_out, MASK)


    # pd float dfs can take any of the following representations of nan
    # and convert them to either np.nan or pd.NA:
    # np.nan, any string, pd.NA, or None
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_nan_type',
        ('npnan', 'strnan', 'any string', 'pdNA', 'none')
    )
    def test_pd_float(
        self, _shape, truth_mask_1, truth_mask_2, _dim, _trial, _nan_type,
        _columns, pd_assnmt_handle
    ):

        X = pd.DataFrame(
            data = np.random.uniform(0, 1, _shape),
            columns = _columns,
            dtype=np.float64
        )

        if _trial == 1:
            MASK = truth_mask_1
        elif _trial == 2:
            MASK = truth_mask_2
        elif _trial == 3:
            MASK = np.zeros(_shape).astype(bool)
        else:
            raise Exception

        if _nan_type == 'npnan':
            X = pd_assnmt_handle(X, MASK, np.nan)
        elif _nan_type == 'strnan':
            X = pd_assnmt_handle(X, MASK, 'nan')
        elif _nan_type == 'any string':
            X = pd_assnmt_handle(X, MASK, 'any string')
        elif _nan_type == 'pdNA':
            X = pd_assnmt_handle(X, MASK, pd.NA)
        elif _nan_type == 'none':
            X = pd_assnmt_handle(X, MASK, None)
        else:
            raise Exception

        if _dim == 1:
            X = X.iloc[:, 0].squeeze()
            MASK = MASK[:, 0]
            _shape = (_shape[0], )

        # if exception is raised by pd_assnmnt_handle because of casting
        # nan to disallowed dtype, then X is None and skip test
        if X is None:
            pytest.skip(reason=f"invalid value cast to dataframe dtype, skip test")

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _dtypes = [X.dtypes] if _dim == 1 else list(set(X.dtypes))
        assert len(_dtypes) == 1
        _dtype = _dtypes[0]

        if np.sum(MASK) == 0:
            # when mask makes no assignment, dtype is not changed
            assert _dtype == np.float64
        elif _nan_type in [
            'strnan', 'any string'
        ]:
            # 'strnan' and 'any string' are changing dtype from float64 to object!
            assert _dtype == object
        else:
            # for all other inf assignments, dtypes is not changed
            assert _dtype == np.float64
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if np.sum(MASK) != 0 and _nan_type == 'any string':
            with pytest.raises(ValueError):
                nan_mask_numerical(X)

            assert np.sum(nan_mask(X)) == 0
        else:
            out = nan_mask_numerical(X)
            assert isinstance(out, np.ndarray)
            assert out.shape == _shape
            assert out.dtype == bool
            assert np.array_equal(out, MASK)

            out_2 = nan_mask(X)
            assert isinstance(out_2, np.ndarray)
            assert out_2.shape == _shape
            assert out_2.dtype == bool
            assert np.array_equal(out_2, MASK)


    # pd int dfs can take any of the following representations of nan
    # and convert them to either np.nan or pd.NA:
    # np.nan, any string, pd.NA, or None
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_nan_type',
        ('npnan', 'strnan', 'any string', 'pdNA', 'none')
    )
    def test_pd_int(
        self, _shape, truth_mask_1, truth_mask_2, _dim, _trial, _nan_type,
        _columns, pd_assnmt_handle
    ):

        X = pd.DataFrame(
            data = np.random.randint(0, 10, _shape),
            columns = _columns,
            dtype=np.uint32
        )

        if _trial == 1:
            MASK = truth_mask_1
        elif _trial == 2:
            MASK = truth_mask_2
        elif _trial == 3:
            MASK = np.zeros(_shape).astype(bool)
        else:
            raise Exception

        if _nan_type == 'npnan':
            X = pd_assnmt_handle(X, MASK, np.nan)
        elif _nan_type == 'strnan':
            X = pd_assnmt_handle(X, MASK, 'nan')
        elif _nan_type == 'any string':
            X = pd_assnmt_handle(X, MASK, 'any string')
        elif _nan_type == 'pdNA':
            X = pd_assnmt_handle(X, MASK, pd.NA)
        elif _nan_type == 'none':
            X = pd_assnmt_handle(X, MASK, None)
        else:
            raise Exception

        if _dim == 1:
            X = X.iloc[:, 0].squeeze()
            MASK = MASK[:, 0]
            _shape = (_shape[0], )

        # if exception is raised by pd_assnmnt_handle because of casting
        # nan to disallowed dtype, then X is None and skip test
        if X is None:
            pytest.skip(reason=f"invalid value cast to dataframe dtype, skip test")

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _dtypes = [X.dtypes] if _dim == 1 else list(set(X.dtypes))
        assert len(_dtypes) == 1
        _dtype = _dtypes[0]

        if np.sum(MASK) == 0:
            # if the mask does not assign anything then dtype does not change
            assert _dtype == np.uint32
        elif _nan_type in ['strnan', 'any string']:
            # 'strnan' and 'any string' are changing dtype from float64 to object!
            assert _dtype == object
        else:
            assert _dtype == np.float64
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if np.sum(MASK) == 0 or _nan_type == 'any string':
            with pytest.raises(ValueError):
                nan_mask_numerical(X)

            assert np.sum(nan_mask(X)) == 0
        else:
            assert np.array_equal(nan_mask_numerical(X), MASK)
            assert np.array_equal(nan_mask(X), MASK)


    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_nan_type',
        ('npnan', 'strnan', 'any string', 'pdNA', 'none')
    )
    def test_polars_float(
        self, _shape, truth_mask_1, truth_mask_2, _dim, _trial, _nan_type,
        _columns
    ):

        # prepare np array for conversion to polars -- -- -- -- -- --
        X = np.random.uniform(0, 1, _shape).astype(np.float64)

        if _trial == 1:
            MASK = truth_mask_1
        elif _trial == 2:
            MASK = truth_mask_2
        elif _trial == 3:
            MASK = np.zeros(_shape).astype(bool)
        else:
            raise Exception

        if _nan_type == 'npnan':
            X[MASK] = np.nan
        elif _nan_type == 'strnan':
            X[MASK] = 'nan'
        elif _nan_type == 'any string':
            with pytest.raises(ValueError):
                X[MASK] = 'any string'
            pytest.skip()
        elif _nan_type == 'pdNA':
            with pytest.raises(TypeError):
                X[MASK] = pd.NA
            pytest.skip()
        elif _nan_type == 'none':
            X[MASK] = None
        else:
            raise Exception

        if _dim == 1:
            X = X[:, 0]
            MASK = MASK[:, 0]
            _shape = (_shape[0], )

        assert X.dtype == np.float64
        # END prepare the np array for conversion to polars -- -- -- --

        if _dim == 1:
            X = pl.Series(X)
        else:
            X = pl.from_numpy(X, schema=list(_columns))


        if _nan_type == 'any string':
            with pytest.raises(ValueError):
                nan_mask_numerical(X)

            assert np.sum(nan_mask(X)) == 0
        else:
            out = nan_mask_numerical(X)
            assert isinstance(out, np.ndarray)
            assert out.shape == _shape
            assert out.dtype == bool
            assert np.array_equal(out, MASK)

            out_2 = nan_mask(X)
            assert isinstance(out_2, np.ndarray)
            assert out_2.shape == _shape
            assert out_2.dtype == bool
            assert np.array_equal(out_2, MASK)


    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2))
    @pytest.mark.parametrize('_nan_type',
        ('npnan', 'strnan', 'any string', 'pdNA', 'none')
    )
    def test_polars_int(
        self, _shape, truth_mask_1, truth_mask_2, _trial, _dim, _nan_type,
        _columns
    ):

        # prepare the np array for conversion to polars -- -- -- -- --
        X = np.random.randint(0, 10, _shape).astype(np.float64)

        if _trial == 1:
            MASK = truth_mask_1
        elif _trial == 2:
            MASK = truth_mask_2
        else:
            raise Exception

        if _nan_type == 'npnan':
            X[MASK] = np.nan
        elif _nan_type == 'strnan':
            X[MASK] = 'nan'
        elif _nan_type == 'any string':
            with pytest.raises(ValueError):
                X[MASK] = 'any string'
            pytest.skip()
        elif _nan_type == 'pdNA':
            with pytest.raises(TypeError):
                X[MASK] = pd.NA
            pytest.skip()
        elif _nan_type == 'none':
            X[MASK] = None
        else:
            raise Exception

        if _dim == 1:
            X = X[:, 0]
            MASK = MASK[:, 0]
            _shape = (_shape[0], )

        assert X.dtype == np.float64

        # polars wont cast any infs to Int32
        # this is raised by polars, let it raise whatever
        with pytest.raises(Exception):
            X_wip = pl.from_numpy(X).cast(pl.Int32)


    # make a pandas dataframe with all the possible things that make an
    # nan-like in a dataframe. see if converting to np array converts
    # them all to np.nan, and is recognized.
    # takeaway:
    # to_numpy() converts all of these different nans to np.nan correctly
    def numpy_float_via_pd_made_with_various_nan_types(
        self, _shape, _trial, _nan_type, _columns
    ):

        X = pd.DataFrame(
            data = np.random.uniform(0, 1, _shape),
            columns = _columns,
            dtype=np.float64
        )

        _pool = (np.nan, 'nan', 'any string', pd.NA, None, '<NA>')

        # sprinkle the various nan-types into the float DF
        # make a mask DF to mark the places of the nan-likes
        MASK = np.zeros(_shape).astype(bool)
        for _sprinkling_itr in range(X.size//10):
            _row_idx = np.random.randint(_shape[0])
            _col_idx = np.random.randint(_shape[1])

            X.iloc[_row_idx, _col_idx] = np.random.choice(_pool)
            MASK[_row_idx, _col_idx] = True

        X = X.to_numpy()

        out = nan_mask_numerical(X)
        out_2 = nan_mask(X)

        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool
        assert np.array_equal(out, MASK)

        assert isinstance(out_2, np.ndarray)
        assert out_2.shape == _shape
        assert out_2.dtype == bool
        assert np.array_equal(out_2, MASK)


    def test_nan_mask_numerical_takes_str_numbers(self):

        # 1D -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _X = list(map(str, list(range(10))))

        assert all(map(isinstance, _X, (str for _ in _X)))

        _X[1] = 'nan'
        _X[2] = np.nan

        ref = np.zeros((10,)).astype(bool)
        ref[1] = True
        ref[2] = True

        out = nan_mask_numerical(_X)

        assert np.array_equal(out, ref)
        # END 1D -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # 2D -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _X = np.random.randint(0, 10, (5, 3)).astype(str)

        assert all(map(isinstance, _X[0], (str for _ in _X[0])))

        _X[1][0] = 'nan'
        _X[2][0] = np.nan

        ref = np.zeros((5, 3)).astype(bool)
        ref[1][0] = True
        ref[2][0] = True
        ref = ref.tolist()

        out = nan_mask_numerical(_X)

        assert np.array_equal(out, ref)

        # END 2D -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    def test_nan_mask_numerical_takes_weird_str_numbers(self):

        # 25_04_12 there was a problem with all of the Text modules failing
        # on string data that looks like ['8\n', '9\n']. Only when there are
        # no other legit strings. the problem appears to be in
        # nan_mask_numerical.

        _nums = ['1\n', '2\n', '3\n', '4\n','5\n', '6\n', '7\n']

        # use this as a control to show this works on string
        assert not any(nan_mask_string(_nums))

        assert not any(nan_mask_numerical(_nums))


class TestNanMaskString:

    # scipy sparse cannot take non-numeric datatypes

    @staticmethod
    @pytest.fixture()
    def _X(_shape):
        return np.random.choice(list('abcdefghij'), _shape, replace=True)


    @pytest.mark.parametrize('_container', (list, tuple, set))
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_nan_type',
        ('npnan', 'strnan', 'any string', 'pdNA', 'none')
    )
    def test_python_builtins_str(
        self, _X, truth_mask_1, truth_mask_2, _container, _dim, _trial,
        _nan_type, _shape
    ):

        # skip impossible -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if _container is set:
            if _dim == 2:
                pytest.skip(reason=f"cant have 2D set")
            if _trial != 'trial_3':
                # the masks have multiple inf values and set is screwing
                # up the count, just do the empty mask trial and
                # see that it passes thru.
                pytest.skip(reason=f"sets mess up the inf count")

        # END skip impossible -- -- -- -- -- -- -- -- -- -- -- -- -- --


        X = _X.astype('<U10')

        if _trial == 1:
            MASK = truth_mask_1
        elif _trial == 2:
            MASK = truth_mask_2
        elif _trial == 3:
            MASK = np.zeros(_shape).astype(bool)
        else:
            raise Exception

        if _nan_type == 'npnan':
            X[MASK] = np.nan
        elif _nan_type == 'strnan':
            X[MASK] = 'nan'
        elif _nan_type == 'any string':
            X[MASK] = 'any string'
            # this is a valid assignment into a str array
        elif _nan_type == 'pdNA':
            X[MASK] = pd.NA
        elif _nan_type == 'none':
            X[MASK] = None
        else:
            raise Exception

        out = nan_mask_string(X)

        out_2 = nan_mask(X)

        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool

        assert isinstance(out_2, np.ndarray)
        assert out_2.shape == _shape
        assert out_2.dtype == bool

        if _nan_type == 'any string':
            assert np.sum(out) == 0
            assert np.sum(out_2) == 0
        else:
            assert np.array_equal(out, MASK)
            assert np.array_equal(out_2, MASK)


    # np str arrays can take any of the folloing representations of nan:
    # np.nan, 'nan', pd.NA, None
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_nan_type',
        ('npnan', 'strnan', 'any string', 'pdNA', 'none')
    )
    def test_np_array_str(
        self, _X, truth_mask_1, truth_mask_2, _dim, _trial, _nan_type, _shape
    ):

        X = _X.astype('<U10')

        if _trial == 1:
            MASK = truth_mask_1
        elif _trial == 2:
            MASK = truth_mask_2
        elif _trial == 3:
            MASK = np.zeros(_shape).astype(bool)
        else:
            raise Exception

        if _nan_type == 'npnan':
            X[MASK] = np.nan
        elif _nan_type == 'strnan':
            X[MASK] = 'nan'
        elif _nan_type == 'any string':
            X[MASK] = 'any string'
            # this is a valid assignment into a str array
        elif _nan_type == 'pdNA':
            X[MASK] = pd.NA
        elif _nan_type == 'none':
            X[MASK] = None
        else:
            raise Exception

        out = nan_mask_string(X)

        out_2 = nan_mask(X)

        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool

        assert isinstance(out_2, np.ndarray)
        assert out_2.shape == _shape
        assert out_2.dtype == bool

        if _nan_type == 'any string':
            assert np.sum(out) == 0
            assert np.sum(out_2) == 0
        else:
            assert np.array_equal(out, MASK)
            assert np.array_equal(out_2, MASK)


    # np object arrays can take any of the following representations of nan:
    # np.nan, 'nan', pd.NA, None
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_nan_type',
        ('npnan', 'strnan', 'any string', 'pdNA', 'none')
    )
    def test_np_array_object(
        self, _X, truth_mask_1, truth_mask_2, _dim, _trial, _nan_type, _shape
    ):

        X = _X.astype(object)

        if _trial == 1:
            MASK = truth_mask_1
        elif _trial == 2:
            MASK = truth_mask_2
        elif _trial == 3:
            MASK = np.zeros(_shape).astype(bool)
        else:
            raise Exception

        if _nan_type == 'npnan':
            X[MASK] = np.nan
        elif _nan_type == 'strnan':
            X[MASK] = 'nan'
        elif _nan_type == 'any string':
            X[MASK] = 'any string'
            # this is a valid assignment into a obj array
        elif _nan_type == 'pdNA':
            X[MASK] = pd.NA
        elif _nan_type == 'none':
            X[MASK] = None
        else:
            raise Exception

        if _dim == 1:
            X = X[:, 0].squeeze()
            MASK = MASK[:, 0]
            _shape = (_shape[0], )

        assert X.dtype == object

        out = nan_mask_string(X)

        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool

        out_2 = nan_mask(X)

        assert isinstance(out_2, np.ndarray)
        assert out_2.shape == _shape
        assert out_2.dtype == bool

        if _nan_type == 'any string':
            assert np.sum(out) == 0
            assert np.sum(out_2) == 0
        else:
            assert np.array_equal(out, MASK)
            assert np.array_equal(out_2, MASK)


    # pd str dfs can take any of the following representations of nan:
    # np.nan, 'nan', pd.NA, None
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_nan_type',
        ('npnan', 'strnan', 'any string', 'pdNA', 'none')
    )
    def test_pd_str(
        self, _X, truth_mask_1, truth_mask_2, _dim, _trial, _nan_type, _shape,
        _columns, pd_assnmt_handle
    ):

        X = pd.DataFrame(
            data = _X,
            columns = _columns,
            dtype='<U10'
        )

        if _trial == 1:
            MASK = truth_mask_1
        elif _trial == 2:
            MASK = truth_mask_2
        elif _trial == 3:
            MASK = np.zeros(_shape).astype(bool)
        else:
            raise Exception

        if _dim == 1:
            X = X.iloc[:, 0].squeeze()
            MASK = MASK[:, 0]
            _shape = (_shape[0], )

        if _nan_type == 'npnan':
            X = pd_assnmt_handle(X, MASK, np.nan)
        elif _nan_type == 'strnan':
            X = pd_assnmt_handle(X, MASK, 'nan')
        elif _nan_type == 'any string':
            X = pd_assnmt_handle(X, MASK, 'any string')
            # this is a valid assignment into a pd str type
        elif _nan_type == 'pdNA':
            X = pd_assnmt_handle(X, MASK, pd.NA)
        elif _nan_type == 'none':
            X = pd_assnmt_handle(X, MASK, None)
        else:
            raise Exception

        # if exception is raised by pd_assnmnt_handle because of casting
        # nan to disallowed dtype, then X is None and skip test
        if X is None:
            pytest.skip(reason=f"invalid value cast to dataframe dtype, skip test")

        # pd cant have str dtypes, always coerced to object
        # so that means these tests are redundant with the next tests
        _dtypes = [X.dtypes] if _dim == 1 else list(set(X.dtypes))
        assert len(_dtypes) == 1
        assert _dtypes[0] == object

        out = nan_mask_string(X)

        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool

        out_2 = nan_mask(X)

        assert isinstance(out_2, np.ndarray)
        assert out_2.shape == _shape
        assert out_2.dtype == bool

        if _nan_type == 'any string':
            assert np.sum(out) == 0
            assert np.sum(out_2) == 0
        else:
            assert np.array_equal(out, MASK)
            assert np.array_equal(out_2, MASK)


    # pd obj dfs can take any of the following representations of nan:
    # np.nan, 'nan', pd.NA, None
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_nan_type',
        ('npnan', 'strnan', 'any string', 'pdNA', 'none')
    )
    def test_pd_object(
        self, _X, truth_mask_1, truth_mask_2, _dim, _trial, _nan_type, _shape,
        _columns, pd_assnmt_handle
    ):

        X = pd.DataFrame(
            data = _X,
            columns = _columns,
            dtype=object
        )

        if _trial == 1:
            MASK = truth_mask_1
        elif _trial == 2:
            MASK = truth_mask_2
        elif _trial == 3:
            MASK = np.zeros(_shape).astype(bool)
        else:
            raise Exception

        if _dim == 1:
            X = X.iloc[:, 0].squeeze()
            MASK = MASK[:, 0]
            _shape = (_shape[0], )

        if _nan_type == 'npnan':
            X = pd_assnmt_handle(X, MASK, np.nan)
        elif _nan_type == 'strnan':
            X = pd_assnmt_handle(X, MASK, 'nan')
        elif _nan_type == 'any string':
            X = pd_assnmt_handle(X, MASK, 'any string')
            # this is a valid assignment into a pd object type
        elif _nan_type == 'pdNA':
            X = pd_assnmt_handle(X, MASK, pd.NA)
        elif _nan_type == 'none':
            X = pd_assnmt_handle(X, MASK, None)
        else:
            raise Exception

        # if exception is raised by pd_assnmnt_handle because of casting
        # nan to disallowed dtype, then X is None and skip test
        if X is None:
            pytest.skip(reason=f"invalid value cast to dataframe dtype, skip test")

        _dtypes = [X.dtypes] if _dim == 1 else list(set(X.dtypes))
        assert len(_dtypes) == 1
        assert _dtypes[0] == object

        out = nan_mask_string(X)

        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool

        out_2 = nan_mask(X)

        assert isinstance(out_2, np.ndarray)
        assert out_2.shape == _shape
        assert out_2.dtype == bool

        if _nan_type == 'any string':
            assert np.sum(out) == 0
            assert np.sum(out_2) == 0
        else:
            assert np.array_equal(out, MASK)
            assert np.array_equal(out_2, MASK)


    # polars wont cast any infs to Object
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2))
    @pytest.mark.parametrize('_nan_type',
        ('npnan', 'strnan', 'any string', 'pdNA', 'none')
    )
    def test_polars_object(
        self, _X, truth_mask_1, truth_mask_2, _dim, _trial, _nan_type, _shape,
        _columns
    ):

        # prepare the np array before converting to polars -- -- --

        X = _X.astype(object)

        if _trial == 1:
            MASK = truth_mask_1
        elif _trial == 2:
            MASK = truth_mask_2
        else:
            raise Exception

        if _dim == 1:
            X = X[:, 0]
            MASK = MASK[:, 0]
            _shape = (_shape[0], )

        if _nan_type == 'npnan':
            X[MASK] = np.nan
        elif _nan_type == 'strnan':
            X[MASK] = 'nan'
        elif _nan_type == 'any string':
            X[MASK] = 'any string'
            # this is a valid assignment into a obj array
        elif _nan_type == 'pdNA':
            X[MASK] = pd.NA
        elif _nan_type == 'none':
            X[MASK] = None
        else:
            raise Exception

        assert X.dtype == object

        # END prepare the np array before converting to polars -- --

        # polars wont cast any infs to Object
        # this is raised by polars, let it raise whatever

        with pytest.raises(Exception):
            if _dim == 1:
                pl.Series(X).cast(pl.Object)
            else:
                pl.from_numpy(X).cast(pl.Object)
            pytest.skip(reason=f"cant do later tests after except")




