# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy
import uuid

import numpy as np
np.random.seed(0)
import pandas as pd
import polars as pl
import scipy.sparse as ss

from sklearn.preprocessing import OneHotEncoder

from pybear.preprocessing import MinCountTransformer as MCT

from pybear.base.exceptions import NotFittedError

from pybear.utilities._nan_masking import nan_mask



bypass = False


# v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
# SET X, y DIMENSIONS AND DEFAULT THRESHOLD FOR TESTING MCT

@pytest.fixture(scope='session')
def _mct_rows():
    # _mct_rows must be between 50 and 750
    # this is fixed, all MCT test (not mmct test) objects have this many
    # rows (mmct rows is set by the construction parameters when a
    # suitable set of vectors for building mmct is found, remember)
    return 100


@pytest.fixture(scope='session')
def _mct_cols():
    # _mct_cols must be > 0
    # this sets the number of columns for each data type! not the total
    # number of columns in X! See the logic inside build_test_objects_for_MCT
    # to get how many columns are actually returned. That number is held
    # in fixture 'x_cols'.
    return 2


@pytest.fixture(scope='session')
def _kwargs(_mct_rows):
    return {
        'count_threshold': _mct_rows // 20,
        'ignore_float_columns': True,
        'ignore_non_binary_integer_columns': True,
        'ignore_columns': None,
        'ignore_nan': True,
        'delete_axis_0': True,
        'handle_as_bool': None,
        'reject_unseen_values': False,
        'max_recursions': 1
    }

# END SET X, y DIMENSIONS AND DEFAULT THRESHOLD FOR TESTING MCT
# v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^




# build X, NO_NAN_X, DTYPE_KEY, x_rows, x_cols for MCT test (not mmct test!)

@pytest.fixture(scope='session')
def build_test_objects_for_MCT(mmct, _mct_rows, _mct_cols, _kwargs):

    # This constructs a test array "X" of randomly filled vectors that
    # have certain criteria like a certain number of certain types of
    # columns, certain amounts of uniques, certain proportions of uniques,
    # to make X manipulable with certain outcomes across all tests. The
    # vectors are filled randomly and may not always be generated with
    # the expected characteristics in one shot, so this iterates over and
    # over until vectors are created that pass certain tests done on them
    # by mmct.

    _ct = _kwargs['count_threshold']

    ctr = 0
    while True:  # LOOP UNTIL DATA IS SUFFICIENT TO BE USED FOR ALL THE TESTS

        ctr += 1
        _tries = 10
        if ctr >= _tries:
            raise Exception(
                f"\033[91mMinCountThreshold failed at {_tries} attempts "
                f"to generate an appropriate X for test\033[0m")

        # vvv CORE TEST DATA vvv *************************
        # CREATE _mct_cols COLUMNS OF BINARY INTEGERS
        _X = np.random.randint(
            0, 2, (_mct_rows, _mct_cols)
        ).astype(object)
        # CREATE _mct_cols COLUMNS OF NON-BINARY INTEGERS
        _X = np.hstack((
            _X, np.random.randint(
                0, _mct_rows // 15, (_mct_rows, _mct_cols)
            ).astype(object)
        ))
        # CREATE _mct_cols COLUMNS OF FLOATS
        _X = np.hstack((
            _X, np.random.uniform(
                0, 1, (_mct_rows, _mct_cols)
            ).astype(object)
        ))
        # CREATE _mct_cols COLUMNS OF STRS
        _alpha = 'abcdefghijklmnopqrstuvwxyz'
        _alpha = _alpha + _alpha.upper()
        for _ in range(_mct_cols):
            _X = np.hstack((_X,
                np.random.choice(
                    list(_alpha[:_mct_rows // 10]),
                    (_mct_rows,),
                    replace=True
                ).astype(object).reshape((-1, 1))
            ))
        # END ^^^ CORE TEST DATA ^^^ *************************

        # CREATE A COLUMN OF STRS THAT WILL ALWAYS BE DELETED BY FIRST RECURSION
        DUM_STR_COL = np.fromiter(('dum' for _ in range(_mct_rows)), dtype='<U3')
        DUM_STR_COL[0] = 'one'
        DUM_STR_COL[1] = 'two'
        DUM_STR_COL[2] = 'six'
        DUM_STR_COL[3] = 'ten'

        _X = np.hstack((_X, DUM_STR_COL.reshape((-1, 1)).astype(object)))
        del DUM_STR_COL

        # _X SHAPE SHOULD BE (x_rows, 4 * x_cols + 1)
        x_rows = _mct_rows
        x_cols = 4 * _mct_cols + 1

        _DTYPE_KEY = [
            k for k in ['bin_int', 'int', 'float', 'obj'] for j in range(_mct_cols)
        ]
        _DTYPE_KEY += ['obj']

        # KEEP THIS FOR TESTING IF DTYPES RETRIEVED CORRECTLY WITH np.nan MIXED IN
        _NO_NAN_X = _X.copy()

        # FLOAT/STR ONLY --- NO_NAN_X MUST BE REDUCED WHEN STR COLUMNS ARE
        # TRANSFORMED
        FLOAT_STR_X = _NO_NAN_X[:, 2 * _mct_cols:4 * _mct_cols].copy()
        # mmct() args = MOCK_X, MOCK_Y, ign_col, ign_nan, ignore_flt_col,
        # ignore_non_binary_int_col, handle_as_bool, delete_axis_0, ct_thresh
        _X1 = mmct().trfm(_X, None, None, True, True, True, None, True, _ct)
        if np.array_equiv(_X1, FLOAT_STR_X):
            del _X1
            continue
        del _X1

        del FLOAT_STR_X

        # PEPPER 10% OF CORE DATA WITH np.nan
        for _ in range(x_rows * x_cols // 10):
            row_coor = np.random.randint(0, x_rows)
            col_coor = np.random.randint(0, x_cols - 1)
            if col_coor < 3 * _mct_cols:
                _X[row_coor, col_coor] = np.nan
            elif col_coor >= 3 * _mct_cols:
                _X[row_coor, col_coor] = 'nan'
        del row_coor, col_coor

        # MAKE EVERY CORE COLUMN HAVE 2 VALUES THAT CT FAR EXCEEDS
        # count_threshold SO DOESNT ALLOW FULL DELETE
        _repl = x_rows // 3
        _get_idxs = lambda: np.random.choice(range(x_rows), _repl, replace=False)
        # 24_06_05_13_16_00 the assignments here cannot be considated using
        # lambda functions - X is being passed to mmct and it is saying cannot
        # pickle
        for idx in range(_mct_cols):
            _X[_get_idxs(), _mct_cols + idx] = \
                int(np.random.randint(0, x_rows // 20) + idx)
            _X[_get_idxs(), _mct_cols + idx] = \
                int(np.random.randint(0, x_rows // 20) + idx)
            _X[_get_idxs(), 2 * _mct_cols + idx] = np.random.uniform(0, 1) + idx
            _X[_get_idxs(), 2 * _mct_cols + idx] = np.random.uniform(0, 1) + idx
            _X[_get_idxs(), 3 * _mct_cols + idx] = _alpha[:x_rows // 15][idx]
            _X[_get_idxs(), 3 * _mct_cols + idx] = _alpha[:x_rows // 15][idx + 1]

        del idx, _repl, _alpha

        # VERIFY ONE RECURSION OF mmct DELETED THE SACRIFICIAL LAST COLUMN
        # (CORE COLUMNS ARE RIGGED TO NOT BE DELETED)
        # MOCK_X, MOCK_Y, ign_col, ign_nan, ignore_non_binary_int_col,
        # ignore_flt_col, handle_as_bool, delete_axis_0, ct_thresh
        _X1 = mmct().trfm(_X, None, None, False, False, False, None, True, _ct)
        assert not np.array_equiv(_X1[:, -1], _X[:, -1]), \
            "Mock MinCountTransformer did not delete last column"

        if len(_X1.shape) != 2 or 0 in _X1.shape:
            # IF ONE RECURSION DELETES EVERYTHING, BUILD NEW X
            continue
        elif np.array_equiv(_X1[:, :-1], _X[:, :-1]):
            # IF ONE RECURSION DOESNT DELETE ANY ROWS OF THE CORE COLUMNS,
            # BUILD NEW X
            continue

        # IF NUM OF RIGGED IDENTICAL NUMBERS IN ANY FLT COLUMN < THRESHOLD,
        # BUILD NEW X
        for flt_col_idx in range(2 * _mct_cols, 3 * _mct_cols, 1):
            _max_ct = np.unique(
                _X[:, flt_col_idx], return_counts=True
            )[1].max(axis=0)
            if _max_ct < _ct:
                continue
        del _max_ct

        # TRFM OF NON-BINARY INTEGER COLUMNS MUST NOT DELETE EVERYTHING,
        # BUT MUST DELETE SOMETHING
        try:
            _X1 = mmct().trfm(
                _X[:, _mct_cols:(2 * _mct_cols)].copy(),
                None,
                None,
                True,
                False,
                True,
                None,
                False,
                _ct
            )
            # MOCK_X, MOCK_Y, ign_col, ign_nan, ignore_non_binary_int_col,
            # ignore_flt_col, handle_as_bool, delete_axis_0, ct_thresh
            if np.array_equiv(_X1, _X[:, _mct_cols:(2 * _mct_cols)].copy()):
                continue
        except:
            continue

        try_again = False
        # IF ALL CTS OF EVERY STR UNIQUE IS >= THRESHOLD, BUILD NEW X
        for str_col_idx in range(x_cols - 1, x_cols - _mct_cols - 1, -1):
            _min_ct = min(np.unique(_X[:, str_col_idx], return_counts=True)[1])
            if _min_ct >= _ct:
                try_again = True
                break
        if try_again:
            continue
        del _min_ct

        # IF X CANNOT TAKE 2 RECURSIONS WITH THRESHOLD==3, BUILD NEW X
        try_again = False
        _X1 = mmct().trfm(_X, None, None, False, False, False, None, True, 3)
        # MOCK_X, MOCK_Y, ign_col, ign_nan, ignore_non_binary_int_col,
        # ignore_flt_col, handle_as_bool, delete_axis_0, ct_thresh
        try:
            # THIS SHOULD EXCEPT IF ALL ROWS/COLUMNS WOULD BE DELETED
            _X2 = mmct().trfm(_X1, None, None, False, False, False, None, True, 3)
            # SECOND RECURSION SHOULD ALSO DELETE SOMETHING, BUT NOT EVERYTHING
            if np.array_equiv(_X1, _X2):
                try_again = True
        except:
            try_again = True

        if try_again:
            continue

        del try_again, _X1, _X2

        # IF X PASSED ALL THESE PRE-CONDITION TESTS, IT IS GOOD TO USE FOR TEST
        break

    # IF X PASSED ALL THESE PRE-CONDITION TESTS, IT IS GOOD TO USE FOR TEST

    return _X, _NO_NAN_X, _DTYPE_KEY, x_rows, x_cols


@pytest.fixture(scope='session')
def NAN_X(build_test_objects_for_MCT):
    return build_test_objects_for_MCT[0]


@pytest.fixture(scope='session')
def NO_NAN_X(build_test_objects_for_MCT):
    return build_test_objects_for_MCT[1]


@pytest.fixture(scope='session')
def DTYPE_KEY(build_test_objects_for_MCT):
    return build_test_objects_for_MCT[2]


@pytest.fixture(scope='session')
def x_rows(build_test_objects_for_MCT):
    return build_test_objects_for_MCT[3]


@pytest.fixture(scope='session')
def x_cols(build_test_objects_for_MCT):
    return build_test_objects_for_MCT[4]


@pytest.fixture(scope='session')
def COLUMNS(x_cols):
    return [str(uuid.uuid4())[:8] for _ in range(x_cols)]

# END build X_np, NO_NAN_X, DTYPE_KEY, x_rows, x_cols for MCT test (not mmct test!)

# END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
# ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
# ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


# test input validation ** * ** * ** * ** * ** * ** * ** * ** * ** * **
@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestInitValidation:


    # _ignore_float_columns, _ignore_non_binary_integer_columns, _ignore_nan,
    # _delete_axis_0, reject_unseen_values ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('_param',
        ('ignore_float_columns', 'ignore_non_binary_integer_columns',
            'delete_axis_0', 'ignore_nan', 'reject_unseen_values')
    )
    @pytest.mark.parametrize('junk_value',
        (None, np.pi, 0, 1, min, (1, 2), [1, 2], {1, 2}, {'a': 1}, lambda x: x)
    )
    def test_bool_kwargs_reject_non_bool(
        self, X_np, y_np, _kwargs, _param, junk_value
    ):

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs[_param] = junk_value

        TestCls = MCT(**_new_kwargs)
        with pytest.raises(TypeError):
            TestCls.fit_transform(X_np, y_np)


    @pytest.mark.parametrize('_param',
        ('ignore_float_columns', 'ignore_non_binary_integer_columns',
         'delete_axis_0', 'ignore_nan', 'reject_unseen_values')
    )
    @pytest.mark.parametrize('good_value', (True, False))
    def test_bool_kwargs_accept_bool(self, X_np, y_np, _kwargs, _param, good_value):

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs[_param] = good_value
        TestCls = MCT(**_new_kwargs)
        TestCls.fit_transform(X_np, y_np)
    # END _ignore_float_columns, _ignore_non_binary_integer_columns,
    # _ignore_nan, _delete_axis_0, reject_unseen_values ** * ** * ** *


    # count_threshold ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('junk_ct',
        (float('inf'), True, False, None, 'junk', {'a': 1}, lambda x: x)
    )
    def test_junk_thresh(self, X_np, y_np, _kwargs, junk_ct):

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['count_threshold'] = junk_ct
        TestCls = MCT(**_new_kwargs)

        with pytest.raises(TypeError):
            TestCls.fit_transform(X_np, y_np)


    @pytest.mark.parametrize('bad_ct',
        (np.pi, -2, 1, 100_000_000, 'bad_list_1', 'bad_list_2')
    )
    def test_bad_thresh(self, X_np, y_np, _kwargs, bad_ct):

        if bad_ct == 'bad_list_1':
            bad_ct = [1] * X_np.shape[1]
        elif bad_ct == 'bad_list_2':
            bad_ct = range(X_np.shape[1])

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['count_threshold'] = bad_ct
        TestCls = MCT(**_new_kwargs)

        with pytest.raises(ValueError):
            TestCls.fit_transform(X_np, y_np)


    @pytest.mark.parametrize('good_ct', (3, 5, 'good_list_1'))
    def test_good_thresh(self, X_np, y_np, _kwargs, good_ct):

        if good_ct == 'good_list_1':
            good_ct = np.random.randint(1, 10, (X_np.shape[1],)).tolist()

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['count_threshold'] = good_ct
        TestCls = MCT(**_new_kwargs)
        TestCls.fit_transform(X_np, y_np)
    # END TEST count_threshold ** * ** * ** * ** * ** * ** * ** * ** *


    # max_recursions ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('junk_mr',
        (np.pi, np.nan, float('inf'), True, False, None, 'junk', [1,2],
        (1,2), {1,2}, {'a': 1}, lambda x: x)
    )
    def test_junk_rcr(self, X_np, y_np, _kwargs, junk_mr):

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['max_recursions'] = junk_mr
        TestCls = MCT(**_new_kwargs)

        with pytest.raises(TypeError):
            TestCls.fit_transform(X_np, y_np)


    @pytest.mark.parametrize('bad_mr', (-1, 0))
    def test_bad_rcr(self, X_np, y_np, _kwargs, bad_mr):

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['max_recursions'] = bad_mr
        TestCls = MCT(**_new_kwargs)

        with pytest.raises(ValueError):
            TestCls.fit_transform(X_np, y_np)


    @pytest.mark.parametrize('good_mr', (1, 10))
    def test_good_rcr(self, X_np, y_np, _kwargs, good_mr):

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['max_recursions'] = good_mr
        TestCls = MCT(**_new_kwargs)

        TestCls.fit_transform(X_np, y_np)
    # END max_recursions ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    # ignore_columns / handle_as_bool ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('junk_value',
        (0, 1, 3.14, True, False, 'junk', np.nan, {0: 'a', 1: 'b'},
        [True, False, None, 'junk'], 'get_from_columns', [np.nan],
        'bad_callable')
    )
    @pytest.mark.parametrize('_param', ('ignore_columns', 'handle_as_bool'))
    def test_junk_ign_cols_handle_as_bool(
        self, X_np, _columns, y_np, _kwargs, junk_value, _param
    ):

        _new_kwargs = deepcopy(_kwargs)
        if junk_value == 'get_from_columns':
            _new_kwargs[_param] = [1, 3, _columns[6]]
        elif junk_value == 'bad_callable':
            _new_kwargs[_param] = lambda X: 'unrecognizable junk'
        else:
            _new_kwargs[_param] = junk_value

        TestCls = MCT(**_new_kwargs)

        with pytest.raises(TypeError):
            TestCls.fit_transform(X_np, y_np)


    @pytest.mark.parametrize('_param', ('ignore_columns', 'handle_as_bool'))
    def test_bad_ign_cols_handle_as_bool(
        self, X_np, _columns, y_np, _kwargs, _param, _mct_cols
    ):

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs[_param] = [1000, 1001, 1002]
        TestCls = MCT(**_new_kwargs)

        with pytest.raises(ValueError):
            TestCls.fit_transform(X_np, y_np)


    @pytest.mark.parametrize('x_format', ('np', 'pd', 'pl'))
    @pytest.mark.parametrize('kwarg_input',
        ([], [0], 'make_from_cols', 'get_from_columns', 'good_callable')
    )
    @pytest.mark.parametrize('_param', ('ignore_columns', 'handle_as_bool'))
    def test_accepts_good_ign_cols_handle_as_bool(
        self, X_np, _columns, y_np, _kwargs, x_format, kwarg_input, _param,
        _mct_cols, x_cols
    ):

        # skip impossible conditions -- -- -- -- -- -- -- -- -- -- -- --
        if kwarg_input == 'get_from_columns' and x_format == 'np':
            pytest.skip(reason=f"cannot use column names when header is not given")
        # END skip impossible conditions -- -- -- -- -- -- -- -- -- --  

        _new_kwargs = deepcopy(_kwargs)

        _col_idxs = range(_mct_cols, 2*_mct_cols)

        if kwarg_input == 'get_from_columns':
            _new_kwargs[_param] = [_columns[j] for j in _col_idxs]
        elif kwarg_input == 'good_callable':
            _new_kwargs[_param] = lambda X: list(_col_idxs)
        elif kwarg_input == 'make_from_cols':
            _new_kwargs[_param] = list(_col_idxs)
        else:
            _new_kwargs[_param] = kwarg_input

        if x_format == 'np':
            _X_wip = X_np.copy()
        elif x_format == 'pd':
            _X_wip = pd.DataFrame(data=X_np, columns=_columns, dtype=object)
        elif x_format == 'pl':
            _X_wip = pl.from_numpy(X_np, schema=list(_columns))
        else:
            raise Exception

        TestCls = MCT(**_new_kwargs)

        TestCls.fit_transform(_X_wip, y_np)

    # END ignore_columns / handle_as_bool ** * ** * ** * ** * ** * ** *

# END test input validation ** * ** * ** * ** * ** * ** * ** * ** * ** *


# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
# TEST PARAM ACCURACY ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

# TEST ignore_float_columns WORKS ######################################
@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestIgnoreFloatColumnsWorks:


    def test_ignore_float_columns_works(self, NO_NAN_X, _kwargs, _mct_cols):

        # FLOAT ONLY COLUMNS SHOULD BE 3rd GROUP OF COLUMNS
        FLOAT_ONLY_X = NO_NAN_X[:, (2 * _mct_cols):(3 * _mct_cols)]

        # ignore_float_columns = False SHOULD delete all columns and rows
        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['ignore_float_columns'] = False
        TestCls = MCT(**_new_kwargs)

        with pytest.raises(ValueError):
            TestCls.fit_transform(FLOAT_ONLY_X)
        # END ignore_float_columns = False SHOULD delete all columns and rows

        # ignore_float_columns = True SHOULD not delete anything -- --
        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['ignore_float_columns'] = True
        TestCls = MCT(**_new_kwargs)

        assert np.array_equiv(TestCls.fit_transform(FLOAT_ONLY_X), FLOAT_ONLY_X)
        # END ignore_float_columns = True SHOULD not delete anything --

# END TEST ignore_float_columns WORKS ##################################


# TEST ignore_non_binary_integer_columns WORKS #########################

@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestIgnoreNonBinaryIntegerColumnsWorks:


    def test_ignore_non_binary_integer_columns_works(
        self, NO_NAN_X, y_np, _kwargs, _mct_cols
    ):

        # NON-BINARY INTEGER COLUMNS SHOULD BE 2nd GROUP OF COLUMNS
        NON_BIN_INT_ONLY_X = NO_NAN_X[:, _mct_cols:(2 * _mct_cols)]
        # chop rows off X until one value is below thresh
        for r_idx in range(NON_BIN_INT_ONLY_X.shape[0]-1, -1, -1):
            unqs, cts = np.unique(NON_BIN_INT_ONLY_X[:r_idx, 0], return_counts=True)
            if min(cts) < _kwargs['count_threshold'] \
                    and max(cts) >= _kwargs['count_threshold']:
                NON_BIN_INT_ONLY_X = NON_BIN_INT_ONLY_X[:r_idx, :]
                break
        else:
            raise Exception

        # prove the configuration would delete some rows if int not ignored
        # ignore_non_binary_integer_columns = False deletes some rows
        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['ignore_non_binary_integer_columns'] = False
        _new_kwargs['count_threshold']

        assert not np.array_equiv(
            MCT(**_new_kwargs).fit_transform(NON_BIN_INT_ONLY_X),
            NON_BIN_INT_ONLY_X
        )

        # prove that the same configuration does not delete when ignored
        # ignore_non_binary_integer_columns = True
        # SHOULD not delete anything
        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['ignore_non_binary_integer_columns'] = True

        assert np.array_equiv(
            MCT(**_new_kwargs).fit_transform(NON_BIN_INT_ONLY_X),
            NON_BIN_INT_ONLY_X
        )

# END TEST ignore_non_binary_integer_columns WORKS #####################


# TEST ignore_nan WORKS ################################################
@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestIgnoreNanWorks:


    def test_ignore_nan_works(self, y_np, _kwargs, x_rows):

        # rig an X that wouldnt have anything deleted
        _X_wip = np.random.randint(0, 2, (x_rows,)).astype(np.float64)

        # sprinkle < thresh nans on X so that they would be deleted
        _thresh = _kwargs['count_threshold']
        NAN_MASK = np.zeros((x_rows, )).astype(bool)
        NAN_MASK[np.random.choice(range(x_rows), _thresh-1, replace=False)] = True
        _X_wip[NAN_MASK] = np.nan

        # MCT requires 2D
        _X_wip = _X_wip.reshape((-1, 1))

        # with ignore_nan = False, what is left behind should be null of nan mask
        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['ignore_nan'] = False
        out = MCT(**_new_kwargs).fit_transform(_X_wip)

        assert np.array_equal(out, _X_wip[np.logical_not(NAN_MASK)])

        # with ignore_nan = True, nothing should be deleted
        _new_kwargs['ignore_nan'] = True
        out = MCT(**_new_kwargs).fit_transform(_X_wip)

        assert np.array_equal(out, _X_wip, equal_nan=True)

# END TEST ignore_nan WORKS ############################################


# TEST ignore_columns WORKS ############################################
@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestIgnoreColumnsWorks:

    def test_ignore_columns_works(self, NO_NAN_X, y_np, _kwargs, _mct_cols):

        # USE FLOAT AND STR COLUMNS
        _X_wip = NO_NAN_X[:, 2 * _mct_cols:].copy()

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['count_threshold'] *= 2
        _new_kwargs['ignore_float_columns'] = True

        # DEMONSTRATE THAT THIS THRESHOLD WILL ALTER X (AND y) -- -- --
        # MANY OR ALL STR ROWS SHOULD BE DELETED
        TestCls = MCT(**_new_kwargs)
        try:
            OUTPUT_X, OUTPUT_y = TestCls.fit_transform(_X_wip, y_np)
            raise UnicodeError
        except UnicodeError:
            # if not everything was deleted, look to see if anything was deleted
            err_msg = lambda i: (f"ignore_columns: {i} was not altered "
                                 f"when high threshold on str columns")
            assert not np.array_equiv(OUTPUT_X, _X_wip), err_msg('X')
            assert not np.array_equiv(OUTPUT_y, y_np), err_msg('y')
            del OUTPUT_X, OUTPUT_y, err_msg
            # if get to here this means that something was deleted, which is good
        except Exception as e:
            # this means that everything was deleted, which is good
            pass
        # END DEMONSTRATE THAT THIS THRESHOLD WILL ALTER X (AND y) -- --


        # SHOW THAT WHEN THE COLUMNS ARE IGNORED THAT X (AND y) ARE NOT ALTERED
        # ignore the string columns
        _new_kwargs['ignore_columns'] = np.arange(_mct_cols, _X_wip.shape[1])

        TestCls = MCT(**_new_kwargs)
        OUTPUT_X, OUTPUT_y = TestCls.fit_transform(_X_wip, y_np)
        err_msg = lambda i: (f"ignore_columns: {i} was altered when the only "
                             f"columns that could change were ignored")
        assert np.array_equiv(OUTPUT_X, _X_wip), err_msg('X')
        assert np.array_equiv(OUTPUT_y, y_np), err_msg('y')

# END TEST ignore_columns WORKS ########################################


# TEST handle_as_bool WORKS ############################################
@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestHandleAsBoolWorks:

    def test_handle_as_bool_works(
        self, X_np, NO_NAN_X, y_np, _kwargs, _mct_cols, x_rows, x_cols
    ):

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['ignore_non_binary_integer_columns'] = False

        _thresh = _new_kwargs['count_threshold']

        # USE NON_BINARY_INT COLUMNS
        _X_wip = NO_NAN_X[:, _mct_cols:2 * _mct_cols].copy()

        # RIG ONE OF THE COLUMNS WITH ENOUGH ZEROS THAT IT WOULD BE DELETED
        # WHEN HANDLED AS AN INT --- BECAUSE EACH INT WOULD BE < count_threshold,
        # DELETING THEM, LEAVING A COLUMN OF ALL ZEROS, WHICH WOULD THEN
        # BE DELETED
        RIGGED_INTEGERS = np.zeros(x_rows, dtype=np.uint32)
        for row_idx in range(1, _thresh + 2):
            RIGGED_INTEGERS[row_idx] = row_idx
        _X_wip[:, -1] = RIGGED_INTEGERS
        del RIGGED_INTEGERS

        # DEMONSTRATE THAT ONE CHOP WHEN NOT HANDLED AS BOOL WILL SHRINK
        # ROWS AND ALSO DELETE 1 COLUMN FROM X
        _new_kwargs['handle_as_bool'] = None
        TRFM_X = MCT(**_new_kwargs).fit_transform(_X_wip)
        assert TRFM_X.shape[1] == _X_wip.shape[1] - 1
        assert TRFM_X.shape[0] < _X_wip.shape[0]
        del TRFM_X

        # DEMONSTRATE THAT WHEN ZERO-PEPPERED COLUMN IS HANDLED AS A
        # BOOL, THE COLUMN IS RETAINED
        _new_kwargs['handle_as_bool'] = [_X_wip.shape[1] - 1]
        TRFM_X = MCT(**_new_kwargs).fit_transform(_X_wip)
        assert TRFM_X.shape == _X_wip.shape


    def test_hab_cannot_be_used_on_str(
        self, _kwargs, NAN_X, y_np, _mct_cols, x_cols
    ):

        # TEST handle_as_bool CANNOT BE USED ON STR ('obj') COLUMNS
        # STR COLUMNS SHOULD BE [:, 3*_mct_cols:] ON ORIGINAL X
        # PICK ONE COLUMN IS STR; ONE EACH FROM BIN-INT, INT, AND FLOAT
        MCT(**_kwargs).set_params(handle_as_bool=[_mct_cols - 1]).fit(NAN_X, y_np)
        MCT(**_kwargs).set_params(handle_as_bool=[2 * _mct_cols - 1]).fit(NAN_X, y_np)
        MCT(**_kwargs).set_params(handle_as_bool=[3 * _mct_cols - 1]).fit(NAN_X, y_np)
        with pytest.raises(ValueError):
            MCT(**_kwargs).set_params(handle_as_bool=[3 * _mct_cols]).fit(NAN_X, y_np)


        # DEMONSTRATE THAT AFTER fit() WITH VALID handle_as_bool, IF
        # handle_as_bool IS CHANGED TO INVALID, RAISES ValueError
        TestCls = MCT(**_kwargs)
        TestCls.set_params(handle_as_bool=[_mct_cols + 1])  # A NON-BINARY INT COLUMN
        TestCls.partial_fit(NAN_X)
        TestCls.set_params(handle_as_bool=[x_cols - 1])  # STR COLUMN
        with pytest.raises(ValueError):
            TestCls.partial_fit(NAN_X)

        with pytest.raises(ValueError):
            TestCls.transform(NAN_X)
# END TEST handle_as_bool WORKS ########################################


# TEST delete_axis_0 WORKS #############################################
@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestDeleteAxis0Works:


    def test_delete_axis_0_works(
        self, NO_NAN_X, y_np, COLUMNS, _kwargs, _mct_cols
    ):

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['count_threshold'] *= 2

        # 1) USE FLOAT AND STR COLUMNS ONLY, ignore_float_columns=True
        # 2A) RUN MCT WHEN STRS ARE NOT DUMMIED, THE FLOAT COLUMN OUTPUT
        #   IS SUPPOSED TO BE THE "TRUTH" FOR FLOAT COLUMNS WHEN DUMMIED
        #   AND delete_axis_0 = True
        # 2B) Ensure some rows were actually deleted (BUT NOT ALL) by
        #   comparing NO_DUMMY_BASELINE_FLOAT_DF against ORIGINAL
        #   UN-TRANSFORMED FLOAT_DF
        # 3A) BUILD THE DUMMIED EQUIVALENT OF THE FLOAT AND STR COLUMN DF
        # 3B) PROVE NO ROWS ARE DELETED FROM DUMMIED WHEN delete_axis_0
        #   is False
        # 3C) RUN delete_axis_0 True ON DUMMIED, COMPARE THE FLT COLUMNS
        #   AGAINST "TRUTH" TO SEE IF THE RESULTS ARE EQUAL

        # 1) USE FLOAT AND STR COLUMNS ONLY * * * * * * * * * * * * * *
        FLOAT_STR_DF = pd.DataFrame(
            data=NO_NAN_X[:, 2 * _mct_cols:4 * _mct_cols].copy(),
            columns=COLUMNS[2 * _mct_cols:4 * _mct_cols].copy()
        )

        FLOAT_DF = pd.DataFrame(
            data=NO_NAN_X[:, 2 * _mct_cols:3 * _mct_cols].copy(),
            columns=COLUMNS[2 * _mct_cols:3 * _mct_cols].copy()
        )  # "TRUTH" for when delete_axis_0 = False

        # KEEP STR_DF TO DO OneHot
        STR_DF = pd.DataFrame(
            data=NO_NAN_X[:, 3 * _mct_cols:4 * _mct_cols].copy(),
            columns=COLUMNS[3 * _mct_cols:4 * _mct_cols].copy()
        )
        # END 1) USE FLOAT AND STR COLUMNS ONLY * * * * * * * * * * * *

        # 2A) RUN MCT WHEN STRS ARE NOT DUMMIED, THE FLOAT COLUMN OUTPUT
        #   IS SUPPOSED TO BE THE "TRUTH" FOR FLOAT COLUMNS WHEN DUMMIED
        #   AND delete_axis_0 = True
        ChopStrTestCls = MCT(**_new_kwargs)
        # DOESNT MATTER WHAT delete_axis_0 IS SET TO, THERE ARE NO BOOL COLUMNS
        ChopStrTestCls.set_params(ignore_float_columns=True)
        STR_FLT_NO_DUMMY_BASELINE = ChopStrTestCls.fit_transform(FLOAT_STR_DF)

        STR_FLT_NO_DUMMY_BASELINE_DF = pd.DataFrame(
            data=STR_FLT_NO_DUMMY_BASELINE,
            columns=ChopStrTestCls.get_feature_names_out(None)
        )
        del ChopStrTestCls, STR_FLT_NO_DUMMY_BASELINE, FLOAT_STR_DF

        NO_DUMMY_BASELINE_FLOAT_DF = \
            STR_FLT_NO_DUMMY_BASELINE_DF.iloc[:, :_mct_cols]
        del STR_FLT_NO_DUMMY_BASELINE_DF
        # END 2A * * * * * * * * * * * * * * * * * * * * * * * * * * * *

        # 2B) Ensure some rows were actually deleted (but not all) by
        #   comparing NO_DUMMY_BASELINE_FLOAT_DF against ORIGINAL
        #   UN-TRANSFORMED FLOAT_DF
        assert not NO_DUMMY_BASELINE_FLOAT_DF.equals(FLOAT_DF), \
            f"MinCountTransform of FLOAT_STR_DF did not delete any rows"
        assert NO_DUMMY_BASELINE_FLOAT_DF.shape[0] > 0, \
            f"ALL ROWS WERE DELETED WHEN DURING BASELINE NO DUMMY TRANSFORM"
        # END 2B * * * * * * * * * * * * * * * * * * * * * * * * * * * *

        # 3A) BUILD THE DUMMIED EQUIVALENT OF THE FLOAT AND STR COLUMN DF
        onehot = OneHotEncoder(
            categories='auto',
            drop=None,
            dtype=np.uint8,
            handle_unknown='error',
            min_frequency=None,
            max_categories=None
        )

        expanded = onehot.fit_transform(STR_DF)

        # need to accommodate sklearn revs where OHE does/doesnt have sparse_output
        if hasattr(expanded, 'toarray'):
            expanded = expanded.toarray()

        DUMMIED_STR_DF = pd.DataFrame(
            data=expanded,
            columns=onehot.get_feature_names_out()
        )
        FULL_DUMMIED_STR_FLOAT_DF = pd.concat((FLOAT_DF, DUMMIED_STR_DF), axis=1)
        del onehot, expanded, STR_DF, DUMMIED_STR_DF
        # END 3A * * * * * * * * * * * * * * * * * * * * * * * * * * * *

        # 3B) PROVE NO ROWS ARE DELETED FROM DUMMIED WHEN delete_axis_0 is False
        DummyDontDeleteAxis0TestCls = MCT(**_new_kwargs)
        DummyDontDeleteAxis0TestCls.set_params(
            delete_axis_0=False, ignore_float_columns=True
        )
        DUMMIED_FLT_STR_DONT_DELETE_AXIS_0 = \
            DummyDontDeleteAxis0TestCls.fit_transform(FULL_DUMMIED_STR_FLOAT_DF)

        DUMMIED_FLT_STR_DONT_DELETE_AXIS_0_DF = pd.DataFrame(
            data=DUMMIED_FLT_STR_DONT_DELETE_AXIS_0,
            columns=DummyDontDeleteAxis0TestCls.get_feature_names_out(None)
        )
        del DummyDontDeleteAxis0TestCls, DUMMIED_FLT_STR_DONT_DELETE_AXIS_0

        DUMMIED_FLT_DONT_DELETE_AXIS_0_DF = \
            DUMMIED_FLT_STR_DONT_DELETE_AXIS_0_DF.iloc[:, :_mct_cols]
        del DUMMIED_FLT_STR_DONT_DELETE_AXIS_0_DF

        # Compare DUMMIED_FLT_DONT_DELETE_AXIS_0_DF against FLOAT_DF
        assert DUMMIED_FLT_DONT_DELETE_AXIS_0_DF.equals(FLOAT_DF), \
            (f"floats with dummies and delete_axis_0=False do not "
             f"equal original untransformed floats (rows were deleted)")

        del DUMMIED_FLT_DONT_DELETE_AXIS_0_DF
        # END 3B * * * * * * * * * * * * * * * * * * * * * * * * * * * *


        # 3C) RUN delete_axis_0 True ON DUMMIED STRINGS, COMPARE THE FLT
        #   COLUMNS AGAINST NON-DUMMIED STRINGS TO SEE IF THE RESULTS
        #   ARE EQUAL
        DummyDeleteAxis0TestCls = MCT(**_new_kwargs)
        DummyDeleteAxis0TestCls.set_params(
            delete_axis_0=True, ignore_float_columns=True
        )
        DUMMIED_FLT_STR_DELETE_0_X = \
            DummyDeleteAxis0TestCls.fit_transform(FULL_DUMMIED_STR_FLOAT_DF)

        DUMMIED_FLT_STR_DELETE_0_X_DF = pd.DataFrame(
            data=DUMMIED_FLT_STR_DELETE_0_X,
            columns=DummyDeleteAxis0TestCls.get_feature_names_out(None)
        )
        del DummyDeleteAxis0TestCls

        # Compare DUM_MIN_COUNTED_DELETE_0_FLOAT_DF against
        # NO_DUMMY_BASELINE_FLOAT_DF
        DUMMIED_FLT_DELETE_0_X_DF = \
            DUMMIED_FLT_STR_DELETE_0_X_DF.iloc[:, :_mct_cols]
        del DUMMIED_FLT_STR_DELETE_0_X_DF

        assert DUMMIED_FLT_DELETE_0_X_DF.equals(NO_DUMMY_BASELINE_FLOAT_DF), \
            (f"floats with dummies and delete_axis_0=True do not "
             f"equal no-dummy baseline floats")

        del DUMMIED_FLT_DELETE_0_X_DF
        # END 3C * * * * * * * * * * * * * * * * * * * * * * * * * * * *

        del FLOAT_DF, FULL_DUMMIED_STR_FLOAT_DF, NO_DUMMY_BASELINE_FLOAT_DF

# END TEST delete_axis_0 WORKS #########################################


@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestCountThresholdFormat:

    def test_ct_thresh_accuracy(self, _kwargs, NO_NAN_X, y_np):

        # prove that threshold passed as int and same thresholds passed
        # as list give identical output

        _new_kwargs = deepcopy(_kwargs)

        _MCT = MCT(**_new_kwargs)

        # as int -- -- -- -- -- -- -- -- -- -- -- --
        _MCT = MCT(**_new_kwargs)
        INT_TRFM_X, INT_TRFM_Y = _MCT.fit_transform (NO_NAN_X, y_np)
        # END as int -- -- -- -- -- -- -- -- -- -- --

        # as list -- -- -- -- -- -- -- -- -- -- -- --
        _new_kwargs['count_threshold'] = \
            [_new_kwargs['count_threshold'] for _ in range(NO_NAN_X.shape[1])]
        _MCT = MCT(**_new_kwargs)
        LIST_TRFM_X, LIST_TRFM_Y = _MCT.fit_transform(NO_NAN_X, y_np)
        # END as list -- -- -- -- -- -- -- -- -- -- --

        assert np.array_equal(INT_TRFM_X, LIST_TRFM_X)
        assert np.array_equal(INT_TRFM_Y, LIST_TRFM_Y)

# END TEST PARAM ACCURACY ** * ** * ** * ** * ** * ** * ** * ** * ** *
# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
# TEST MISCELLANEOUS ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

# TEST CORRECT DTYPES ARE RETRIEVED W/ OR W/O np.nan MIXED IN ##########
@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestAssignedDtypesWithAndWithoutNansMixedIn:

    def test_no_nan(self, _kwargs, DTYPE_KEY, NO_NAN_X, y_np):
        # PASS NON-np.nan DATA AND COMPARE TO DTYPE_KEY
        TestCls = MCT(**_kwargs)
        TestCls.fit(NO_NAN_X, y_np)
        assert np.array_equiv(TestCls.original_dtypes_, DTYPE_KEY)

        del TestCls

    def test_with_nan(self, _kwargs, DTYPE_KEY, NAN_X, y_np):
        TestCls = MCT(**_kwargs)
        TestCls.fit(NAN_X, y_np)
        assert np.array_equiv(TestCls.original_dtypes_, DTYPE_KEY)

        del TestCls

# END TEST CORRECT DTYPES ARE RETRIEVED W/ OR W/O np.nan MIXED IN ######

# TEST CONDITIONAL ACCESS TO RECURSION #################################
# 1) access to partial_fit, fit or transform when max_recursions > 1 is blocked
# 2) access fit & transform when max_recursions > 1 can only be through fit_transform
# 3) access to partial_fit, fit or transform when max_recursions == 1 is not blocked
@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestConditionalAccessToRecursion:

    def test_conditional_access_to_recursion(self, X_np, y_np, _kwargs):

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['max_recursions'] = 3

        TEST_X = X_np.copy()
        TEST_Y = y_np.copy()

        TestCls = MCT(**_new_kwargs)

        # 1) partial_fit/fit/transform blocked with max_recursions >= 2
        with pytest.raises(ValueError):
            MCT(**_new_kwargs).partial_fit(TEST_X, TEST_Y)

        with pytest.raises(ValueError):
            MCT(**_new_kwargs).fit(TEST_X, TEST_Y)

        with pytest.raises(ValueError):
            MCT(**_new_kwargs).transform(TEST_X, TEST_Y)

        # 2) ad libido access to fit_transform
        for _ in range(5):
            TestCls.fit_transform(TEST_X, TEST_Y)

        # 3) max_recursions==1 ad libido access to partial_fit/fit/transform
        _new_kwargs['max_recursions'] = 1
        TestCls = MCT(**_new_kwargs)
        for _name, cls_method in zip(
            ['fit', 'partial_fit', 'transform'],
            [TestCls.fit, TestCls.partial_fit, TestCls.transform]
        ):
            cls_method(TEST_X, TEST_Y)

        del TEST_X, TEST_Y, TestCls, _name, cls_method, _

# END TEST CONDITIONAL ACCESS TO RECURSION #############################


# END TEST MISCELLANEOUS ** * ** * ** * ** * ** * ** * ** * ** * ** * **
# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestX:

    # - accepts ndarray, pd.DataFrame, pl.DataFrame, and all ss
    # - cannot be None
    # - must be 2D
    # - must have at least 1 column
    # - must have at least 3 samples
    # - allows nan
    # - partial_fit/transform num columns must equal num columns seen during first fit


    # CONTAINERS #######################################################
    @pytest.mark.parametrize('_junk_X',
        (-1, 0, 1, 3.14, None, 'junk', [0, 1], (1,), {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_X(self, _kwargs, X_np, _junk_X):

        TestCls = MCT(**_kwargs)

        # these are caught by base.validate_data.
        with pytest.raises(ValueError):
            TestCls.partial_fit(_junk_X)

        with pytest.raises(ValueError):
            TestCls.fit(_junk_X)

        with pytest.raises(ValueError):
            TestCls.fit_transform(_junk_X)

        TestCls.fit(X_np)

        with pytest.raises(ValueError) as e:
            TestCls.transform(_junk_X)
        assert not isinstance(e.value, NotFittedError)


    @pytest.mark.parametrize('_format', ('py_list', 'py_tuple'))
    def test_rejects_invalid_container(self, X_np, _columns, _kwargs, _format):

        assert _format in ('py_list', 'py_tuple')

        TestCls = MCT(**_kwargs)

        if _format == 'py_list':
            _X_wip = list(map(list, X_np))
        elif _format == 'py_tuple':
            _X_wip = tuple(map(tuple, X_np))

        with pytest.raises(ValueError):
            TestCls.partial_fit(_X_wip)

        with pytest.raises(ValueError):
            TestCls.fit(_X_wip)

        with pytest.raises(ValueError):
            TestCls.fit_transform(_X_wip)

        TestCls.fit(X_np) # fit on numpy, not the converted data

        with pytest.raises(ValueError) as e:
            TestCls.transform(_X_wip)
        assert not isinstance(e.value, NotFittedError)


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csc_array'))
    def test_good_X_container(
        self, _X_factory, _columns, _shape, _kwargs, _format
    ):

        _X_wip = _X_factory(
            _dupl=None, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns, _constants=None, _noise=0, _zeros=None,
            _shape=_shape
        )


        _MCT = MCT(**_kwargs)

        _MCT.partial_fit(_X_wip)

        _MCT.fit(_X_wip)

        _MCT.fit_transform(_X_wip)

        _MCT.transform(_X_wip)

    # END CONTAINERS ###################################################


    # SHAPE ############################################################
    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl'))
    def test_rejects_1D(self, X_np, _kwargs, _format):

        # validation order is
        # 1) check_fitted (for transform)
        # 2) base.validate_data, which catches dim & min columns
        # 3) _check_n_features in transform
        # so for the fits & transform, 1D will always catch first

        _MCT = MCT(**_kwargs)

        if _format == 'np':
            _X_wip = X_np[:, 0]
        elif _format == 'pd':
            _X_wip = pd.Series(X_np[:, 0])
        elif _format == 'pl':
            _X_wip = pl.Series(X_np[:, 0])
        else:
            raise Exception

        with pytest.raises(ValueError):
            _MCT.partial_fit(_X_wip)

        with pytest.raises(ValueError):
            _MCT.fit(_X_wip)

        with pytest.raises(ValueError):
            _MCT.fit_transform(_X_wip)

        _MCT.fit(X_np)

        with pytest.raises(ValueError) as e:
            _MCT.transform(_X_wip)
        assert not isinstance(e.value, NotFittedError)


    @pytest.mark.parametrize('_num_cols', (0, 1, 2))
    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csc_array'))
    def test_X_2D_number_of_columns(
        self, X_np, _kwargs, _columns, _format, _num_cols
    ):

        # validation order is
        # 1) check_fitted (for transform)
        # 2) base.validate_data, which catches dim & min columns
        # 3) _check_n_features in transform
        # so for the fits & transform, validate_data will catch
        # for all methods the min number of columns is 1

        _base_X = X_np[:, :_num_cols]
        if _format == 'np':
            _X_wip = _base_X
        elif _format == 'pd':
            _X_wip = pd.DataFrame(_base_X, columns=_columns[:_num_cols])
        elif _format == 'pl':
            _X_wip = pl.from_numpy(_base_X, schema=list(_columns[:_num_cols]))
        elif _format == 'csc_array':
            _X_wip = ss.csc_array(_base_X)
        else:
            raise Exception

        assert len(_X_wip.shape) == 2
        assert _X_wip.shape[1] == _num_cols

        _MCT = MCT(**_kwargs)

        if _num_cols == 0:
            with pytest.raises(ValueError):
                _MCT.partial_fit(_X_wip)
            with pytest.raises(ValueError):
                _MCT.fit(_X_wip)
            with pytest.raises(ValueError):
                _MCT.fit_transform(_X_wip)
            _MCT.fit(X_np)
            with pytest.raises(ValueError) as e:
                _MCT.transform(_X_wip)
            assert not isinstance(e.value, NotFittedError)
        else:
            _MCT.partial_fit(_X_wip)
            _MCT.fit(_X_wip)
            _MCT.fit_transform(_X_wip)
            _MCT.transform(_X_wip)


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'dok_array'))
    def test_rejects_no_samples(self, _shape, _kwargs, X_np, _format):

        _MCT = MCT(**_kwargs)

        _X_base = np.empty((0, _shape[1]), dtype=np.float64)

        if _format == 'np':
            _X_wip = _X_base
        elif _format == 'pd':
            _X_wip = pd.DataFrame(_X_base)
        elif _format == 'pl':
            _X_wip = pl.from_numpy(_X_base)
        elif _format == 'dok_array':
            _X_wip = ss.dok_array(_X_base)
        else:
            raise Exception


        with pytest.raises(ValueError):
            _MCT.partial_fit(_X_base)

        with pytest.raises(ValueError):
            _MCT.fit(_X_base)

        with pytest.raises(ValueError):
            _MCT.fit_transform(_X_base)

        _MCT.fit(X_np)

        with pytest.raises(ValueError) as e:
            _MCT.transform(_X_wip)
        assert not isinstance(e.value, NotFittedError)


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csr_matrix'))
    @pytest.mark.parametrize('_diff', ('more', 'less', 'same'))
    def test_rejects_bad_num_features(
        self, _X_factory, _shape, _kwargs, _columns, X_np, _format, _diff
    ):
        # ** ** ** **
        # THERE CANNOT BE "BAD NUM FEATURES" FOR fit & fit_transform
        # partial_fit & transform is handled by _check_n_features
        # ** ** ** **

        # SHOULD RAISE ValueError WHEN COLUMNS DO NOT EQUAL NUMBER OF
        # COLUMNS SEEN ON FIRST FIT

        _new_shape_dict = {
            'same': _shape,
            'less': (_shape[0], _shape[1] - 1),
            'more': (_shape[0], 2 * _shape[1])
        }
        _columns_dict = {
            'same': _columns,
            'less': _columns[:-1],
            'more': np.hstack((_columns, np.char.upper(_columns)))
        }

        _X_wip = _X_factory(
            _dupl=None, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns_dict[_diff],
            _constants=None, _zeros=0,
            _shape=_new_shape_dict[_diff]
        )

        _MCT = MCT(**_kwargs).fit(X_np)

        if _diff == 'same':
            _MCT.partial_fit(_X_wip)
            _MCT.transform(_X_wip)
        else:
            with pytest.raises(ValueError) as e:
                _MCT.partial_fit(_X_wip)
            assert not isinstance(e.value, NotFittedError)
            with pytest.raises(ValueError) as e:
                _MCT.transform(_X_wip)
            assert not isinstance(e.value, NotFittedError)

    # END SHAPE ########################################################


    @pytest.mark.parametrize('_format', ('pd', 'pl'))
    @pytest.mark.parametrize('fst_fit_columns', ('DF1', 'DF2', 'NO_HDR_DF'))
    @pytest.mark.parametrize('scd_fit_columns', ('DF1', 'DF2', 'NO_HDR_DF'))
    @pytest.mark.parametrize('trfm_columns', ('DF1', 'DF2', 'NO_HDR_DF'))
    def test_except_or_warn_on_different_headers(
        self, _X_factory, _kwargs, _columns, _shape, _format,
        fst_fit_columns, scd_fit_columns, trfm_columns
    ):

        # TEST ValueError WHEN SEES A DF HEADER DIFFERENT FROM FIRST-SEEN HEADER

        _factory_kwargs = {
            '_dupl':None, '_format':_format, '_dtype':'flt',
            '_has_nan':False, '_constants': None, '_shape':_shape
        }

        # np.flip(_columns) is bad columns
        _col_dict = {'DF1': _columns, 'DF2': np.flip(_columns), 'NO_HDR_DF': None}

        fst_fit_X = _X_factory(_columns=_col_dict[fst_fit_columns], **_factory_kwargs)
        scd_fit_X = _X_factory(_columns=_col_dict[scd_fit_columns], **_factory_kwargs)
        trfm_X = _X_factory(_columns=_col_dict[trfm_columns], **_factory_kwargs)

        TestCls = MCT(**_kwargs)

        _objs = [fst_fit_columns, scd_fit_columns, trfm_columns]
        # EXCEPT IF 2 DIFFERENT HEADERS ARE SEEN
        pybear_exception = 0
        pybear_exception += bool('DF1' in _objs and 'DF2' in _objs)
        # POLARS ALWAYS HAS A HEADER
        if _format == 'pl':
            pybear_exception += (len(np.unique(_objs)) > 1)
        # IF FIRST FIT WAS WITH PD NO HEADER, THEN ANYTHING GETS THRU ON
        # SUBSEQUENT partial_fits AND transform
        if _format == 'pd':
            pybear_exception -= bool(fst_fit_columns == 'NO_HDR_DF')
        pybear_exception = max(0, pybear_exception)

        # WARN IF HAS-HEADER AND PD NOT-HEADER BOTH PASSED DURING fits/transform
        # POLARS SHOULDNT GET IN HERE, WILL ALWAYS EXCEPT, ALWAYS HAS A HEADER
        pybear_warn = 0
        if not pybear_exception:
            pybear_warn += ('NO_HDR_DF' in _objs)
            # IF NONE OF THEM HAD A HEADER, THEN NO WARNING
            pybear_warn -= ('DF1' not in _objs and 'DF2' not in _objs)
            pybear_warn = max(0, pybear_warn)

        del _objs

        if pybear_exception:
            # this raises in _check_feature_names
            TestCls.partial_fit(fst_fit_X)
            with pytest.raises(ValueError) as e:
                TestCls.partial_fit(scd_fit_X)
                TestCls.transform(trfm_X)
            assert not isinstance(e.value, NotFittedError)
        elif pybear_warn:
            TestCls.partial_fit(fst_fit_X)
            with pytest.warns():
                TestCls.partial_fit(scd_fit_X)
                TestCls.transform(trfm_X)
        else:
            # SHOULD NOT EXCEPT OR WARN
            TestCls.partial_fit(fst_fit_X)
            TestCls.partial_fit(scd_fit_X)
            TestCls.transform(trfm_X)


@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestPartialFit:


    @pytest.mark.parametrize('_y',
        (-1,0,1, np.pi, True, False, None, 'trash', [1,2], {1,2}, {'a':1},
        lambda x: x, min)
    )
    def test_fit_partial_fit_accept_Y_equals_anything(self, _kwargs, X_np, _y):
        MCT(**_kwargs).partial_fit(X_np, _y)
        MCT(**_kwargs).fit(X_np, _y)


    def test_conditional_access_to_partial_fit_and_fit(self, X_np, y_np, _kwargs):

        TestCls = MCT(**_kwargs)

        # 1) partial_fit() should allow unlimited number of subsequent partial_fits()
        for _ in range(5):
            TestCls.partial_fit(X_np, y_np)

        TestCls.reset()

        # 2) one call to fit() should allow subsequent attempts to partial_fit()
        TestCls.fit(X_np, y_np)
        TestCls.partial_fit(X_np, y_np)

        TestCls.reset()

        # 3) one call to fit() should allow later attempts to fit() (2nd fit will reset)
        TestCls.fit(X_np, y_np)
        TestCls.fit(X_np, y_np)

        TestCls.reset()

        # 4) a call to fit() after a previous partial_fit() should be allowed
        TestCls.partial_fit(X_np, y_np)
        TestCls.fit(X_np, y_np)

        TestCls.reset()

        # 5) fit_transform() should allow calls ad libido
        for _ in range(5):
            TestCls.fit_transform(X_np, y_np)


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'coo_matrix'))
    def test_X_is_not_mutated(
        self, _X_factory, _columns, _shape, _kwargs, _format
    ):

        _X_wip = _X_factory(
            _dupl=None, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns, _constants=None, _noise=0, _zeros=None,
            _shape=_shape
        )

        if _format == 'np':
            assert _X_wip.flags['C_CONTIGUOUS'] is True

        try:
            _X_wip_before = _X_wip.copy()
        except:
            _X_wip_before = _X_wip.clone()


        # verify _X_wip does not mutate in partial_fit()
        _MCT = MCT(**_kwargs).partial_fit(_X_wip)


        # ASSERTIONS v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        assert isinstance(_X_wip, type(_X_wip_before))
        assert _X_wip.shape == _X_wip_before.shape

        if isinstance(_X_wip, np.ndarray):
            # if numpy output, is C order
            assert _X_wip.flags['C_CONTIGUOUS'] is True
            assert np.array_equal(_X_wip_before, _X_wip)
            assert _X_wip.dtype == _X_wip_before.dtype
        elif hasattr(_X_wip, 'columns'):  # DATAFRAMES
            assert _X_wip.equals(_X_wip_before)
            assert np.array_equal(_X_wip.dtypes, _X_wip_before.dtypes)
        elif hasattr(_X_wip_before, 'toarray'):
            assert np.array_equal(_X_wip.toarray(), _X_wip_before.toarray())
            assert _X_wip.dtype == _X_wip_before.dtype
        else:
            raise Exception


    def test_many_partial_fits_equal_one_big_fit(
        self, X_np, y_np, _kwargs, x_rows
    ):

        # ** ** ** ** ** ** ** ** ** ** **
        # TEST THAT ONE-SHOT partial_fit() / transform() == ONE-SHOT fit() / transform()
        OneShotPartialFitTestCls = MCT(**_kwargs).partial_fit(X_np, y_np)

        OneShotFullFitTestCls = MCT(**_kwargs).fit(X_np, y_np)

        # make a 2D y
        y_np = np.vstack((y_np, np.flip(y_np))).transpose()

        # original_dtypes are equal -- -- -- --
        assert np.array_equal(
            OneShotPartialFitTestCls.original_dtypes_,
            OneShotFullFitTestCls.original_dtypes_
        )
        # END original_dtypes are equal -- -- -- --

        ONE_SHOT_PARTIAL_FIT_TRFM_X, ONE_SHOT_PARTIAL_FIT_TRFM_Y = \
            OneShotPartialFitTestCls.transform(X_np, y_np)

        ONE_SHOT_FULL_FIT_TRFM_X, ONE_SHOT_FULL_FIT_TRFM_Y = \
            OneShotFullFitTestCls.transform(X_np, y_np)

        assert np.array_equiv(
            ONE_SHOT_PARTIAL_FIT_TRFM_X.astype(str),
            ONE_SHOT_FULL_FIT_TRFM_X.astype(str)
        ), f"one shot partial fit trfm X != one shot full fit trfm X"

        assert np.array_equiv(
            ONE_SHOT_PARTIAL_FIT_TRFM_Y,
            ONE_SHOT_FULL_FIT_TRFM_Y
        ), f"one shot partial fit trfm Y != one shot full fit trfm Y"

        del OneShotPartialFitTestCls, OneShotFullFitTestCls
        del ONE_SHOT_PARTIAL_FIT_TRFM_X, ONE_SHOT_FULL_FIT_TRFM_X
        del ONE_SHOT_PARTIAL_FIT_TRFM_Y, ONE_SHOT_FULL_FIT_TRFM_Y

        # END TEST THAT ONE-SHOT partial_fit/transform==ONE-SHOT fit/transform
        # ** ** ** ** ** ** ** ** ** ** **

        # ** ** ** ** ** ** ** ** ** ** **
        # TEST PARTIAL FIT COUNTS ARE DOUBLED WHEN FULL DATA IS partial_fit() 2X
        SingleFitTestClass = MCT(**_kwargs).fit(X_np, y_np)
        CT1 = SingleFitTestClass.total_counts_by_column_

        DoublePartialFitTestClass = MCT(**_kwargs)
        DoublePartialFitTestClass.partial_fit(X_np, y_np)

        DoublePartialFitTestClass.partial_fit(X_np, y_np)
        CT2 = DoublePartialFitTestClass.total_counts_by_column_

        assert np.array_equal(list(CT1.keys()), list(CT2.keys()))

        # convert keys to strs to deal with nans
        CT1 = {i: {str(k): v for k, v in _.items()} for i, _ in CT1.items()}
        CT2 = {i: {str(k): v for k, v in _.items()} for i, _ in CT2.items()}
        for _c_idx in CT1:
            for _unq in CT1[_c_idx]:
                assert CT2[_c_idx][_unq] == 2 * CT1[_c_idx][_unq]
        del CT1, CT2

        # END TEST PARTIAL FIT COUNTS ARE DOUBLED WHEN FULL DATA IS partial_fit() 2X
        # ** ** ** ** ** ** ** ** ** ** **

        # ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
        # ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
        # TEST MANY PARTIAL FITS == ONE BIG FIT

        # STORE CHUNKS TO ENSURE THEY STACK BACK TO THE ORIGINAL X/y
        _chunks = 5
        X_CHUNK_HOLDER = []
        Y_CHUNK_HOLDER = []
        for row_chunk in range(_chunks):
            _mask_start = row_chunk * x_rows // _chunks
            _mask_end = (row_chunk + 1) * x_rows // _chunks
            X_CHUNK_HOLDER.append(X_np[_mask_start:_mask_end, :])
            Y_CHUNK_HOLDER.append(y_np[_mask_start:_mask_end, :])
        del _mask_start, _mask_end

        assert np.array_equiv(
            np.vstack(X_CHUNK_HOLDER).astype(str), X_np.astype(str)
        ), f"agglomerated X chunks != original X"
        assert np.array_equiv(np.vstack(Y_CHUNK_HOLDER), y_np), \
            f"agglomerated Y chunks != original Y"

        PartialFitPartialTrfmTestCls = MCT(**_kwargs)
        PartialFitOneShotTrfmTestCls = MCT(**_kwargs)
        OneShotFitTransformTestCls = MCT(**_kwargs)

        # PIECEMEAL PARTIAL FIT ****************************************
        for X_CHUNK, Y_CHUNK in zip(X_CHUNK_HOLDER, Y_CHUNK_HOLDER):
            PartialFitPartialTrfmTestCls.partial_fit(X_CHUNK, Y_CHUNK)
            PartialFitOneShotTrfmTestCls.partial_fit(X_CHUNK, Y_CHUNK)

        # PIECEMEAL TRANSFORM ******************************************
        # THIS CANT BE UNDER THE partial_fit LOOP, ALL FITS MUST BE DONE
        # BEFORE DOING ANY TRFMS
        PARTIAL_TRFM_X_HOLDER = []
        PARTIAL_TRFM_Y_HOLDER = []
        for X_CHUNK, Y_CHUNK in zip(X_CHUNK_HOLDER, Y_CHUNK_HOLDER):
            PARTIAL_TRFM_X, PARTIAL_TRFM_Y = \
                PartialFitPartialTrfmTestCls.transform(X_CHUNK, Y_CHUNK)
            PARTIAL_TRFM_X_HOLDER.append(PARTIAL_TRFM_X)
            PARTIAL_TRFM_Y_HOLDER.append(PARTIAL_TRFM_Y)

        # AGGLOMERATE PARTIAL TRFMS FROM PARTIAL FIT
        FULL_TRFM_X_FROM_PARTIAL_FIT_PARTIAL_TRFM = \
            np.vstack(PARTIAL_TRFM_X_HOLDER)
        FULL_TRFM_Y_FROM_PARTIAL_FIT_PARTIAL_TRFM = \
            np.vstack(PARTIAL_TRFM_Y_HOLDER)

        del PartialFitPartialTrfmTestCls, PARTIAL_TRFM_X, PARTIAL_TRFM_Y
        # END PIECEMEAL TRANSFORM **************************************

        # DO ONE-SHOT TRANSFORM OF X,y ON THE PARTIALLY FIT INSTANCE
        out = PartialFitOneShotTrfmTestCls.transform(X_np, y_np)
        FULL_TRFM_X_FROM_PARTIAL_FIT_ONESHOT_TRFM = out[0]
        FULL_TRFM_Y_FROM_PARTIAL_FIT_ONESHOT_TRFM = out[1]

        del out,  PartialFitOneShotTrfmTestCls


        # ONE-SHOT FIT TRANSFORM
        FULL_TRFM_X_ONE_SHOT_FIT_TRANSFORM, FULL_TRFM_Y_ONE_SHOT_FIT_TRANSFORM = \
            OneShotFitTransformTestCls.fit_transform(X_np, y_np)

        del OneShotFitTransformTestCls

        # ASSERT ALL AGGLOMERATED X AND Y TRFMS ARE EQUAL
        assert np.array_equiv(
            FULL_TRFM_X_ONE_SHOT_FIT_TRANSFORM.astype(str),
            FULL_TRFM_X_FROM_PARTIAL_FIT_PARTIAL_TRFM.astype(str)
        ), f"trfm X from partial fit / partial trfm != one-shot fit/trfm X"

        assert np.array_equiv(
            FULL_TRFM_Y_ONE_SHOT_FIT_TRANSFORM,
            FULL_TRFM_Y_FROM_PARTIAL_FIT_PARTIAL_TRFM
        ), f"compiled trfm y from partial fit / partial trfm != one-shot fit/trfm y"

        assert np.array_equiv(
            FULL_TRFM_X_ONE_SHOT_FIT_TRANSFORM.astype(str),
            FULL_TRFM_X_FROM_PARTIAL_FIT_ONESHOT_TRFM.astype(str)
        ), f"trfm X from partial fits / one-shot trfm != one-shot fit/trfm X"

        assert np.array_equiv(
            FULL_TRFM_Y_ONE_SHOT_FIT_TRANSFORM,
            FULL_TRFM_Y_FROM_PARTIAL_FIT_ONESHOT_TRFM
        ), f"trfm y from partial fits / one-shot trfm != one-shot fit/trfm y"

        # TEST MANY PARTIAL FITS == ONE BIG FIT
        # ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


    def test_later_partial_fits_accept_new_uniques(
        self, NO_NAN_X, y_np, _kwargs, _mct_cols
    ):

        X1 = NO_NAN_X[:, _mct_cols:(2 * _mct_cols)].copy()  # non-bin-int columns
        X1 = X1.astype(np.float64).astype(np.int32)
        y1 = np.vstack((np.flip(y_np), y_np)).transpose()
        # 10X THE VALUES IN THE COPY OF DATA TO INTRODUCE NEW UNIQUE VALUES
        X2 = (10 * X1.astype(np.float64)).astype(np.int32)
        y2 = np.vstack((y_np, np.flip(y_np))).transpose()

        STACKED_X = np.vstack((X1, X2)).astype(np.float64).astype(np.int32)
        STACKED_Y = np.vstack((y1, y2)).astype(np.uint8)

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['count_threshold'] *= 3
        _new_kwargs['ignore_non_binary_integer_columns'] = False

        # 2 PARTIAL FITS - - -  - - - - - - - - - - - - - - - - - - - -
        PartialFitTestCls = MCT(**_new_kwargs)

        PartialFitTestCls.partial_fit(X1, y1)
        PartialFitTestCls.partial_fit(X2, y2)
        PARTIAL_FIT_X, PARTIAL_FIT_Y = \
            PartialFitTestCls.transform(STACKED_X, STACKED_Y)

        assert not PARTIAL_FIT_X.shape[0] == 0, \
            f'transform for 2 partial fits deleted all rows'

        # VERIFY SOME ROWS WERE ACTUALLY DELETED
        assert not np.array_equiv(PARTIAL_FIT_X, STACKED_X), \
            (f'later partial fits accept new uniques --- '
             f'transform did not delete any rows')
        # END 2 PARTIAL FITS - - -  - - - - - - - - - - - - - - - - - -

        # 1 BIG FIT - - -  - - - - - - - - - - - - - - - - - - - - - - -
        SingleFitTestCls = MCT(**_new_kwargs)
        SingleFitTestCls.fit(STACKED_X, STACKED_Y)
        SINGLE_FIT_X, SINGLE_FIT_Y = \
            SingleFitTestCls.transform(STACKED_X, STACKED_Y)

        assert not SINGLE_FIT_X.shape[0] == 0, \
            f'transform for one big fit deleted all rows'
        # END 1 BIG FIT - - -  - - - - - - - - - - - - - - - - - - - - -

        # compare 2 partial fits to 1 big fit, should be equal
        assert np.array_equiv(PARTIAL_FIT_X, SINGLE_FIT_X), \
            (f"new uniques in partial fits -- partial fitted X does not "
             f"equal single fitted X")
        assert np.array_equiv(PARTIAL_FIT_Y, SINGLE_FIT_Y), \
            (f"new uniques in partial fits -- partial fitted y does not "
             f"equal single fitted y")
    # END TEST LATER PARTIAL FITS ACCEPT NEW UNIQUES *******************


@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestTransform:


    # - num columns must equal num columns seen during fit
    # - must have at least 3 samples
    # - allows nan
    # - output is C contiguous
    # - does not mutate passed X


    @pytest.mark.parametrize('_copy',
        (-1, 0, 1, 3.14, True, False, None, 'junk', [0, 1], (1,), {'a': 1}, min)
    )
    def test_copy_validation(self, X_np, _shape, _kwargs, _copy):

        _MCT = MCT(**_kwargs)
        _MCT.fit(X_np)

        if isinstance(_copy, (bool, type(None))):
            _MCT.transform(X_np, copy=_copy)
        else:
            with pytest.raises(TypeError):
                _MCT.transform(X_np, copy=_copy)


    def test_accepts_y_equals_none(self, _kwargs, X_np):
        TestCls = MCT(**_kwargs)

        TestCls.partial_fit(X_np, None)
        TestCls.fit(X_np, None)
        TestCls.transform(X_np, None)
        TestCls.fit_transform(X_np, None)



    # # ValueError WHEN ROWS OF y != X ROWS ONLY UNDER transform

    @pytest.mark.parametrize('fit_y_format', ('np', 'pd', 'pl'))
    @pytest.mark.parametrize('fit_y_dim', (1, 2))
    @pytest.mark.parametrize('trfm_y_format', ('np', 'pd', 'pl'))
    @pytest.mark.parametrize('trfm_y_dim', (1, 2))
    @pytest.mark.parametrize('trfm_y_rows', ('good', 'less_row', 'more_row'))
    def test_except_on_bad_y_rows(
        self, X_np, _X_factory, _columns, _shape, _kwargs, fit_y_format,
        fit_y_dim, trfm_y_format, trfm_y_dim, trfm_y_rows, x_rows
    ):

        # only in transform. y is ignored in all of the 'fit's

        # use _X_factory to make y

        TestCls = MCT(**_kwargs)

        # build fit y ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
        fit_y = _X_factory(
            _dupl=None, _has_nan=False, _format=fit_y_format, _dtype='int',
            _columns=_columns[:2], _constants=None, _noise=0, _zeros=None,
            _shape=(_shape[0], 2)
        )
        assert len(fit_y.shape) == 2
        if fit_y_dim == 1:
            if fit_y_format == 'np':
                fit_y = fit_y[:, 0]
            elif fit_y_format == 'pd':
                fit_y = fit_y.iloc[:, 0]
            elif fit_y_format == 'pl':
                fit_y = fit_y[:, 0]
            else:
                raise Exception
        # END build fit y ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

        # build transform y  ** ** ** ** ** ** ** ** ** ** ** ** ** **
        _shape_dict = {
            'good':_shape[0], 'less_row':_shape[0]-1, 'more_row':_shape[1]+1
        }
        trfm_Y = _X_factory(
            _dupl=None, _has_nan=False, _format=trfm_y_format, _dtype='int',
            _columns=_columns[:2], _constants=None, _noise=0, _zeros=None,
            _shape=(_shape_dict[trfm_y_rows], 2)
        )
        assert len(trfm_Y.shape) == 2
        if trfm_y_dim == 1:
            if trfm_y_format == 'np':
                trfm_Y = trfm_Y[:, 0]
            elif trfm_y_format == 'pd':
                trfm_Y = trfm_Y.iloc[:, 0]
            elif trfm_y_format == 'pl':
                trfm_Y = trfm_Y[:, 0]
            else:
                raise Exception
        # END build transform y ** ** ** ** ** ** ** ** ** ** ** ** **

        value_error = 0
        # True only if trfm_y rows != X rows
        value_error += (trfm_Y.shape[0] != x_rows) if trfm_Y is not None else 0

        TestCls.partial_fit(X_np, fit_y)

        if value_error:
            with pytest.raises(ValueError):
                TestCls.transform(X_np, trfm_Y)
        elif not value_error:
            TestCls.transform(X_np, trfm_Y)


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csr_array'))
    @pytest.mark.parametrize('y_input_type', ('np', 'pd', 'pl'))
    @pytest.mark.parametrize('output_type', (None, 'default', 'pandas', 'polars'))
    def test_output_types(
        self, _X_factory, y_np, _columns, _shape, _kwargs, _format, y_input_type,
        output_type
    ):

        _X_wip = _X_factory(
            _dupl=None, _has_nan=False, _format=_format, _dtype='int',
            _columns=_columns if _format in ['pd', 'pl'] else None,
            _constants=None, _noise=0, _zeros=None, _shape=_shape
        )

        if y_input_type == 'np':
            _y_wip = y_np.copy()
        elif y_input_type == 'pd':
            _y_wip = pd.DataFrame(y_np, columns=['y1'])
        elif y_input_type == 'pl':
            _y_wip = pl.from_numpy(y_np, schema=['y1'])
        else:
            raise Exception

        TestCls = MCT(**_kwargs)
        TestCls.set_output(transform=output_type).fit(_X_wip, _y_wip)
        TRFM_X, TRFM_Y = TestCls.transform(_X_wip, _y_wip)

        # if output_type is None, should return same type as given
        # if 'default', should return np array no matter what given
        # if 'pandas' or 'polars', should return pd/pl df no matter what given
        _output_type_dict = {
            None: type(_X_wip), 'default': np.ndarray, 'polars': pl.DataFrame,
            'pandas': pd.DataFrame
        }
        assert isinstance(TRFM_X, _output_type_dict[output_type]), \
            (f"X input type {type(_X_wip)}, X output type {type(TRFM_X)}, "
             f"expected output_type {output_type}")

        # y output container is never changed
        assert type(TRFM_Y) == type(_y_wip), \
            (f"Y output type ({type(TRFM_Y)}) != "
             f"Y input type ({type(_y_wip)})")


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csc_array'))
    def test_X_is_not_mutated(
        self, _X_factory, _columns, _mct_cols, _shape, _kwargs, _format
    ):

        _X_wip = _X_factory(
            _dupl=None, _has_nan=False, _format=_format, _dtype='int',
            _columns=_columns, _constants=None, _noise=0, _zeros=None,
            _shape=_shape
        )

        if _format == 'np':
            assert _X_wip.flags['C_CONTIGUOUS'] is True

        try:
            _X_wip_before = _X_wip.copy()
        except:
            _X_wip_before = _X_wip.clone()


        _MCT = MCT(**_kwargs).fit(_X_wip)

        # verify _X_wip does not mutate in transform()
        TRFM_X = _MCT.transform(_X_wip)


        # ASSERTIONS v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        assert isinstance(_X_wip, type(_X_wip_before))
        assert _X_wip.shape == _X_wip_before.shape

        if isinstance(_X_wip_before, np.ndarray):
            assert np.array_equal(_X_wip_before, _X_wip)
            # if numpy output, is C order
            assert _X_wip.flags['C_CONTIGUOUS'] is True
            assert _X_wip.dtype == _X_wip_before.dtype
        elif hasattr(_X_wip_before, 'columns'):    # DATAFRAMES
            assert _X_wip.equals(_X_wip_before)
            assert np.array_equal(_X_wip.dtypes, _X_wip_before.dtypes)
        elif hasattr(_X_wip_before, 'toarray'):
            assert np.array_equal(
                _X_wip.toarray(), _X_wip_before.toarray()
            )
            assert _X_wip.dtype == _X_wip_before.dtype
        else:
            raise Exception


    @pytest.mark.parametrize('count_threshold', [2, 3])
    @pytest.mark.parametrize('ignore_float_columns', [True, False])
    @pytest.mark.parametrize('ignore_non_binary_integer_columns', [True, False])
    @pytest.mark.parametrize('ignore_columns', [None, [0, 1, 2, 3]])
    @pytest.mark.parametrize('ignore_nan', [True, False])
    @pytest.mark.parametrize('handle_as_bool', ('hab_1', 'hab_2', 'hab_3'))
    @pytest.mark.parametrize('delete_axis_0', [False, True])
    @pytest.mark.parametrize('reject_unseen_values', [False, True])
    def test_accuracy_one_rcr(self, _kwargs, X_np, y_np, count_threshold, ignore_columns,
        ignore_float_columns, ignore_non_binary_integer_columns, ignore_nan, mmct,
        handle_as_bool, delete_axis_0, reject_unseen_values, _mct_cols, x_cols
    ):

        # this compares 1rcrX1 outputs of MCT and mmct

        if handle_as_bool == 'hab_1':
            HANDLE_AS_BOOL = None
        elif handle_as_bool == 'hab_2':
            HANDLE_AS_BOOL = list(range(_mct_cols, 2 * _mct_cols))
        elif handle_as_bool == 'hab_3':
            HANDLE_AS_BOOL = lambda X: list(range(_mct_cols, 2 * _mct_cols))
        else:
            raise Exception

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['count_threshold'] = count_threshold
        _new_kwargs['ignore_float_columns'] = ignore_float_columns
        _new_kwargs['ignore_non_binary_integer_columns'] = \
            ignore_non_binary_integer_columns
        _new_kwargs['ignore_columns'] = ignore_columns
        _new_kwargs['ignore_nan'] = ignore_nan
        _new_kwargs['handle_as_bool'] = HANDLE_AS_BOOL
        _new_kwargs['delete_axis_0'] = delete_axis_0
        _new_kwargs['reject_unseen_values'] = reject_unseen_values
        _new_kwargs['max_recursions'] = 1

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        TestCls = MCT(**_new_kwargs)
        TRFM_X1, TRFM_Y1 = TestCls.fit_transform(X_np.copy(), y_np.copy())

        # validate MCT 1rcrX1 get_support and object dimensions make sense
        _support = TestCls.get_support(indices=False)
        assert len(_support) == X_np.shape[1]
        assert TRFM_X1.shape[1] == sum(_support)
        del _support

        _row_support = TestCls.get_row_support(indices=False)
        assert len(_row_support) == X_np.shape[0]
        assert TRFM_X1.shape[0] == sum(_row_support)

        # assert columns in get_support and those actually in the output match
        _get_support_idxs = TestCls.get_support(indices=True)
        _actual_idxs = []
        for col_idx in range(TRFM_X1.shape[1]):
            for col_idx2 in range(X_np.shape[1]):
                NOT_NAN_MASK = np.logical_not(nan_mask(TRFM_X1[:, col_idx]))
                if np.array_equal(
                    TRFM_X1[:, col_idx][NOT_NAN_MASK],
                    X_np[_row_support, col_idx2][NOT_NAN_MASK]
                ):
                    _actual_idxs.append(col_idx2)

        assert np.array_equal(_get_support_idxs, _actual_idxs), \
            f"get_support: {_get_support_idxs}, actual_idxs: {_actual_idxs}"
        # END assert columns in get_support and those actually in the data match

        # END validate MCT 1rcrX1 get_support and object dimensions make sense

        del _get_support_idxs, _actual_idxs, _row_support

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        # BUILD MOCK_X & MOCK_Y

        try:
            _ignore_columns = ignore_columns(X_np)
        except:
            _ignore_columns = ignore_columns
        try:
            _handle_as_bool = HANDLE_AS_BOOL(X_np)
        except:
            _handle_as_bool = HANDLE_AS_BOOL

        MmctCls = mmct()
        MOCK_X1, MOCK_Y1 = MmctCls.trfm(
            X_np.copy(), y_np.copy(), _ignore_columns, ignore_nan,
            ignore_non_binary_integer_columns, ignore_float_columns,
            _handle_as_bool, delete_axis_0, count_threshold
        )

        assert len(MmctCls.get_support_) == X_np.shape[1]
        assert MOCK_X1.shape[1] == sum(MmctCls.get_support_)

        # END BUILD MOCK_X & MOCK_Y #
        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        assert np.array_equal(
            TestCls.get_support(indices=False),
            MmctCls.get_support_
        )

        assert TRFM_X1.shape == MOCK_X1.shape
        assert np.array_equiv(
            TRFM_X1[np.logical_not(nan_mask(TRFM_X1))],
            MOCK_X1[np.logical_not(nan_mask(MOCK_X1))]
        )

        assert TRFM_Y1.shape == MOCK_Y1.shape
        assert np.array_equiv(TRFM_Y1.astype(str), MOCK_Y1.astype(str))


    @pytest.mark.parametrize('count_threshold', (2, 3))
    @pytest.mark.parametrize('ignore_float_columns', (True, False))
    @pytest.mark.parametrize('ignore_non_binary_integer_columns', (True, False))
    @pytest.mark.parametrize('ignore_columns', (None, (0, 1, 2, 3)))
    @pytest.mark.parametrize('ignore_nan', (True, False))
    @pytest.mark.parametrize('handle_as_bool', ('hab_1', 'hab_2', 'hab_3'))
    @pytest.mark.parametrize('delete_axis_0', (True, False))
    @pytest.mark.parametrize('reject_unseen_values', (True, False))
    def test_accuracy_two_rcr_one_shot(self, _kwargs, X_np, y_np, count_threshold,
        ignore_columns, ignore_float_columns, ignore_non_binary_integer_columns,
        ignore_nan, handle_as_bool, delete_axis_0, reject_unseen_values,
        _mct_cols, x_cols, mmct
    ):

        # this compares 2rcr output of MCT against 2x1rcr output of mmct

        if handle_as_bool == 'hab_1':
            HANDLE_AS_BOOL = None
        elif handle_as_bool == 'hab_2':
            HANDLE_AS_BOOL = list(range(_mct_cols, 2 * _mct_cols))
        elif handle_as_bool == 'hab_3':
            HANDLE_AS_BOOL = lambda X: list(range(_mct_cols, 2 * _mct_cols))
        else:
            raise Exception

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['count_threshold'] = count_threshold
        _new_kwargs['ignore_float_columns'] = ignore_float_columns
        _new_kwargs['ignore_non_binary_integer_columns'] = \
            ignore_non_binary_integer_columns
        _new_kwargs['ignore_columns'] = ignore_columns
        _new_kwargs['ignore_nan'] = ignore_nan
        _new_kwargs['handle_as_bool'] = HANDLE_AS_BOOL
        _new_kwargs['delete_axis_0'] = delete_axis_0
        _new_kwargs['reject_unseen_values'] = reject_unseen_values
        _new_kwargs['max_recursions'] = 2

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # MCT one-shot 2 rcr
        TestCls = MCT(**_new_kwargs)
        TRFM_X, TRFM_Y = TestCls.fit_transform(X_np.copy(), y_np.copy())
        # validate MCT 2rcrX1 get_support and object dimensions make sense
        _support = TestCls.get_support(indices=False)
        assert len(_support) == X_np.shape[1]
        assert TRFM_X.shape[1] == sum(_support)

        _row_support = TestCls.get_row_support(indices=False)
        assert len(_row_support) == X_np.shape[0]
        assert TRFM_X.shape[0] == sum(_row_support)

        # assert columns in get_support and those actually in the data match
        _get_support_idxs = TestCls.get_support(indices=True)
        _actual_idxs = []
        for col_idx in range(TRFM_X.shape[1]):
            for col_idx2 in range(X_np.shape[1]):
                NOT_NAN_MASK = np.logical_not(nan_mask(TRFM_X[:, col_idx]))
                if np.array_equal(
                    TRFM_X[:, col_idx][NOT_NAN_MASK],
                    X_np[_row_support, col_idx2][NOT_NAN_MASK]
                ):
                    _actual_idxs.append(col_idx2)


        assert np.array_equal(_get_support_idxs, _actual_idxs), \
            f"get_support: {_get_support_idxs}, actual_idxs: {_actual_idxs}"

        del _support, _actual_idxs, _get_support_idxs

        # END assert columns in get_support and those actually in the data match

        # END validate MCT 2rcrX1 get_support and object dimensions make sense

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        # BUILD MOCK_X & MOCK_Y

        try:
            _ignore_columns = ignore_columns(X_np)
        except:
            _ignore_columns = ignore_columns
        try:
            _handle_as_bool = HANDLE_AS_BOOL(X_np)
        except:
            _handle_as_bool = HANDLE_AS_BOOL

        # ** * ** * ** * ** * **
        # mmct first recursion
        mmct_first_rcr = mmct()   # give class a name to access attr later
        MOCK_X1, MOCK_Y1 = mmct_first_rcr.trfm(
            X_np.copy(), y_np.copy(), _ignore_columns, ignore_nan,
            ignore_non_binary_integer_columns, ignore_float_columns,
            _handle_as_bool, delete_axis_0, count_threshold
        )

        assert len(mmct_first_rcr.get_support_) == X_np.shape[1]
        assert MOCK_X1.shape[1] == sum(mmct_first_rcr.get_support_)

        # ** * ** * ** * ** * ** *

        # ADJUST ign_columns & handle_as_bool FOR 2ND RECURSION ** ** ** **
        # USING mmct get_support

        if MOCK_X1.shape[1] == X_np.shape[1]:
            scd_ignore_columns = _ignore_columns
            mmct_scd_handle_as_bool = _handle_as_bool
        else:
            NEW_COLUMN_MASK = mmct_first_rcr.get_support_

            OG_IGN_COL_MASK = np.zeros(X_np.shape[1]).astype(bool)
            OG_IGN_COL_MASK[list(_ignore_columns) if _ignore_columns else []] = True
            scd_ignore_columns = \
                np.arange(sum(NEW_COLUMN_MASK))[OG_IGN_COL_MASK[NEW_COLUMN_MASK]]
            if _ignore_columns is None or len(scd_ignore_columns) == 0:
                scd_ignore_columns = None

            OG_H_A_B_MASK = np.zeros(X_np.shape[1]).astype(bool)
            OG_H_A_B_MASK[_handle_as_bool] = True
            mmct_scd_handle_as_bool = \
                np.arange(sum(NEW_COLUMN_MASK))[OG_H_A_B_MASK[NEW_COLUMN_MASK]]
            if _handle_as_bool is None or len(mmct_scd_handle_as_bool) == 0:
                mmct_scd_handle_as_bool = None

            del NEW_COLUMN_MASK, OG_IGN_COL_MASK, OG_H_A_B_MASK
        # END ADJUST ign_columns & handle_as_bool FOR 2ND RECURSION ** ** **


        # ** * ** * ** * ** * ** * **
        # mmct 2nd recursion
        mmct_scd_rcr = mmct()
        MOCK_X2, MOCK_Y2 = mmct_scd_rcr.trfm(
            MOCK_X1, MOCK_Y1, scd_ignore_columns, ignore_nan,
            ignore_non_binary_integer_columns, ignore_float_columns,
            mmct_scd_handle_as_bool, delete_axis_0, count_threshold
        )
        # ** * ** * ** * ** * ** * **

        assert len(mmct_scd_rcr.get_support_) == MOCK_X1.shape[1]
        assert MOCK_X2.shape[1] == sum(mmct_scd_rcr.get_support_)

        del MOCK_X1, MOCK_Y1, scd_ignore_columns, mmct_scd_handle_as_bool

        # END BUILD MOCK_X & MOCK_Y #
        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        _adj_get_support = np.array(mmct_first_rcr.get_support_.copy())
        _idxs = np.arange(len(_adj_get_support))[_adj_get_support]
        _adj_get_support[_idxs] = mmct_scd_rcr.get_support_
        del _idxs

        assert np.array_equal(
            TestCls.get_support(indices=False),
            _adj_get_support
        )

        del _adj_get_support


        assert TRFM_X.shape == MOCK_X2.shape
        assert np.array_equiv(
            TRFM_X[np.logical_not(nan_mask(TRFM_X))],
            MOCK_X2[np.logical_not(nan_mask(MOCK_X2))]
        ), (f'TestCls y output WITH max_recursions=2 FAILED')

        assert TRFM_Y.shape == MOCK_Y2.shape
        assert np.array_equiv(TRFM_Y, MOCK_Y2), \
            (f'TestCls y output WITH max_recursions=2 FAILED')


    @pytest.mark.parametrize('count_threshold', [2, 3])
    @pytest.mark.parametrize('ignore_float_columns',[True, False])
    @pytest.mark.parametrize('ignore_non_binary_integer_columns', [True, False])
    @pytest.mark.parametrize('ignore_columns', [None, [0, 1, 2, 3]])
    @pytest.mark.parametrize('ignore_nan', [True, False])
    @pytest.mark.parametrize('handle_as_bool', ('hab_1',  'hab_2', 'hab_3'))
    @pytest.mark.parametrize('delete_axis_0', [False, True])
    @pytest.mark.parametrize('reject_unseen_values', [False, True])
    def test_accuracy_two_rcr_two_shot(self, _kwargs, NAN_X, y_np, count_threshold,
        ignore_columns, ignore_float_columns, ignore_non_binary_integer_columns,
        ignore_nan, handle_as_bool, delete_axis_0, reject_unseen_values,
        _mct_cols, x_cols, mmct
    ):

        # compare MCT 2rcrX1 outputs are equal to MCT 1rcrX2 outputs
        # compare MCT 1rcrX2 output against mmct 1rcrX2 output

        if handle_as_bool == 'hab_1':
            HANDLE_AS_BOOL = None
        elif handle_as_bool == 'hab_2':
            HANDLE_AS_BOOL = list(range(_mct_cols, 2 * _mct_cols))
        elif handle_as_bool == 'hab_3':
            HANDLE_AS_BOOL = lambda X: list(range(_mct_cols, 2 * _mct_cols))
        else:
            raise Exception

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['count_threshold'] = count_threshold
        _new_kwargs['ignore_columns'] = ignore_columns
        _new_kwargs['ignore_float_columns'] = ignore_float_columns
        _new_kwargs['ignore_non_binary_integer_columns'] = \
            ignore_non_binary_integer_columns
        _new_kwargs['ignore_nan'] = ignore_nan
        _new_kwargs['handle_as_bool'] = HANDLE_AS_BOOL
        _new_kwargs['delete_axis_0'] = delete_axis_0
        _new_kwargs['reject_unseen_values'] = reject_unseen_values


        # need to make accommodations for mmct kwargs, cant take callables
        try:
            _ignore_columns = ignore_columns(NAN_X)
        except:
            _ignore_columns = ignore_columns

        try:
            _handle_as_bool = HANDLE_AS_BOOL(NAN_X)
        except:
            _handle_as_bool = HANDLE_AS_BOOL

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # MCT first one-shot rcr
        TestCls1 = MCT(**_new_kwargs)
        TRFM_X_1, TRFM_Y_1 = TestCls1.fit_transform(NAN_X.copy(), y_np.copy())

        _first_support = TestCls1.get_support(indices=False).copy()

        # validate MCT 1rcrX1 get_support and object dimensions make sense
        assert len(_first_support) == NAN_X.shape[1]
        assert TRFM_X_1.shape[1] == sum(_first_support)

        # assert columns in get_support and those actually in the data match
        _get_support_idxs = TestCls1.get_support(indices=True)
        _row_support = TestCls1.get_row_support(indices=False)
        _actual_idxs = []
        for col_idx in range(TRFM_X_1.shape[1]):
            for col_idx2 in range(NAN_X.shape[1]):
                NOT_NAN_MASK = np.logical_not(nan_mask(TRFM_X_1[:, col_idx]))
                if np.array_equal(
                    TRFM_X_1[:, col_idx][NOT_NAN_MASK],
                    NAN_X[_row_support, col_idx2][NOT_NAN_MASK]
                ):
                    _actual_idxs.append(col_idx2)

        assert np.array_equal(_get_support_idxs, _actual_idxs), \
            f"get_support: {_get_support_idxs}, actual_idxs: {_actual_idxs}"

        del _get_support_idxs, _row_support, _actual_idxs

        # END assert columns in get_support and those actually in the data match

        # END validate MCT 1rcrX1 get_support and object dimensions make sense

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


        # ADJUST ign_columns & handle_as_bool FOR 2ND RECURSION
        # USING MCT get_support
        NEW_COLUMN_MASK = TestCls1.get_support(indices=False)

        OG_IGN_COL_MASK = np.zeros(NAN_X.shape[1]).astype(bool)
        OG_IGN_COL_MASK[_ignore_columns] = True
        mct_scd_ignore_columns = \
            np.arange(sum(NEW_COLUMN_MASK))[OG_IGN_COL_MASK[NEW_COLUMN_MASK]]
        if _ignore_columns is None or len(mct_scd_ignore_columns) == 0:
            mct_scd_ignore_columns = None

        OG_H_A_B_MASK = np.zeros(NAN_X.shape[1]).astype(bool)
        OG_H_A_B_MASK[_handle_as_bool] = True
        mct_scd_handle_as_bool = \
            np.arange(sum(NEW_COLUMN_MASK))[OG_H_A_B_MASK[NEW_COLUMN_MASK]]
        if _handle_as_bool is None or len(mct_scd_handle_as_bool) == 0:
            mct_scd_handle_as_bool = None

        del NEW_COLUMN_MASK, OG_IGN_COL_MASK, OG_H_A_B_MASK
        # END ADJUST ign_columns & handle_as_bool FOR 2ND RECURSION

        _new_kwargs['ignore_columns'] = mct_scd_ignore_columns
        _new_kwargs['handle_as_bool'] = mct_scd_handle_as_bool

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # MCT second one-shot rcr
        TestCls2 = MCT(**_new_kwargs)
        TRFM_X_2, TRFM_Y_2 = TestCls2.fit_transform(TRFM_X_1, TRFM_Y_1)

        # validate MCT 1rcrX2 get_support and object dimensions make sense
        _second_support = TestCls2.get_support(indices=False)
        assert len(_second_support) == TRFM_X_1.shape[1]
        assert TRFM_X_2.shape[1] == sum(_second_support)

        # assert columns in get_support and those actually in the data match
        _get_support_idxs = TestCls2.get_support(indices=True)
        _row_support = TestCls2.get_row_support(indices=False)
        _actual_idxs = []
        for col_idx in range(TRFM_X_2.shape[1]):
            for col_idx2 in range(TRFM_X_1.shape[1]):
                NOT_NAN_MASK = np.logical_not(nan_mask(TRFM_X_2[:, col_idx]))
                if np.array_equal(
                    TRFM_X_2[:, col_idx][NOT_NAN_MASK],
                    TRFM_X_1[_row_support, col_idx2][NOT_NAN_MASK]
                ):
                    _actual_idxs.append(col_idx2)


        assert np.array_equal(_get_support_idxs, _actual_idxs), \
            f"get_support: {_get_support_idxs}, actual_idxs: {_actual_idxs}"

        del _second_support, _actual_idxs, _get_support_idxs, _row_support

        # END assert columns in get_support and those actually in the data match

        # END validate MCT 1rcrX2 get_support and object dimensions make sense

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # reset _new_kwargs
        _new_kwargs['ignore_columns'] = ignore_columns
        _new_kwargs['handle_as_bool'] = HANDLE_AS_BOOL

        # compare 2 one-shot MCTs against 1 two-shot MCT - -- - -- - -- - -- - --
        TestCls_2SHOT = MCT(**_new_kwargs)  # use original _new_kwargs!
        TestCls_2SHOT.set_params(max_recursions=2)
        TRFM_X_2SHOT, TRFM_Y_2SHOT = TestCls_2SHOT.fit_transform(NAN_X.copy(), y_np.copy())

        _adj_get_support_mct = np.array(_first_support.copy())
        _idxs = np.arange(len(_adj_get_support_mct))[_adj_get_support_mct]
        _adj_get_support_mct[_idxs] = TestCls2.get_support(indices=False)
        del _idxs

        # compare MCT 2rcrX1 outputs are equal to MCT 1rcrX2 outputs
        assert len(TestCls_2SHOT.get_support(indices=False)) == NAN_X.shape[1]
        assert sum(TestCls_2SHOT.get_support(indices=False)) == TRFM_X_2SHOT.shape[1]

        assert np.array_equal(
            _adj_get_support_mct,
            TestCls_2SHOT.get_support(indices=False)
        )

        del _adj_get_support_mct

        assert TRFM_X_2.shape == TRFM_X_2SHOT.shape
        assert np.array_equiv(
            TRFM_X_2[np.logical_not(nan_mask(TRFM_X_2))],
            TRFM_X_2SHOT[np.logical_not(nan_mask(TRFM_X_2SHOT))]
        ), f'1X2rcr X output != 2X1rcr X output'

        assert TRFM_Y_2.shape == TRFM_Y_2SHOT.shape
        assert np.array_equiv(TRFM_Y_2, TRFM_Y_2SHOT), \
            f'1X2rcr Y output != 2X1rcr Y output'

        del TRFM_X_2SHOT, TRFM_Y_2SHOT
        # END compare 2 one-shot MCTs against 1 two-shot MCT - -- - -- -

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        # BUILD MOCK_X & MOCK_Y #
        # mmct first recursion
        mmct_first_rcr = mmct()   # give class a name to access attr later
        MOCK_X1, MOCK_Y1 = mmct_first_rcr.trfm(
            NAN_X.copy(), y_np.copy(), _ignore_columns, ignore_nan,
            ignore_non_binary_integer_columns, ignore_float_columns,
            _handle_as_bool, delete_axis_0, count_threshold
        )

        # validate mmct 1rcrX1 get_support and object dimensions make sense
        assert len(mmct_first_rcr.get_support_) == NAN_X.shape[1]
        assert MOCK_X1.shape[1] == sum(mmct_first_rcr.get_support_)


        # ** * ** * ** * ** * ** *
        # compare MCT 1rcrX1 output against mmct 1rcrX1 output

        assert np.array_equal(
            TestCls1.get_support(indices=False),
            mmct_first_rcr.get_support_
        )

        assert TRFM_X_1.shape == MOCK_X1.shape
        assert np.array_equiv(
            TRFM_X_1[np.logical_not(nan_mask(TRFM_X_1))],
            MOCK_X1[np.logical_not(nan_mask(MOCK_X1))]
        ), f'X output for 1X PASSES THRU TestCls WITH max_recursions=1 FAILED'

        assert TRFM_Y_1.shape == MOCK_Y1.shape
        assert np.array_equiv(TRFM_Y_1, MOCK_Y1), \
            (f'y output for 1X PASSES THRU TestCls WITH max_recursions=1 FAILED')

        del TRFM_X_1, TRFM_Y_1

        # ** * ** * ** * ** * ** *

        # ADJUST ign_columns & handle_as_bool FOR 2ND RECURSION ** ** ** **
        # USING mmct get_support
        NEW_COLUMN_MASK = mmct_first_rcr.get_support_

        OG_IGN_COL_MASK = np.zeros(NAN_X.shape[1]).astype(bool)
        OG_IGN_COL_MASK[_ignore_columns] = True
        mmct_scd_ignore_columns = \
            np.arange(sum(NEW_COLUMN_MASK))[OG_IGN_COL_MASK[NEW_COLUMN_MASK]]
        if _ignore_columns is None or len(mmct_scd_ignore_columns) == 0:
            mmct_scd_ignore_columns = None

        OG_H_A_B_MASK = np.zeros(x_cols).astype(bool)
        OG_H_A_B_MASK[_handle_as_bool] = True
        mmct_scd_handle_as_bool = \
            np.arange(sum(NEW_COLUMN_MASK))[OG_H_A_B_MASK[NEW_COLUMN_MASK]]
        if _handle_as_bool is None or len(mmct_scd_handle_as_bool) == 0:
            mmct_scd_handle_as_bool = None

        del NEW_COLUMN_MASK, OG_IGN_COL_MASK, OG_H_A_B_MASK
        # # END ADJUST ign_columns & handle_as_bool FOR 2ND RECURSION ** ** **

        # compare mmct_scd_ignore_columns to mct_scd_ignore_columns,
        # mmct_scd_handle_as_bool to mmct_scd_handle_as_bool
        assert np.array_equal(mmct_scd_ignore_columns, mct_scd_ignore_columns)
        assert np.array_equal(mmct_scd_handle_as_bool, mct_scd_handle_as_bool)

        # ** * ** * ** * ** * ** * **
        # mmct 2nd recursion
        mmct_scd_rcr = mmct()   # give class a name to access attr later
        MOCK_X2, MOCK_Y2 = mmct_scd_rcr.trfm(
            MOCK_X1.copy(), MOCK_Y1.copy(), mmct_scd_ignore_columns, ignore_nan,
            ignore_non_binary_integer_columns, ignore_float_columns,
            mmct_scd_handle_as_bool, delete_axis_0, count_threshold
        )

        # validate mmct 1rcrX2 get_support and object dimensions make sense
        assert len(mmct_scd_rcr.get_support_) == MOCK_X1.shape[1]
        assert MOCK_X2.shape[1] == sum(mmct_scd_rcr.get_support_)

        del MOCK_X1, MOCK_Y1, mmct_scd_ignore_columns, mmct_scd_handle_as_bool

        # END BUILD MOCK_X & MOCK_Y #
        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


        # vvvv *************************************************
        # where <function array_equiv> 2133: AssertionError

        # compare MCT 1rcrX2 output against mmct 1rcrX2 output
        _adj_get_support_mct = np.array(TestCls1.get_support(indices=False).copy())
        _idxs = np.arange(len(_adj_get_support_mct))[_adj_get_support_mct]
        _adj_get_support_mct[_idxs] = TestCls2.get_support(indices=False)
        del _idxs

        _adj_get_support_mmct = np.array(mmct_first_rcr.get_support_.copy())
        _idxs = np.arange(len(_adj_get_support_mmct))[_adj_get_support_mmct]
        _adj_get_support_mmct[_idxs] = mmct_scd_rcr.get_support_
        del _idxs

        assert np.array_equal(_adj_get_support_mct, _adj_get_support_mmct)

        del _adj_get_support_mct, _adj_get_support_mmct


        assert TRFM_X_2.shape == MOCK_X2.shape
        assert np.array_equiv(
            TRFM_X_2[np.logical_not(nan_mask(TRFM_X_2))],
            MOCK_X2[np.logical_not(nan_mask(MOCK_X2))]
        ), f'X output for 2X PASSES THRU TestCls WITH max_recursions=1 FAILED'

        assert TRFM_Y_2.shape == MOCK_Y2.shape
        assert np.array_equiv(TRFM_Y_2, MOCK_Y2), \
            (f'y output for 2X PASSES THRU TestCls WITH max_recursions=1 FAILED')

        del TRFM_X_2, TRFM_Y_2
        del _ignore_columns, _handle_as_bool


    def test_one_all_nans(self, _shape):

        # need to not ignore float columns because nans are float
        _MCT = MCT(
            count_threshold=3,
            ignore_float_columns=False,
            ignore_non_binary_integer_columns=True,
            max_recursions=1
        )

        _X = np.vstack((
            np.random.randint(0, 10, (_shape[0], )),
            np.fromiter((np.nan for i in range(_shape[0])), dtype=np.float64)
        )).transpose().astype(np.float64)

        out = _MCT.fit_transform(_X)

        # the column of all nans should be dropped because it is a constant
        # column and leave behind only the column of floats
        assert np.array_equal(out.ravel(), _X[:, 0])


    # TEST BIN INT COLUMN WITH ALL ABOVE THRESHOLD NOT DELETED #########
    def test_bin_int_above_thresh_not_deleted(self, _kwargs, y_np):
        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['count_threshold'] = 2

        TestCls = MCT(**_new_kwargs)

        _X_wip = np.array(
            [['a', 0], ['b', 0], ['a', 1], ['b', 1], ['c', 0]], dtype=object
        )
        _y_wip = y_np[:_X_wip.shape[0]]

        TestCls.fit(_X_wip, _y_wip)

        TRFM_X, TRFM_Y = TestCls.transform(_X_wip, _y_wip)

        assert TRFM_X.shape[1] == 2, \
            f"bin int column with all values above threshold was deleted"

        assert TRFM_X.shape[0] == 4, \
            f"TRFM_X should have 4 rows but has {TRFM_X.shape[0]}"

    # END TEST BIN INT COLUMN WITH ALL ABOVE THRESHOLD NOT DELETED #####

    # TEST TRANSFORM CONDITIONALLY ACCEPT NEW UNIQUES ******************
    def test_transform_conditionally_accepts_new_uniques(
        self, NO_NAN_X, y_np, _kwargs, _mct_cols, x_rows
    ):
        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['count_threshold'] *= 2

        # USE STR COLUMNS
        X1 = NO_NAN_X[:, (3 * _mct_cols):(4 * _mct_cols)].copy()
        y1 = y_np.copy()

        # fit() & transform() ON X1 TO PROVE X1 PASSES transform()
        TestCls = MCT(**_new_kwargs)
        TestCls.fit(X1, y1)
        OUT_X, OUT_Y = TestCls.transform(X1, y1)
        assert OUT_X.shape[0] > 0
        del TestCls, OUT_X, OUT_Y

        # PEPPER ONE OF THE STR COLUMNS WITH A UNIQUE THAT WAS NOT SEEN DURING fit()
        X2 = X1.copy()
        new_unqs = list('1234567890')
        MASK = np.random.choice(range(x_rows), len(new_unqs), replace=False)
        # put str(number) into str column of alphas
        X2[MASK, 0] = new_unqs
        del new_unqs, MASK
        TestCls = MCT(**_new_kwargs)
        TestCls.fit(X1, y1)

        # DEMONSTRATE NEW VALUES ARE ACCEPTED WHEN reject_unseen_values = False
        TestCls.set_params(reject_unseen_values=False)
        assert TestCls.reject_unseen_values is False
        TestCls.transform(X2, y1)

        # DEMONSTRATE NEW VALUES ARE REJECTED WHEN reject_unseen_values = True
        TestCls.set_params(reject_unseen_values=True)
        assert TestCls.reject_unseen_values is True
        with pytest.raises(ValueError):
            TestCls.transform(X2, y1)

        del X1, y1, X2, TestCls
    # END TEST TRANSFORM CONDITIONALLY ACCEPT NEW UNIQUES **************

    # TEST ALL COLUMNS WILL BE DELETED #################################
    def test_all_columns_will_be_deleted(
            self, _kwargs, _mct_rows, x_cols, x_rows
    ):
        # CREATE VERY SPARSE DATA
        TEST_X = np.zeros((_mct_rows, x_cols), dtype=np.uint8)
        TEST_Y = np.random.randint(0, 2, _mct_rows)

        for col_idx in range(x_cols):
            MASK = np.random.choice(range(x_rows), 2, replace=False), col_idx
            TEST_X[MASK] = 1
        del MASK

        TestCls = MCT(**_kwargs)
        TestCls.fit(TEST_X, TEST_Y)

        with pytest.raises(ValueError):
            TestCls.transform(TEST_X, TEST_Y)

        del TEST_X, TEST_Y, col_idx, TestCls

    # TEST ALL COLUMNS WILL BE DELETED #################################

    # TEST ALL ROWS WILL BE DELETED ####################################
    def test_all_rows_will_be_deleted(self, _kwargs, _mct_rows, x_cols):
        # ALL FLOATS
        TEST_X = np.random.uniform(0, 1, (_mct_rows, x_cols))
        TEST_Y = np.random.randint(0, 2, _mct_rows)

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['ignore_float_columns'] = False
        TestCls = MCT(**_new_kwargs)
        TestCls.fit(TEST_X, TEST_Y)

        with pytest.raises(ValueError):
            TestCls.transform(TEST_X, TEST_Y)

        del TEST_X, TEST_Y, TestCls
    # TEST ALL ROWS WILL BE DELETED ####################################


@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestFitTransform:


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csc_matrix'))
    @pytest.mark.parametrize('y_input_type', ('np', 'pd', 'pl'))
    @pytest.mark.parametrize('output_type', (None, 'default', 'pandas', 'polars'))
    def test_output_types(
        self, _X_factory, y_np, _columns, _shape, _kwargs, _format, y_input_type,
        output_type
    ):

        _X_wip = _X_factory(
            _dupl=None, _has_nan=False, _format=_format, _dtype='int',
            _columns=_columns if _format in ['pd', 'pl'] else None,
            _constants=None, _noise=0, _zeros=None, _shape=_shape
        )

        if y_input_type == 'np':
            _y_wip = y_np.copy()
        elif y_input_type == 'pd':
            _y_wip = pd.DataFrame(y_np, columns=['y1'])
        elif y_input_type == 'pl':
            _y_wip = pl.from_numpy(y_np, schema=['y1'])
        else:
            raise Exception


        TestCls = MCT(**_kwargs)
        TestCls.set_output(transform=output_type)

        TRFM_X, TRFM_Y = TestCls.fit_transform(_X_wip, _y_wip)

        # if output_type is None, should return same type as given
        # if  'default', should return np array no matter what given
        # if  'pandas' or 'polars', should return pd/pl df no matter what given
        _output_type_dict = {
            None: type(_X_wip), 'default': np.ndarray, 'polars': pl.DataFrame,
            'pandas': pd.DataFrame
        }
        assert isinstance(TRFM_X, _output_type_dict[output_type]), \
            (f"X input type {type(_X_wip)}, X output type {type(TRFM_X)}, "
             f"expected output_type {output_type}")

        # y output container is never changed
        assert type(TRFM_Y) == type(_y_wip), \
            (f"Y output type ({type(TRFM_Y)}) != Y input type ({type(_y_wip)})")




