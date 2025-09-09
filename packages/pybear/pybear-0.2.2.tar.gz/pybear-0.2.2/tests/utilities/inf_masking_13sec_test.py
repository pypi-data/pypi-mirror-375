# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import math
import decimal

import numpy as np
import pandas as pd
import scipy.sparse as ss
import polars as pl

from pybear.utilities._inf_masking import inf_mask



# tests python built-ins, numpy arrays, pandas dataframes, and scipy.sparse
# with various inf-like representations ('inf', '-inf', np.inf, -np.inf,
# np.PINF, np.NINF, math.inf, -math.inf, float('inf'), float('-inf'),
# decimal.Decimal('Infinity'), decimal.Decimal('-Infinity'), for float,
# int, str, and object dtypes.

# np.PINF and np.NINF were removed from numpy 2.0. Want to be able to
# handle and test for older versions of numpy. But supposedly these
# constants are just aliases for numpy.inf and -numpy.inf, so these
# tests assume that tests for np.PINF np.NINF are accomplished by the
# tests for np.inf and -np.inf.


@pytest.fixture(scope='module')
def truth_mask_1(_shape):
    """Random mask for building containers with inf in them."""
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
def truth_mask_2(_shape):
    """Random mask for building containers with inf in them."""
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
    """Wrap inf assignments to pd dataframes in try except block."""
    # 25_01_07 pandas future warnings about casting incompatible
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



class TestInfMaskNumeric:


    @pytest.mark.parametrize('_container', (list, tuple, set))
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_inf_type',
        ('npinf', '-npinf', 'mathinf', '-mathinf', 'strinf', '-strinf',
         'floatinf', '-floatinf', 'decimalInfinity', '-decimalInfinity')
    )
    def test_python_builtins_num(
        self, _shape, truth_mask_1, truth_mask_2, _container, _dim, _trial,
        _inf_type
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

        if _inf_type == 'npinf':
            X[MASK] = np.inf
        elif _inf_type == '-npinf':
            X[MASK] = -np.inf
        elif _inf_type == 'mathinf':
            X[MASK] = math.inf
        elif _inf_type == '-mathinf':
            X[MASK] = -math.inf
        elif _inf_type == 'strinf':
            X[MASK] = 'inf'
        elif _inf_type == '-strinf':
            X[MASK] = '-inf'
        elif _inf_type == 'floatinf':
            X[MASK] = float('inf')
        elif _inf_type == '-floatinf':
            X[MASK] = float('-inf')
        elif _inf_type == 'decimalInfinity':
            X[MASK] = decimal.Decimal('Infinity')
        elif _inf_type == '-decimalInfinity':
            X[MASK] = decimal.Decimal('-Infinity')
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

        out = inf_mask(X)

        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool
        assert np.array_equal(out, MASK)


    # the only np numerical dtype that can take inf is np.float64
    # and it can take all of the inf-like forms tested here while staying
    # in the float64 dtype.
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_inf_type',
        ('npinf', '-npinf', 'mathinf', '-mathinf', 'strinf', '-strinf',
         'floatinf', '-floatinf', 'decimalInfinity', '-decimalInfinity')
    )
    def test_np_float_array(
        self, _shape, truth_mask_1, truth_mask_2, _dim, _trial, _inf_type
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

        if _inf_type == 'npinf':
            X[MASK] = np.inf
        elif _inf_type == '-npinf':
            X[MASK] = -np.inf
        elif _inf_type == 'mathinf':
            X[MASK] = math.inf
        elif _inf_type == '-mathinf':
            X[MASK] = -math.inf
        elif _inf_type == 'strinf':
            X[MASK] = 'inf'
        elif _inf_type == '-strinf':
            X[MASK] = '-inf'
        elif _inf_type == 'floatinf':
            X[MASK] = float('inf')
        elif _inf_type == '-floatinf':
            X[MASK] = float('-inf')
        elif _inf_type == 'decimalInfinity':
            X[MASK] = decimal.Decimal('Infinity')
        elif _inf_type == '-decimalInfinity':
            X[MASK] = decimal.Decimal('-Infinity')
        else:
            raise Exception

        if _dim == 1:
            X = X[:, 0]
            MASK = MASK[:, 0]
            _shape = (_shape[0], )

        # 'inf', '-inf',  decimal.Decimal('Infinity'), decimal.Decimal('-Infinity')
        # are not changing dtype from float64 to object!
        assert X.dtype == np.float64

        out = inf_mask(X)

        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool
        assert np.array_equal(out, MASK)


    # numpy integer array cannot take any representation of inf, raises
    # OverflowError. would need to convert X to float64.
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2))
    @pytest.mark.parametrize('_inf_type',
        ('npinf', '-npinf', 'mathinf', '-mathinf', 'strinf', '-strinf',
         'floatinf', '-floatinf', 'decimalInfinity', '-decimalInfinity',
         'noinf')
    )
    def test_np_int_array(
        self, _shape, truth_mask_1, truth_mask_2, _dim, _trial, _inf_type
    ):

        # all inf-likes raise exception when casting into int dtypes

        # this is also testing an int dtype with no infs to see if
        # inf_mask() can take int dtype (and return a mask of all Falses).

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
        if _inf_type == 'npinf':
            with pytest.raises(OverflowError):
                X[MASK] = np.inf
            pytest.skip()
        elif _inf_type == '-npinf':
            with pytest.raises(OverflowError):
                X[MASK] = -np.inf
            pytest.skip()
        elif _inf_type == 'mathinf':
            with pytest.raises(OverflowError):
                X[MASK] = math.inf
            pytest.skip()
        elif _inf_type == '-mathinf':
            with pytest.raises(OverflowError):
                X[MASK] = -math.inf
            pytest.skip()
        elif _inf_type == 'strinf':
            with pytest.raises(ValueError):
                X[MASK] = 'inf'
            pytest.skip()
        elif _inf_type == '-strinf':
            with pytest.raises(ValueError):
                X[MASK] = '-inf'
            pytest.skip()
        elif _inf_type == 'floatinf':
            with pytest.raises(OverflowError):
                X[MASK] = float('inf')
            pytest.skip()
        elif _inf_type == '-floatinf':
            with pytest.raises(OverflowError):
                X[MASK] = float('-inf')
            pytest.skip()
        elif _inf_type == 'decimalInfinity':
            with pytest.raises(OverflowError):
                X[MASK] = decimal.Decimal('Infinity')
            pytest.skip()
        elif _inf_type == '-decimalInfinity':
            with pytest.raises(OverflowError):
                X[MASK] = decimal.Decimal('-Infinity')
            pytest.skip()
        elif _inf_type == 'noinf':
            out = inf_mask(X)
            assert isinstance(out, np.ndarray)
            assert out.shape == _shape
            assert out.dtype == bool
            assert np.array_equal(out, np.zeros(X.shape).astype(bool))
        else:
            raise Exception


    # all scipy sparses return infs correctly
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_format',
        (
            'csr_matrix', 'csc_matrix', 'coo_matrix', 'dia_matrix',
            'lil_matrix', 'dok_matrix', 'bsr_matrix', 'csr_array', 'csc_array',
            'coo_array', 'dia_array', 'lil_array', 'dok_array', 'bsr_array'
        )
    )
    @pytest.mark.parametrize('_inf_type',
        ('npinf', '-npinf', 'mathinf', '-mathinf', 'strinf', '-strinf',
         'floatinf', '-floatinf', 'decimalInfinity', '-decimalInfinity')
    )
    def test_scipy_sparse_via_np_float_array(
        self, _shape, truth_mask_1, truth_mask_2, _trial, _format, _inf_type
    ):

        # can only be 2D and numeric

        X = np.random.uniform(0, 1, _shape)

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

        if _inf_type == 'npinf':
            X[MASK] = np.inf
        elif _inf_type == '-npinf':
            X[MASK] = -np.inf
        elif _inf_type == 'mathinf':
            X[MASK] = math.inf
        elif _inf_type == '-mathinf':
            X[MASK] = -math.inf
        elif _inf_type == 'strinf':
            X[MASK] = 'inf'
        elif _inf_type == '-strinf':
            X[MASK] = '-inf'
        elif _inf_type == 'floatinf':
            X[MASK] = float('inf')
        elif _inf_type == '-floatinf':
            X[MASK] = float('-inf')
        elif _inf_type == 'decimalInfinity':
            X[MASK] = decimal.Decimal('Infinity')
        elif _inf_type == '-decimalInfinity':
            X[MASK] = decimal.Decimal('-Infinity')
        else:
            raise Exception

        # 'inf', '-inf', decimal.Decimal('Infinity'), decimal.Decimal('-Infinity')
        # are not changing dtype from float64 to object!
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
                inf_mask(X_wip)
        else:
            ss_out = inf_mask(X_wip)
            assert isinstance(ss_out, np.ndarray)
            assert ss_out.shape == X_wip.data.shape
            assert ss_out.dtype == bool


        # covert back to np to see if inf mask was affected
        X = X_wip.toarray()

        np_out = inf_mask(X)
        assert isinstance(np_out, np.ndarray)
        assert np_out.shape == _shape
        assert np_out.dtype == bool

        assert np.array_equal(np_out, MASK)


    # pd float dfs can take all of the inf-like forms tested here, but some
    # of them are coercing float64 dtype to object dtype.
    # 'strinf' and 'decimalinf' are changing dtype from float64 to object
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_inf_type',
        ('npinf', '-npinf', 'mathinf', '-mathinf', 'strinf', '-strinf',
         'floatinf', '-floatinf', 'decimalInfinity', '-decimalInfinity')
    )
    def test_pd_float(
        self, _shape, truth_mask_1, truth_mask_2, _dim, _trial, _inf_type,
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

        if _inf_type == 'npinf':
            X = pd_assnmt_handle(X, MASK, np.inf)
        elif _inf_type == '-npinf':
            X = pd_assnmt_handle(X, MASK, -np.inf)
        elif _inf_type == 'mathinf':
            X = pd_assnmt_handle(X, MASK, math.inf)
        elif _inf_type == '-mathinf':
            X = pd_assnmt_handle(X, MASK, -math.inf)
        elif _inf_type == 'strinf':
            X = pd_assnmt_handle(X, MASK, 'inf')
        elif _inf_type == '-strinf':
            X = pd_assnmt_handle(X, MASK, '-inf')
        elif _inf_type == 'floatinf':
            X = pd_assnmt_handle(X, MASK, float('inf'))
        elif _inf_type == '-floatinf':
            X = pd_assnmt_handle(X, MASK, float('-inf'))
        elif _inf_type == 'decimalInfinity':
            X = pd_assnmt_handle(X, MASK, decimal.Decimal('Infinity'))
        elif _inf_type == '-decimalInfinity':
            X = pd_assnmt_handle(X, MASK, decimal.Decimal('-Infinity'))
        else:
            raise Exception

        if _dim == 1:
            X = X.iloc[:, 0].squeeze()
            MASK = MASK[:, 0]
            _shape = (_shape[0], )

        # if exception is raised by pd_assnmt_handle because of casting
        # inf to disallowed dtype, then X is None and skip test
        if X is None:
            pytest.skip(reason=f"invalid value cast to dataframe dtype, skip test")

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _dtypes = [X.dtypes] if _dim == 1 else list(set(X.dtypes))
        assert len(_dtypes) == 1
        _dtype = _dtypes[0]

        if np.sum(MASK) == 0:
            # when mask makes no assignment, dtype is not changed
            assert _dtype == np.float64
        elif _inf_type in [
            'strinf', '-strinf', 'decimalInfinity', '-decimalInfinity'
        ]:
            # 'strinf' and 'decimalinf' are changing dtype from float64 to object!
            assert _dtype == object
        else:
            # for all other inf assignments, dtypes is not changed
            assert _dtype == np.float64
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        out = inf_mask(X)

        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool
        assert np.array_equal(out, MASK)


    # pd int dfs can take all of the inf-likes being tested here except
    # they coerce the dtypes in the DF to object or float64
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_inf_type',
        ('npinf', '-npinf', 'mathinf', '-mathinf', 'strinf', '-strinf',
         'floatinf', '-floatinf', 'decimalInfinity', '-decimalInfinity')
    )
    def test_pd_int(
        self, _shape, truth_mask_1, truth_mask_2, _dim, _trial, _inf_type,
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

        if _inf_type == 'npinf':
            X = pd_assnmt_handle(X, MASK, np.inf)
        elif _inf_type == '-npinf':
            X = pd_assnmt_handle(X, MASK, -np.inf)
        elif _inf_type == 'mathinf':
            X = pd_assnmt_handle(X, MASK, math.inf)
        elif _inf_type == '-mathinf':
            X = pd_assnmt_handle(X, MASK, -math.inf)
        elif _inf_type == 'strinf':
            X = pd_assnmt_handle(X, MASK, 'inf')
        elif _inf_type == '-strinf':
            X = pd_assnmt_handle(X, MASK, '-inf')
        elif _inf_type == 'floatinf':
            X = pd_assnmt_handle(X, MASK, float('inf'))
        elif _inf_type == '-floatinf':
            X = pd_assnmt_handle(X, MASK, float('-inf'))
        elif _inf_type == 'decimalInfinity':
            X = pd_assnmt_handle(X, MASK, decimal.Decimal('Infinity'))
        elif _inf_type == '-decimalInfinity':
            X = pd_assnmt_handle(X, MASK, decimal.Decimal('-Infinity'))
        else:
            raise Exception

        if _dim == 1:
            X = X.iloc[:, 0].squeeze()
            MASK = MASK[:, 0]
            _shape = (_shape[0], )

        # if exception is raised by pd_assnmt_handle because of casting
        # inf to disallowed dtype, then X is None and skip test
        if X is None:
            pytest.skip(reason=f"invalid value cast to dataframe dtype, skip test")

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _dtypes = [X.dtypes] if _dim == 1 else list(set(X.dtypes))
        assert len(_dtypes) == 1
        _dtype = _dtypes[0]

        if np.sum(MASK) == 0:
            # if the mask does not assign anything then dtype does not change
            assert _dtype == np.uint32
        elif _inf_type in [
            'strinf', '-strinf', 'decimalInfinity', '-decimalInfinity'
        ]:
            # 'strinf' and 'decimalinf' are changing dtype from float64 to object!
            assert _dtype == object
        else:
            # all other inf types are changing dtype from uint32 to float64!
            assert _dtype == np.float64
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        out = inf_mask(X)

        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool
        assert np.array_equal(out, MASK)


    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_inf_type',
        ('npinf', '-npinf', 'mathinf', '-mathinf', 'strinf', '-strinf',
         'floatinf', '-floatinf', 'decimalInfinity', '-decimalInfinity')
    )
    def test_polars_float(
        self, _shape, truth_mask_1, truth_mask_2, _dim, _trial, _inf_type,
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

        if _inf_type == 'npinf':
            X[MASK] = np.inf
        elif _inf_type == '-npinf':
            X[MASK] = -np.inf
        elif _inf_type == 'mathinf':
            X[MASK] = math.inf
        elif _inf_type == '-mathinf':
            X[MASK] = -math.inf
        elif _inf_type == 'strinf':
            X[MASK] = 'inf'
        elif _inf_type == '-strinf':
            X[MASK] = '-inf'
        elif _inf_type == 'floatinf':
            X[MASK] = float('inf')
        elif _inf_type == '-floatinf':
            X[MASK] = float('-inf')
        elif _inf_type == 'decimalInfinity':
            X[MASK] = decimal.Decimal('Infinity')
        elif _inf_type == '-decimalInfinity':
            X[MASK] = decimal.Decimal('-Infinity')
        else:
            raise Exception

        if _dim == 1:
            X = X[:, 0]
            MASK = MASK[:, 0]
            _shape = (_shape[0], )

        # 'inf', '-inf',  decimal.Decimal('Infinity'), decimal.Decimal('-Infinity')
        # are not changing dtype from float64 to object!
        assert X.dtype == np.float64
        # END prepare the np array for conversion to polars -- -- -- --

        if _dim == 1:
            X = pl.Series(X)
        else:
            X = pl.from_numpy(X, schema=list(_columns))

        out = inf_mask(X)

        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool
        assert np.array_equal(out, MASK)


    # polars wont cast any infs to Int32
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2))
    @pytest.mark.parametrize('_inf_type',
        ('npinf', '-npinf', 'mathinf', '-mathinf', 'strinf', '-strinf',
         'floatinf', '-floatinf', 'decimalInfinity', '-decimalInfinity')
    )
    def test_polars_int(
        self, _shape, truth_mask_1, truth_mask_2, _dim, _trial, _inf_type,
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

        if _inf_type == 'npinf':
            X[MASK] = np.inf
        elif _inf_type == '-npinf':
            X[MASK] = -np.inf
        elif _inf_type == 'mathinf':
            X[MASK] = math.inf
        elif _inf_type == '-mathinf':
            X[MASK] = -math.inf
        elif _inf_type == 'strinf':
            X[MASK] = 'inf'
        elif _inf_type == '-strinf':
            X[MASK] = '-inf'
        elif _inf_type == 'floatinf':
            X[MASK] = float('inf')
        elif _inf_type == '-floatinf':
            X[MASK] = float('-inf')
        elif _inf_type == 'decimalInfinity':
            X[MASK] = decimal.Decimal('Infinity')
        elif _inf_type == '-decimalInfinity':
            X[MASK] = decimal.Decimal('-Infinity')
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
    # inf-like in a dataframe. see if converting to np array via to_numpy()
    # preserves all of the infs in a form that is recognized by inf_mask().
    # takeaway:
    # to_numpy() keeps all of these different infs in a recognizable form
    def test_numpy_via_pd_made_with_various_inf_types(self, _shape, _columns):

        X = pd.DataFrame(
            data = np.random.uniform(0, 1, _shape),
            columns = _columns,
            dtype=np.float64
        )

        _pool = (
            np.inf,
            -np.inf,
            math.inf,
            -math.inf,
            float('inf'),
            float('-inf'),
            decimal.Decimal('Infinity'),
            decimal.Decimal('-Infinity')
        )

        # sprinkle the various inf-types into the float DF,
        # make a ref mask DF to mark the places of the inf-likes
        MASK = np.zeros(_shape).astype(bool)
        for _sprinkling_itr in range(X.size//10):
            _row_idx = np.random.randint(_shape[0])
            _col_idx = np.random.randint(_shape[1])

            X.iloc[_row_idx, _col_idx] = np.random.choice(_pool)
            MASK[_row_idx, _col_idx] = True

        X = X.to_numpy()

        out = inf_mask(X)
        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool
        assert np.array_equal(out, MASK)


    def test_inf_mask_takes_str_numbers(self):

        # 1D -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _X = list(map(str, list(range(10))))

        assert all(map(isinstance, _X, (str for i in _X)))

        _X[1] = 'inf'
        _X[2] = np.inf

        ref = np.zeros((10,)).astype(bool)
        ref[1] = True
        ref[2] = True

        out = inf_mask(_X)

        assert np.array_equal(out, ref)
        # END 1D -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # 2D -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _X = np.random.randint(0, 10, (5, 3)).astype(str)

        assert all(map(isinstance, _X[0], (str for _ in _X[0])))

        _X[1][0] = 'inf'
        _X[2][0] = np.inf

        ref = np.zeros((5, 3)).astype(bool)
        ref[1][0] = True
        ref[2][0] = True
        ref = ref.tolist()

        out = inf_mask(_X)

        assert np.array_equal(out, ref)

        # END 2D -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


class TestInfMaskString:

    # scipy sparse cannot take non-numeric datatypes

    @staticmethod
    @pytest.fixture()
    def _X(_shape):
        return np.random.choice(list('abcdefghij'), _shape, replace=True)


    @pytest.mark.parametrize('_container', (list, tuple, set))
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_inf_type',
        ('npinf', '-npinf', 'mathinf', '-mathinf', 'strinf', '-strinf',
         'floatinf', '-floatinf', 'decimalInfinity', '-decimalInfinity')
    )
    def test_python_builtins_str(
        self, _X, truth_mask_1, truth_mask_2, _container, _dim, _trial, _inf_type,
        _shape
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


        X = _X.astype('<U20')

        if _trial == 1:
            MASK = truth_mask_1
        elif _trial == 2:
            MASK = truth_mask_2
        elif _trial == 3:
            MASK = np.zeros(_shape).astype(bool)
        else:
            raise Exception

        if _inf_type == 'npinf':
            X[MASK] = np.inf
        elif _inf_type == '-npinf':
            X[MASK] = -np.inf
        elif _inf_type == 'mathinf':
            X[MASK] = math.inf
        elif _inf_type == '-mathinf':
            X[MASK] = -math.inf
        elif _inf_type == 'strinf':
            X[MASK] = 'inf'
        elif _inf_type == '-strinf':
            X[MASK] = '-inf'
        elif _inf_type == 'floatinf':
            X[MASK] = float('inf')
        elif _inf_type == '-floatinf':
            X[MASK] = float('-inf')
        elif _inf_type == 'decimalInfinity':
            X[MASK] = decimal.Decimal('Infinity')
        elif _inf_type == '-decimalInfinity':
            X[MASK] = decimal.Decimal('-Infinity')
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

        out = inf_mask(X)

        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool
        assert np.array_equal(out, MASK)


    # np str arrays can take all of the inf representations being tested.
    # decimal.Decimal is coerced to str('Infinity') or str('-Infinity'),
    # all others are coerced to str('inf') or str('-inf').
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_inf_type',
        ('npinf', '-npinf', 'mathinf', '-mathinf', 'strinf', '-strinf',
         'floatinf', '-floatinf', 'decimalInfinity', '-decimalInfinity')
    )
    def test_np_array_str(
        self, _X, truth_mask_1, truth_mask_2, _dim, _trial, _inf_type, _shape
    ):

        X = _X.astype('<U20')

        if _trial == 1:
            MASK = truth_mask_1
        elif _trial == 2:
            MASK = truth_mask_2
        elif _trial == 3:
            MASK = np.zeros(_shape).astype(bool)
        else:
            raise Exception

        if _inf_type == 'npinf':
            X[MASK] = np.inf
        elif _inf_type == '-npinf':
            X[MASK] = -np.inf
        elif _inf_type == 'mathinf':
            X[MASK] = math.inf
        elif _inf_type == '-mathinf':
            X[MASK] = -math.inf
        elif _inf_type == 'strinf':
            X[MASK] = 'inf'
        elif _inf_type == '-strinf':
            X[MASK] = '-inf'
        elif _inf_type == 'floatinf':
            X[MASK] = float('inf')
        elif _inf_type == '-floatinf':
            X[MASK] = float('-inf')
        elif _inf_type == 'decimalInfinity':
            X[MASK] = decimal.Decimal('Infinity')
        elif _inf_type == '-decimalInfinity':
            X[MASK] = decimal.Decimal('-Infinity')
        else:
            raise Exception

        if _dim == 1:
            X = X[:, 0].squeeze()
            MASK = MASK[:, 0]
            _shape = (_shape[0], )

        assert X.dtype == '<U20'

        out = inf_mask(X)

        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool
        assert np.array_equal(out, MASK)


    # np object arrays can take all of the inf representations being tested.
    # because this is an object array, the inf-likes are not coerced to a
    # different format, they are kept as given. This has implications for
    # the way inf_mask() is built. see the inf_mask module.
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_inf_type',
        ('npinf', '-npinf', 'mathinf', '-mathinf', 'strinf', '-strinf',
         'floatinf', '-floatinf', 'decimalInfinity', '-decimalInfinity')
    )
    def test_np_array_object(
        self, _X, truth_mask_1, truth_mask_2, _dim, _trial, _inf_type, _shape
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

        if _inf_type == 'npinf':
            X[MASK] = np.inf
        elif _inf_type == '-npinf':
            X[MASK] = -np.inf
        elif _inf_type == 'mathinf':
            X[MASK] = math.inf
        elif _inf_type == '-mathinf':
            X[MASK] = -math.inf
        elif _inf_type == 'strinf':
            X[MASK] = 'inf'
        elif _inf_type == '-strinf':
            X[MASK] = '-inf'
        elif _inf_type == 'floatinf':
            X[MASK] = float('inf')
        elif _inf_type == '-floatinf':
            X[MASK] = float('-inf')
        elif _inf_type == 'decimalInfinity':
            X[MASK] = decimal.Decimal('Infinity')
        elif _inf_type == '-decimalInfinity':
            X[MASK] = decimal.Decimal('-Infinity')
        else:
            raise Exception

        if _dim == 1:
            X = X[:, 0].squeeze()
            MASK = MASK[:, 0]
            _shape = (_shape[0], )

        assert X.dtype == object

        out = inf_mask(X)

        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool
        assert np.array_equal(out, MASK)


    # pd str dfs take all of the inf representations being tested....
    # pd cant have str dtype it is always coerced to object
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_inf_type',
        ('npinf', '-npinf', 'mathinf', '-mathinf', 'strinf', '-strinf',
         'floatinf', '-floatinf', 'decimalInfinity', '-decimalInfinity')
    )
    def test_pd_str(
        self, _X, truth_mask_1, truth_mask_2, _dim, _trial, _inf_type, _shape,
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

        if _inf_type == 'npinf':
            X = pd_assnmt_handle(X, MASK, np.inf)
        elif _inf_type == '-npinf':
            X = pd_assnmt_handle(X, MASK, -np.inf)
        elif _inf_type == 'mathinf':
            X = pd_assnmt_handle(X, MASK, math.inf)
        elif _inf_type == '-mathinf':
            X = pd_assnmt_handle(X, MASK, -math.inf)
        elif _inf_type == 'strinf':
            X = pd_assnmt_handle(X,  MASK, 'inf')
        elif _inf_type == '-strinf':
            X = pd_assnmt_handle(X, MASK, '-inf')
        elif _inf_type == 'floatinf':
            X = pd_assnmt_handle(X,  MASK, float('inf'))
        elif _inf_type == '-floatinf':
            X = pd_assnmt_handle(X,  MASK, float('-inf'))
        elif _inf_type == 'decimalInfinity':
            X = pd_assnmt_handle(X,  MASK, decimal.Decimal('Infinity'))
        elif _inf_type == '-decimalInfinity':
            X = pd_assnmt_handle(X, MASK, decimal.Decimal('-Infinity'))
        else:
            raise Exception


        # if exception is raised by pd_assnmt_handle because of casting
        # inf to disallowed dtype, then X is None and skip test
        if X is None:
            pytest.skip(reason=f"invalid value cast to dataframe dtype, skip test")

        # pd cant have str dtypes, always coerced to object
        # so that means these tests are redundant with the next tests
        _dtypes = [X.dtypes] if _dim == 1 else list(set(X.dtypes))
        assert len(_dtypes) == 1
        assert _dtypes[0] == object

        out = inf_mask(X)

        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool
        assert np.array_equal(out, MASK)


    # pd obj dfs can take all of the inf representations being tested
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_inf_type',
        ('npinf', '-npinf', 'mathinf', '-mathinf', 'strinf', '-strinf',
         'floatinf', '-floatinf', 'decimalInfinity', '-decimalInfinity')
    )
    def test_pd_object(
        self, _X, truth_mask_1, truth_mask_2, _dim, _trial, _inf_type, _shape,
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

        if _inf_type == 'npinf':
            X = pd_assnmt_handle(X,  MASK, np.inf)
        elif _inf_type == '-npinf':
            X = pd_assnmt_handle(X, MASK, -np.inf)
        elif _inf_type == 'mathinf':
            X = pd_assnmt_handle(X, MASK, math.inf)
        elif _inf_type == '-mathinf':
            X = pd_assnmt_handle(X, MASK, -math.inf)
        elif _inf_type == 'strinf':
            X = pd_assnmt_handle(X, MASK, 'inf')
        elif _inf_type == '-strinf':
            X = pd_assnmt_handle(X, MASK, '-inf')
        elif _inf_type == 'floatinf':
            X = pd_assnmt_handle(X, MASK, float('inf'))
        elif _inf_type == '-floatinf':
            X = pd_assnmt_handle(X, MASK, float('-inf'))
        elif _inf_type == 'decimalInfinity':
            X = pd_assnmt_handle(X, MASK, decimal.Decimal('Infinity'))
        elif _inf_type == '-decimalInfinity':
            X = pd_assnmt_handle(X, MASK, decimal.Decimal('-Infinity'))
        else:
            raise Exception

        # if exception is raised by pd_assnmt_handle because of casting
        # inf to disallowed dtype, then X is None and skip test
        if X is None:
            pytest.skip(reason=f"invalid value cast to dataframe dtype, skip test")

        _dtypes = [X.dtypes] if _dim == 1 else list(set(X.dtypes))
        assert len(_dtypes) == 1
        assert _dtypes[0] == object

        out = inf_mask(X)

        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool
        assert np.array_equal(out, MASK)


    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2, 3))
    @pytest.mark.parametrize('_inf_type',
        ('npinf', '-npinf', 'mathinf', '-mathinf', 'strinf', '-strinf',
         'floatinf', '-floatinf', 'decimalInfinity', '-decimalInfinity')
    )
    def test_polars_str(
        self, _X, truth_mask_1, truth_mask_2, _dim, _trial, _inf_type, _shape,
        _columns
    ):

        # prepare the np array before converting to polars -- -- --

        X = _X.astype('<U10')

        if _trial == 1:
            MASK = truth_mask_1
        elif _trial == 2:
            MASK = truth_mask_2
        elif _trial == 3:
            MASK = np.zeros(_shape).astype(bool)
        else:
            raise Exception

        if _dim == 1:
            X = X[:, 0].squeeze()
            MASK = MASK[:, 0]
            _shape = (_shape[0], )

        if _inf_type == 'npinf':
            X[MASK] = np.inf
        elif _inf_type == '-npinf':
            X[MASK] = -np.inf
        elif _inf_type == 'mathinf':
            X[MASK] = math.inf
        elif _inf_type == '-mathinf':
            X[MASK] = -math.inf
        elif _inf_type == 'strinf':
            X[MASK] = 'inf'
        elif _inf_type == '-strinf':
            X[MASK] = '-inf'
        elif _inf_type == 'floatinf':
            X[MASK] = float('inf')
        elif _inf_type == '-floatinf':
            X[MASK] = float('-inf')
        elif _inf_type == 'decimalInfinity':
            X[MASK] = decimal.Decimal('Infinity')
        elif _inf_type == '-decimalInfinity':
            X[MASK] = decimal.Decimal('-Infinity')
        else:
            raise Exception

        assert X.dtype == '<U10'
        # END prepare the np array before converting to polars -- -- --

        if _dim == 1:
            X = pl.Series(X).cast(pl.Utf8)
        else:
            X = pl.from_numpy(X, schema=list(_columns)).cast(pl.Utf8)

        out = inf_mask(X)

        assert isinstance(out, np.ndarray)
        assert out.shape == _shape
        assert out.dtype == bool
        assert np.array_equal(out, MASK)


    # polars wont cast any infs to Object
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_trial', (1, 2))
    @pytest.mark.parametrize('_inf_type',
        ('npinf', '-npinf', 'mathinf', '-mathinf', 'strinf', '-strinf',
         'floatinf', '-floatinf', 'decimalInfinity', '-decimalInfinity')
    )
    def test_polars_object(
        self, _X, truth_mask_1, truth_mask_2, _dim, _trial, _inf_type, _shape,
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

        if _inf_type == 'npinf':
            X[MASK] = np.inf
        elif _inf_type == '-npinf':
            X[MASK] = -np.inf
        elif _inf_type == 'mathinf':
            X[MASK] = math.inf
        elif _inf_type == '-mathinf':
            X[MASK] = -math.inf
        elif _inf_type == 'strinf':
            X[MASK] = 'inf'
        elif _inf_type == '-strinf':
            X[MASK] = '-inf'
        elif _inf_type == 'floatinf':
            X[MASK] = float('inf')
        elif _inf_type == '-floatinf':
            X[MASK] = float('-inf')
        elif _inf_type == 'decimalInfinity':
            X[MASK] = decimal.Decimal('Infinity')
        elif _inf_type == '-decimalInfinity':
            X[MASK] = decimal.Decimal('-Infinity')
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




