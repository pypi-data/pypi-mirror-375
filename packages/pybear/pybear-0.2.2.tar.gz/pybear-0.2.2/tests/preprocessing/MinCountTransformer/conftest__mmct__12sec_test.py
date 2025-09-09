# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#


# this is a test module for a fixture (mmct) used to test MinCountTransformer!
# this is test for a test fixture.
#
# nbi = non-binary-integer



import pytest

from typing import (
    Any,
    Callable
)
import numpy.typing as npt

from copy import deepcopy

import numpy as np

from pybear.utilities._nan_masking import (
    nan_mask,
    nan_mask_string,
    nan_mask_numerical
)


# fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


# ^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
# validate fixtures from conftest

# in a separate module (conftest), build the test vectors for mock_mct_test
# to have certain controlled attributes, such as number of uniques, counts,
# etc., that are guaranteed to be altered by mock_mct in a predictable way

# even though these vectors were subject to informal tests to get the
# correct controlled attributes at the time of construction in conftest,
# do the tests formally here.



# MOCK_X_FLT IS NOT TESTED
@pytest.mark.parametrize('_name',
    ('MOCK_X_BIN', 'MOCK_X_NBI', 'MOCK_X_STR', 'MOCK_X_BOOL')
)
def test_vector_fixtures(_name, _mmct_test_thresh, _source_len, MOCK_X_BIN,
    MOCK_X_NBI, MOCK_X_STR, MOCK_X_BOOL
):

    _VECTOR = {
        'MOCK_X_BIN': MOCK_X_BIN, 'MOCK_X_NBI': MOCK_X_NBI,
        'MOCK_X_STR': MOCK_X_STR, 'MOCK_X_BOOL': MOCK_X_BOOL
    }[_name]

    # STR & NBI: MUST DELETE ALL @ 2X THRESH, NONE @ 1/2 THRESH,
    # AND AT LEAST 1 BUT LEAVE 2+ BEHIND AT THRESH
    _low = _mmct_test_thresh // 2
    _mid = _mmct_test_thresh
    _high = 2 * _mmct_test_thresh

    UNQ_CT_DICT = dict((zip(*np.unique(_VECTOR, return_counts=True))))
    CTS = list(UNQ_CT_DICT.values())

    # ALWAYS MUST HAVE AT LEAST 2 UNQS IN THE COLUMN
    assert not len(CTS) < 2

    # IF IS BIN INT
    if _name == 'MOCK_X_BIN':
        assert len(CTS) == 2
        assert min(UNQ_CT_DICT) == 0
        assert max(UNQ_CT_DICT) == 1
        assert min(CTS) in range(_low, _high)

    # FOR handle_as_bool
    elif _name == 'MOCK_X_BOOL':
        assert sum(sorted(CTS)[:-1]) == _source_len
        assert max(CTS) >= (2 * _mmct_test_thresh)
        assert sum(sorted(CTS)[:-1]) < (2 * _mmct_test_thresh)

    else:  # not BIN or BOOL
        assert max(CTS) < _high
        assert min(CTS) >= _low + 1

        assert sorted(CTS)[-2] >= _mid

        assert min(CTS) < _mid
# ^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v


@pytest.fixture(scope='module')
def MOCK_Y(_mmct_test_rows) -> npt.NDArray[int]:
    return np.random.randint(0, 2, _mmct_test_rows)


@pytest.fixture(scope='function')
def _args(_mct_rows):
    return [_mct_rows // 20]


@pytest.fixture(scope='module')
def DEFAULT_ARGS(MOCK_X_STR, MOCK_Y, _mmct_test_thresh) -> dict[
    str, np.ndarray | None | bool | int
]:
    return {
        'MOCK_X': MOCK_X_STR,
        'MOCK_Y': MOCK_Y,
        'ignore_columns': None,
        'ignore_nan': True,
        'ignore_non_binary_integer_columns': True,
        'ignore_float_columns': True,
        'handle_as_bool': None,
        'delete_axis_0': False,
        'count_threshold': _mmct_test_thresh
    }


@pytest.fixture(scope='module')
def arg_setter(mmct, DEFAULT_ARGS) -> Callable:

    def foo(**new_args) -> tuple[npt.NDArray[Any], npt.NDArray[int]] | npt.NDArray[Any]:

        NEW_DICT = deepcopy(DEFAULT_ARGS)
        ALLOWED = [
            'MOCK_X', 'MOCK_Y', 'ignore_columns', 'ignore_nan',
           'ignore_non_binary_integer_columns', 'ignore_float_columns',
           'handle_as_bool', 'delete_axis_0', 'count_threshold'
        ]
        for kwarg, value in new_args.items():
            if kwarg not in ALLOWED:
                raise ValueError(f'illegal arg "{kwarg}" in arg_setter')
            NEW_DICT[kwarg] = value

        return mmct().trfm(**NEW_DICT)

    return foo

# END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


# tests ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


def test_verify_mmct_ignores_columns(MOCK_X_STR, _mmct_test_thresh, arg_setter):

    out = arg_setter(MOCK_X=MOCK_X_STR, ignore_columns=[0])[0]
    assert np.array_equiv(out.ravel(), MOCK_X_STR.ravel()), \
        f"MOCK_TRFM did not ignore str column"

    out = arg_setter(
        MOCK_X=MOCK_X_STR, ignore_columns=None,
        count_threshold=2 * _mmct_test_thresh
    )[0]
    assert len(out) < len(MOCK_X_STR), \
        f"MOCK_TRFM ignored str column when it shouldnt"


def test_verify_mmct_ignores_flts_nbis_but_not_str(
    arg_setter, MOCK_X_FLT, MOCK_X_NBI, MOCK_X_STR
):

    out = arg_setter(MOCK_X=MOCK_X_FLT, ignore_float_columns=True)[0]
    assert np.array_equiv(out, MOCK_X_FLT), \
        f"MOCK_TRFM did not ignore float column"

    out = arg_setter(
        MOCK_X=MOCK_X_NBI, ignore_non_binary_integer_columns=True
    )[0]
    assert np.array_equiv(out, MOCK_X_NBI), \
        f"MOCK_TRFM did not ignore nbi column"

    out = arg_setter(MOCK_X=MOCK_X_STR,
        ignore_float_columns=True, ignore_non_binary_integer_columns=True
    )[0]
    assert not np.array_equiv(out, MOCK_X_FLT), \
        f"MOCK_TRFM did not alter a str column"


def test_verify_mmct_deletes_all_floats(arg_setter, MOCK_X_FLT):
    out = arg_setter(MOCK_X=MOCK_X_FLT, ignore_float_columns=False)[0]
    assert len(out.ravel()) == 0, \
        f"not all floats were deleted"


def test_verify_unqs_cts_after_trfm_gte_threshold(arg_setter, MOCK_X_NBI,
        MOCK_X_STR, _mmct_test_thresh
):

    out = arg_setter(
        MOCK_X=MOCK_X_NBI,
        ignore_non_binary_integer_columns=False
    )[0]
    min_counts = min(dict((zip(*np.unique(out, return_counts=True)))).values())
    assert min_counts >= _mmct_test_thresh, f"nbi ct < thresh"

    out = arg_setter(MOCK_X=MOCK_X_STR)[0]
    min_counts = min(dict((zip(*np.unique(out, return_counts=True)))).values())
    assert min_counts >= _mmct_test_thresh, f"str ct < thresh"


def test_verify_delete_axis_0(
    MOCK_X_BIN, MOCK_X_FLT, arg_setter, _mmct_test_thresh
):

    NEW_X = np.hstack((MOCK_X_BIN, MOCK_X_FLT))
    TRFM_X = arg_setter(
        MOCK_X=NEW_X,
        ignore_float_columns=True,
        delete_axis_0=False,
        count_threshold=2 * _mmct_test_thresh
    )[0]
    TRFM_FLTS = TRFM_X[:, -1]
    assert np.array_equiv(TRFM_FLTS.ravel(), MOCK_X_FLT.ravel()), \
        f"del_axis_0=False removed rows"
    assert TRFM_X.shape[1] == 1, \
        f"bin column was not removed (has {TRFM_X.shape[1]} columns)"

    TRFM_X = arg_setter(
        MOCK_X=NEW_X,
        ignore_float_columns=True,
        delete_axis_0=True,
        count_threshold=2 * _mmct_test_thresh
    )[0]
    REF_X = MOCK_X_FLT[np.logical_not(MOCK_X_BIN)].reshape((-1, 1))
    assert np.array_equiv(TRFM_X, REF_X), f'delete_axis_0 did not delete rows'

    del NEW_X, TRFM_X, TRFM_FLTS, REF_X



class TestHandleAsBool_1:


    @pytest.mark.parametrize('_trial', ('not_hab', 'low_thr', 'hi_thr'))
    @pytest.mark.parametrize('_delete_axis_0', (False, True))
    def test_delete_axis_0(self, _trial, _delete_axis_0, arg_setter, _mmct_test_rows):

        # THE MOCK_X_NBI & MOCK_X_FLT fixtures are flaky in this test.
        # Build rigged X & thresh just for this test.

        _n_values = _mmct_test_rows // 6
        _exp_freq = _mmct_test_rows / _n_values
        _low_thresh = 2
        _hi_thresh = _exp_freq

        while True:
            FLT = np.random.uniform(0, 1, (_mmct_test_rows, 1))

            NBI = np.random.randint(0, _n_values, (_mmct_test_rows, 1))

            UNQS, CTS = np.unique(NBI, return_counts=True)
            UNQ_CT_DICT = dict((zip(list(map(int, UNQS)), list(map(int, CTS)))))
            # need all freqs to be > _low_thresh
            if not all(map(lambda x: x > _low_thresh, UNQ_CT_DICT.values())):
                continue
            del CTS
            # for hab w hi_thr need zeros to be below thresh for
            # something to be deleted
            if 0 not in UNQ_CT_DICT or UNQ_CT_DICT[0] >= _hi_thresh:
                continue

            NEW_X = np.hstack((FLT, NBI))

            if _trial == 'not_hab':
                # not hab, want to prove that NBI column is removed
                # delete_axis_0 doesnt matter because not hab
                _handle_as_bool = None
                _count_threshold = _exp_freq
            elif _trial == 'low_thr':
                # hab but low thresh, prove that nothing is deleted
                _handle_as_bool = [1]
                _count_threshold = 2
            elif _trial == 'hi_thr':
                # hab but high thresh, prove NBI column is removed, but rows
                # deleted depends on delete_axis_0
                _handle_as_bool = [1]
                _count_threshold = _exp_freq
            else:
                raise Exception

            TRFM_X = arg_setter(
                MOCK_X=NEW_X,
                ignore_float_columns=True,
                ignore_non_binary_integer_columns=False,
                handle_as_bool=_handle_as_bool,
                delete_axis_0=_delete_axis_0,
                count_threshold=_count_threshold
            )[0]

            if TRFM_X.shape[0] < 1 or TRFM_X.shape[1] < 1:
                continue
            else:
                break


        if _trial == 'not_hab':
            # column 0 is flt, column 1 is nbi
            # delete_axis_0 ON NBI WITH handle_as_bool==None DOESNT MATTER
            # HANDLED LIKE ANY NON_BIN_INT AND WILL ALWAYS DELETE ROWS
            # for both delete_axis_zero and not:
            assert TRFM_X.shape[0] < _mmct_test_rows, \
                f'handle_as_bool test column delete did not delete rows'

        elif _trial == 'low_thr':
            # column 0 is flt, column 1 is nbi
            # delete_axis_0 ON NBI WHEN handle_as_bool w low thresh
            # SHOULD NOT DELETE
            # is the same for delete_axis_0 True and False
            assert TRFM_X.shape[1] == 2, \
                (f'handle_as_bool test column was removed '
                 f'({_count_threshold=}, {TRFM_X.shape[1]=}')
            assert TRFM_X.shape[0] == _mmct_test_rows, \
                f'handle_as_bool test deleted rows'
            assert np.array_equiv(TRFM_X, NEW_X)

        elif _trial == 'hi_thr':
            # column 0 is flt, column 1 is nbi
            # high thresh should mark forced-nbi-to-bool rows for deletion,
            # and therefore the whole column, but rows actually deleted
            # depends on delete_axis_0
            assert TRFM_X.shape[1] == 1, \
                f'handle_as_bool test column was not removed'
            if _delete_axis_0 is True:
                assert TRFM_X.shape[0] < _mmct_test_rows, \
                    f'handle_as_bool test did not delete rows'
            elif _delete_axis_0 is False:
                assert np.array_equiv(TRFM_X, FLT)
                assert TRFM_X.shape[0] == _mmct_test_rows, \
                    f'handle_as_bool test deleted rows'
        else:
            raise Exception


class TestIgnoreNan:
    # TEST ignore_nan

    # float ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @staticmethod
    @pytest.fixture(scope='session')
    def NEW_MOCK_X_FLT(MOCK_X_FLT, _mmct_test_rows, _mmct_test_thresh):
        NEW_MOCK_X_FLT = MOCK_X_FLT.copy()
        NAN_MASK = \
            np.random.choice(
                _mmct_test_rows, _mmct_test_thresh - 1, replace=False
            )
        NEW_MOCK_X_FLT[NAN_MASK] = np.nan
        return NEW_MOCK_X_FLT


    @pytest.mark.parametrize('ignore_nan', (True, False))
    @pytest.mark.parametrize('_trial', ('trial_1', 'trial_2'))
    def test_float(
        self, NEW_MOCK_X_FLT, ignore_nan, _trial, arg_setter, _mmct_test_thresh
    ):

        if _trial == 'trial_1':
            _threshold = _mmct_test_thresh
        elif _trial == 'trial_2':
            _threshold = _mmct_test_thresh // 2

        # NAN IGNORED WHEN ignore_nan=True, REGARDLESS OF THRESHOLD
        # WHEN ignore_nan=False
        # NAN BELOW THRESH, COLUMN DELETED
        # NAN ABOVE THRESH, COLUMN DELETED
        TRFM_X = arg_setter(
            MOCK_X=NEW_MOCK_X_FLT,
            ignore_float_columns=False,
            ignore_nan=ignore_nan,
            count_threshold=_threshold
        )[0]

        assert TRFM_X.size == 0, f"float column was not deleted"

    # END float ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # bin ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @staticmethod
    @pytest.fixture(scope='session')
    def NEW_MOCK_X_BIN_1(MOCK_X_BIN, _mmct_test_rows, _mmct_test_thresh):
        # has _mmct_test_thresh // 2 - 1 nans (below lowest thresh)
        # lowest freq of any unq is >= _mmct_test_thresh // 2
        while True:
            NEW_MOCK_X_BIN = MOCK_X_BIN.copy().astype(np.float64)
            NAN_MASK = np.zeros(_mmct_test_rows).astype(bool)
            RANDOM_IDXS = np.random.choice(
                _mmct_test_rows, _mmct_test_thresh // 2 - 1, replace=False
            )
            NAN_MASK[RANDOM_IDXS] = True
            NEW_MOCK_X_BIN[NAN_MASK] = np.nan
            # ensure all unqs besides nans are still above _mmct_test_thresh // 2
            if min(np.unique(
                    NEW_MOCK_X_BIN[np.logical_not(NAN_MASK)],
                    return_counts=True
            )[1]) >= _mmct_test_thresh // 2:
                del NAN_MASK, RANDOM_IDXS
                break

        return NEW_MOCK_X_BIN


    @staticmethod
    @pytest.fixture(scope='session')
    def NEW_MOCK_X_BIN_2(MOCK_X_BIN, _mmct_test_rows, _mmct_test_thresh):
        # has _mmct_test_thresh nans (at or above lowest thresh)
        # lowest freq of any unq is >= _mmct_test_thresh // 2
        while True:
            NEW_MOCK_X_BIN = MOCK_X_BIN.copy().astype(np.float64)
            NAN_MASK = np.zeros(_mmct_test_rows).astype(bool)
            NAN_MASK[
                np.random.choice(
                    _mmct_test_rows, _mmct_test_thresh, replace=False
                )
            ] = True
            NEW_MOCK_X_BIN[NAN_MASK] = np.nan
            # ensure all unqs besides nans are still above _mmct_test_thresh // 2
            if min(np.unique(
                NEW_MOCK_X_BIN[np.logical_not(NAN_MASK)],
                return_counts=True
            )[1]) >= _mmct_test_thresh // 2:
                del NAN_MASK
                break

        return NEW_MOCK_X_BIN


    @pytest.mark.parametrize('_DATA', ('DATA_1', 'DATA_2'))
    @pytest.mark.parametrize('_delete_axis_0', (True, False))
    @pytest.mark.parametrize('_ignore_nan', (True, False))
    def test_bin(self, NEW_MOCK_X_BIN_1, NEW_MOCK_X_BIN_2, _DATA, _ignore_nan,
        _delete_axis_0, arg_setter, _mmct_test_thresh,
    ):

        # NEW_MOCK_X_BIN_1 nan freq is below threshold, all num freq >= threshold
        # NEW_MOCK_X_BIN_2 nan freq is at threshold, all num freq >= threshold

        _NEW_MOCK_X = \
            {'DATA_1': NEW_MOCK_X_BIN_1, 'DATA_2': NEW_MOCK_X_BIN_2}[_DATA]

        # NAN IGNORED
        TRFM_X = arg_setter(
            MOCK_X=_NEW_MOCK_X,
            ignore_nan=_ignore_nan,
            delete_axis_0=_delete_axis_0,
            count_threshold=_mmct_test_thresh // 2
        )[0]


        assert np.array_equiv(
            TRFM_X[np.logical_not(nan_mask_numerical(TRFM_X))],
            _NEW_MOCK_X[np.logical_not(nan_mask_numerical(_NEW_MOCK_X))]
        ), f"bin column non-nans wrongly altered"


        if _ignore_nan is True:
            # NAN < THRESH AND NOTHING DELETED
            # NAN >= THRESH AND NOTHING DELETED
            # delete_axis_0 is irrelevant
            assert len(TRFM_X) == len(_NEW_MOCK_X), \
                f"bin column was altered with ignore_nan=True"
        elif _ignore_nan is False:
            # NAN < THRESH AND SOMETHING DELETED
            if _DATA == 'DATA_1':
                # there is a nuance of MCT here, even if not deleting axis 0 on
                # a bin/handleasbool column, if nans are below thresh they are
                # still deleted!
                # so delete_axis_0 is irrelevant, nans rows are always deleted
                # when nan freq is below thresh
                _num_nan = np.sum(nan_mask(_NEW_MOCK_X))
                assert len(TRFM_X) == len(_NEW_MOCK_X) - _num_nan, \
                    f"bin column was incorrectly altered"

            # NAN >= THRESH AND NOTHING DELETED
            elif _DATA == 'DATA_2':
                # delete_axis_0 is irrelevant, nothing should be deleted
                assert len(TRFM_X) == len(_NEW_MOCK_X), \
                    f"bin column was wrongly altered, shouldnt change"
            else:
                raise Exception(f'algorithm failure')


    # END bin ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    # str ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @staticmethod
    @pytest.fixture(scope='session')
    def NEW_MOCK_X_STR_1(MOCK_X_STR, _mmct_test_rows):
        NEW_MOCK_X_STR = MOCK_X_STR.astype('<U3')
        NAN_MASK = np.random.choice(_mmct_test_rows, 1, replace=False)
        NEW_MOCK_X_STR[NAN_MASK] = 'nan'
        return NEW_MOCK_X_STR


    @staticmethod
    @pytest.fixture(scope='session')
    def NEW_MOCK_X_STR_2(MOCK_X_STR, _mmct_test_rows, _mmct_test_thresh):
        while True:
            NEW_MOCK_X_STR = MOCK_X_STR.copy().astype('<U3')
            NAN_MASK = np.zeros(_mmct_test_rows).astype(bool)
            RANDOM_IDXS = np.random.choice(
                _mmct_test_rows, _mmct_test_thresh // 2 + 1, replace=False
            )
            NAN_MASK[RANDOM_IDXS] = True
            NEW_MOCK_X_STR[NAN_MASK] = 'nan'
            if min(np.unique(NEW_MOCK_X_STR[NEW_MOCK_X_STR != 'nan'],
                             return_counts=True)[1]) >= _mmct_test_thresh // 2:
                del NAN_MASK, RANDOM_IDXS
                break

        return NEW_MOCK_X_STR


    @pytest.mark.parametrize('_DATA', ('DATA_1', 'DATA_2'))
    @pytest.mark.parametrize('_ignore_nan', (True, False))
    def test_str(
        self, NEW_MOCK_X_STR_1, NEW_MOCK_X_STR_2, _ignore_nan, _DATA, arg_setter,
        _mmct_test_thresh, _mmct_test_rows
    ):

        _NEW_MOCK_X = \
            {'DATA_1': NEW_MOCK_X_STR_1, 'DATA_2': NEW_MOCK_X_STR_2}[_DATA]

        # NAN IGNORED
        TRFM_X = arg_setter(
            MOCK_X=_NEW_MOCK_X,
            ignore_nan=_ignore_nan,
            count_threshold=_mmct_test_thresh // 2
        )[0]

        NOT_NAN_MASK = np.logical_not(nan_mask_string(_NEW_MOCK_X))

        if _ignore_nan is True:
            assert len(TRFM_X) == len(_NEW_MOCK_X), \
                f"str column was altered with ignore_nan=True"
            assert np.array_equiv(TRFM_X, _NEW_MOCK_X), \
                f"str column was altered with ignore_nan=True"
        elif _ignore_nan is False:
            if _DATA == 'DATA_1':
                # NAN BELOW THRESH AND ROWS DELETED
                assert np.array_equiv(TRFM_X,
                    _NEW_MOCK_X[NOT_NAN_MASK].reshape((-1, 1))), \
                    f"str column nans not deleted"
            elif _DATA == 'DATA_2':
                # NAN ABOVE THRESH AND NOTHING DELETED
                assert len(TRFM_X) == len(_NEW_MOCK_X), \
                    f"str column was wrongly altered"
                assert np.array_equiv(TRFM_X, _NEW_MOCK_X), \
                    f"str column wrongly altered"

    # END str ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    # nbi ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @staticmethod
    @pytest.fixture(scope='session')
    def NEW_MOCK_X_NBI_1(MOCK_X_NBI, _mmct_test_rows, _mmct_test_thresh):
        # has one nan
        while True:
            NEW_MOCK_X_NBI = MOCK_X_NBI.copy().astype(np.float64)
            NEW_MOCK_X_NBI = NEW_MOCK_X_NBI.ravel()
            NEW_MOCK_X_NBI[np.random.choice(_mmct_test_rows)] = np.nan
            # ensure all unqs besides nans are still above _mmct_test_thresh // 2
            if min(np.unique(
                NEW_MOCK_X_NBI[np.logical_not(nan_mask(NEW_MOCK_X_NBI))],
                return_counts=True
            )[1]) >= _mmct_test_thresh // 2:
                break

        NEW_MOCK_X_NBI = NEW_MOCK_X_NBI.reshape((-1, 1))

        return NEW_MOCK_X_NBI


    @staticmethod
    @pytest.fixture(scope='session')
    def NEW_MOCK_X_NBI_2(MOCK_X_NBI, _mmct_test_rows, _mmct_test_thresh):
        # has _mmct_test_thresh // 2 + 1 nans
        while True:
            NEW_MOCK_X_NBI = MOCK_X_NBI.copy().astype(np.float64)
            NAN_MASK = np.random.choice(
                _mmct_test_rows, _mmct_test_thresh // 2 + 1, replace=False
            )
            NEW_MOCK_X_NBI = NEW_MOCK_X_NBI.ravel()
            NEW_MOCK_X_NBI[NAN_MASK] = np.nan
            # ensure all unqs besides nans are still above _mmct_test_thresh // 2
            if min(np.unique(
                    NEW_MOCK_X_NBI[np.logical_not(nan_mask(NEW_MOCK_X_NBI))],
                    return_counts=True
            )[1]) >= _mmct_test_thresh // 2:
                del NAN_MASK
                break

        NEW_MOCK_X_NBI = NEW_MOCK_X_NBI.reshape((-1, 1))

        return NEW_MOCK_X_NBI


    @pytest.mark.parametrize('_DATA', ('DATA_1', 'DATA_2'))
    @pytest.mark.parametrize('_ignore_nan', (True, False))
    def test_nbi(self, NEW_MOCK_X_NBI_1, NEW_MOCK_X_NBI_2, _DATA, _ignore_nan,
        arg_setter, _mmct_test_thresh
    ):

        _NEW_MOCK_X = \
            {'DATA_1': NEW_MOCK_X_NBI_1, 'DATA_2': NEW_MOCK_X_NBI_2}[_DATA]

        # NAN IGNORED
        TRFM_X = arg_setter(
            MOCK_X=_NEW_MOCK_X.copy(),
            ignore_nan=_ignore_nan,
            ignore_non_binary_integer_columns=False,
            count_threshold=_mmct_test_thresh // 2
        )[0]

        if _ignore_nan:
            assert len(TRFM_X) == len(_NEW_MOCK_X), \
                f"nbi rows were altered with ignore_nan=True"

            assert np.array_equal(TRFM_X, _NEW_MOCK_X, equal_nan=True), \
                f"nbi non-nan rows wrongly altered"

        elif not _ignore_nan:
            if _DATA == 'DATA_1':
                # number of nans less than threshold
                # NAN BELOW THRESH AND nan ROWS DELETED
                assert len(TRFM_X) < len(_NEW_MOCK_X), \
                    f"nbi rows were not altered with ignore_nan=False"

            elif _DATA == 'DATA_2':
                # NAN ABOVE THRESH AND NO NANS DELETED
                assert len(TRFM_X) == len(_NEW_MOCK_X), \
                    f"nbi nan rows wrongly deleted"

    # END nbi ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

# END TestIgnoreNan ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **



class TestHandleAsBool_2:

    @staticmethod
    @pytest.fixture(scope='session')
    def NEW_MOCK_X_BOOL_1(MOCK_X_BOOL, _mmct_test_rows, _mmct_test_thresh):
        NEW_MOCK_X_BOOL = MOCK_X_BOOL.copy().astype(np.float64)
        NAN_MASK = np.random.choice(
            _mmct_test_rows, _mmct_test_thresh // 2 - 1, replace=False
        )
        NEW_MOCK_X_BOOL[NAN_MASK] = np.nan
        return NEW_MOCK_X_BOOL


    @staticmethod
    @pytest.fixture(scope='session')
    def NEW_MOCK_X_BOOL_2(MOCK_X_BOOL, _mmct_test_rows, _mmct_test_thresh):
        NEW_MOCK_X_BOOL = MOCK_X_BOOL.copy().astype(np.float64)
        NAN_MASK = np.random.choice(
            _mmct_test_rows, _mmct_test_thresh, replace=False
        )
        NEW_MOCK_X_BOOL[NAN_MASK] = np.nan
        return NEW_MOCK_X_BOOL


    @staticmethod
    @pytest.fixture(scope='session')
    def NEW_MOCK_X_BOOL_3(MOCK_X_BOOL, _mmct_test_rows, _mmct_test_thresh):
        NEW_MOCK_X_BOOL = MOCK_X_BOOL.copy().astype(np.float64)
        NAN_MASK = np.random.choice(
            _mmct_test_rows, _mmct_test_thresh // 2, replace=False
        )
        NEW_MOCK_X_BOOL[NAN_MASK] = np.nan
        return NEW_MOCK_X_BOOL


    @pytest.mark.parametrize('_DATA, _ignore_nan, _delete_axis_0',
        (
        ('DATA_1', True, True),
        ('DATA_1', False, False),
        ('DATA_1', False, True),
        ('DATA_2', False, False),
        ('DATA_3', False, True)
        )
    )
    def test_bool(self, _DATA, _ignore_nan, _delete_axis_0, _mmct_test_thresh,
        NEW_MOCK_X_BOOL_1, NEW_MOCK_X_BOOL_2, NEW_MOCK_X_BOOL_3, arg_setter
    ):

        _NEW_MOCK_X_BOOL = {'DATA_1':  NEW_MOCK_X_BOOL_1,
            'DATA_2': NEW_MOCK_X_BOOL_2, 'DATA_3': NEW_MOCK_X_BOOL_3}[_DATA]

        TRFM_X = arg_setter(
            MOCK_X=_NEW_MOCK_X_BOOL,
            ignore_nan=_ignore_nan,
            delete_axis_0=_delete_axis_0,
            count_threshold=_mmct_test_thresh // 2
        )[0]

        # universal hands-off non-nans
        assert np.array_equiv(
            TRFM_X[np.logical_not(nan_mask_numerical(TRFM_X))],
            _NEW_MOCK_X_BOOL[
                np.logical_not(nan_mask_numerical(_NEW_MOCK_X_BOOL))
            ]
        ), f"handle_as_bool non-nan rows wrongly deleted"

        # NAN IGNORED
        if _ignore_nan:
            assert len(TRFM_X) == len(_NEW_MOCK_X_BOOL), \
                f"handle_as_bool column was altered with ignore_nan=True"
        elif _ignore_nan is False:

            # NAN BELOW THRESH AND NOTHING DELETED
            # if _DATA == 'DATA_1' and _delete_axis_0 in [True, False]:
            # NAN ABOVE THRESH AND NOTHING DELETED
            # if _DATA == 'DATA_2' and _delete_axis_0 is False:
            # NAN ABOVE THRESH AND ROWS NOT DELETED
            # if _DATA == 'DATA_3' and _delete_axis_0 is True:

            assert len(TRFM_X) == len(_NEW_MOCK_X_BOOL), \
                f"handle_as_bool column was wrongly altered"

            # gets universal non-nan hands-off above


    @staticmethod
    @pytest.fixture(scope='session')
    def NEW_MOCK_X_BIN_1(_mmct_test_rows):
        return np.ones(_mmct_test_rows).astype(np.float64).reshape((-1, 1))


    @pytest.mark.parametrize('_ignore_nan', (True, False))
    @pytest.mark.parametrize('_delete_axis_0', (True, False))
    def test_bin(
        self, NEW_MOCK_X_BIN_1, _ignore_nan, _delete_axis_0, arg_setter,
        _mmct_test_rows, _mmct_test_thresh
    ):

        TRFM_X = arg_setter(
            MOCK_X=NEW_MOCK_X_BIN_1,
            ignore_nan=_ignore_nan,
            delete_axis_0=_delete_axis_0,
            count_threshold=_mmct_test_thresh // 2
        )[0]

        # mmct DELETES A COLUMN WITH ONE UNIQUE
        assert TRFM_X.shape == (_mmct_test_rows, 0), \
            f'mmct did not delete a column of constants; shape = {TRFM_X.shape}'







# ACCURACY TEST
# DEFAULT_ARGS = {
#     'MOCK_X': MOCK_X_STR,
#     'MOCK_Y': MOCK_Y,
#     'ignore_columns': None,
#     'ignore_nan': True,
#     'ignore_non_binary_integer_columns': True,
#     'ignore_float_columns': True,
#     'handle_as_bool': False,
#     'delete_axis_0': False,
#     'count_threshold': _thresh
# }



@pytest.fixture(scope='session')
def MOCK_X_NO_NAN(MOCK_X_BIN, MOCK_X_NBI, MOCK_X_FLT, MOCK_X_STR, MOCK_X_BOOL,
        _mmct_test_rows, _source_len
    ):

    # THIS IS THE LARGE OBJECT THAT HOLDS ALL THE VARIOUS VECTORS, WITH NO nans
    _MOCK_X_NO_NAN = np.empty((_mmct_test_rows, 0), dtype=object)

    # CREATE A COLUMN OF CONSTANTS TO DEMONSTRATE IT IS ALWAYS DELETED
    _MOCK_X_INT = np.ones((_mmct_test_rows, 1)).astype(object)
    # CREATE A COLUMN FOR HANDLE AS BOOL WHERE 0 IS < THRESH
    _MOCK_X_BOOL_2 = np.random.randint(0, _source_len, (_mmct_test_rows, 1))
    _MOCK_X_BOOL_2[np.random.choice(_mmct_test_rows, 2, replace=False), 0] = 0

    for X in [MOCK_X_BIN, MOCK_X_NBI, MOCK_X_FLT, MOCK_X_STR, MOCK_X_BOOL,
              _MOCK_X_BOOL_2, _MOCK_X_INT]:

        _MOCK_X_NO_NAN = np.hstack(
            (_MOCK_X_NO_NAN.astype(object), X.astype(object))
        )

    return _MOCK_X_NO_NAN


@pytest.fixture(scope='session')
def MOCK_X_NAN(MOCK_X_NO_NAN):
    # THIS IS THE LARGE OBJECT THAT HOLDS ALL THE VARIOUS VECTORS, WITH nans
    _MOCK_X_NAN = MOCK_X_NO_NAN.copy()
    for _ in range(MOCK_X_NO_NAN.size // 10):
        _row_coor = np.random.randint(0, MOCK_X_NO_NAN.shape[0])
        _col_coor = np.random.randint(0, MOCK_X_NO_NAN.shape[1])
        _MOCK_X_NAN[_row_coor, _col_coor] = np.nan

    del _row_coor, _col_coor
    return _MOCK_X_NAN


@pytest.mark.parametrize('_has_nan', (True, False))
@pytest.mark.parametrize('_ignore_columns', (None, (0, 3)))
@pytest.mark.parametrize('_ignore_nan', (True, False))
@pytest.mark.parametrize('_ignore_non_binary_integer_columns', (True, False))
@pytest.mark.parametrize('_ignore_float_columns', (True, False))
@pytest.mark.parametrize('_handle_as_bool', (None, )) # (1, 4, 5)))
@pytest.mark.parametrize('_delete_axis_0', (False,)) # (True, False))
@pytest.mark.parametrize('_ct_trial', ('_ct_1', '_ct_2', '_ct_3'))
def test_accuracy(
    MOCK_X_NO_NAN, MOCK_X_NAN, _has_nan, _ignore_columns, _mmct_test_thresh,
    _ignore_nan, _ignore_non_binary_integer_columns, _ignore_float_columns,
    _handle_as_bool, _delete_axis_0, _ct_trial, arg_setter
):

    MOCK_X = MOCK_X_NAN if _has_nan else MOCK_X_NO_NAN
    REF_X = MOCK_X_NAN if _has_nan else MOCK_X_NO_NAN

    _count_threshold = {
        '_ct_1': _mmct_test_thresh // 2,
        '_ct_2': _mmct_test_thresh,
        '_ct_3': 2 * _mmct_test_thresh
    }[_ct_trial]

    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
    # MAKE REF_X

    # get the uniques and counts for each column -- -- -- -- -- -- -- --
    TEST_UNQS_CTS = []
    for c_idx in range(MOCK_X.shape[1]):
        # MOCK_X may or may not have nans

        _COLUMN_OF_X = MOCK_X[:, c_idx]

        NAN_MASK = nan_mask(_COLUMN_OF_X)
        NOT_NAN_MASK = np.logical_not(NAN_MASK)

        UNIQUES, COUNTS = np.unique(
            _COLUMN_OF_X[NOT_NAN_MASK], return_counts=True
        )

        if any(NAN_MASK):
            UNIQUES = np.insert(UNIQUES, -1, np.nan, axis=0)
            COUNTS = np.insert(COUNTS, -1, np.sum(NAN_MASK), axis=0)

        TEST_UNQS_CTS.append((UNIQUES, COUNTS))
    # END get the uniques and counts for each column -- -- -- -- -- --

    # use TEST_UNQS_CTS to build DTYPES vector and unq_ct_dict
    unq_ct_dict = {}
    _DTYPES = [None for _ in TEST_UNQS_CTS]
    for c_idx, (UNQS, CTS) in enumerate(TEST_UNQS_CTS):

        # determine if column is bin-int, int, float, or obj
        try:
            # if excepts on any of these, is a str
            _UNQS_NO_NAN = UNQS[
                np.logical_not(nan_mask_numerical(UNQS.astype(np.float64)))
            ]
            _UNQS_NO_NAN_AS_INT = \
                _UNQS_NO_NAN.astype(np.float64).astype(np.int32)
            _UNQS_NO_NAN_AS_FLT = _UNQS_NO_NAN.astype(np.float64)

            # if only one number, is constant regardless of bin-int, int, flt
            if len(_UNQS_NO_NAN) == 0:
                raise Exception(f'algorith failure, len(NO NAN UNIQUES)==0')
            elif len(_UNQS_NO_NAN) == 1:
                _DTYPES[c_idx] = 'constant'
            # determine if is int or float
            elif np.array_equiv(_UNQS_NO_NAN_AS_INT, _UNQS_NO_NAN_AS_FLT):
                # if is integer with 2 unq values
                if len(_UNQS_NO_NAN) == 2:
                    _DTYPES[c_idx] = 'bin_int'
                # if is integer with 3+ unq values
                else:
                    _DTYPES[c_idx] = 'int'
            else:
                # if is float with 2+ unq values
                _DTYPES[c_idx] = 'float'

        except:
            _UNQS_NO_NAN = UNQS[np.logical_not(nan_mask_string(UNQS))]
            if len(_UNQS_NO_NAN) == 1:
                _DTYPES[c_idx] = 'constant'
            else:
                _DTYPES[c_idx] = 'obj'

        # if ignored, dont put a column unq_ct_dict into the full unq_ct_dict
        if _ignore_columns and c_idx in _ignore_columns:
            continue
        elif _DTYPES[c_idx] == 'float' and _ignore_float_columns:
            continue
        elif _DTYPES[c_idx] == 'int' and _ignore_non_binary_integer_columns:
            continue

        unq_ct_dict[int(c_idx)] = dict((zip(UNQS, CTS)))

    try:
        del _UNQS_NO_NAN
        del _UNQS_NO_NAN_AS_INT
        del _UNQS_NO_NAN_AS_FLT
    except:
        pass


    # determine what columns will be deleted:
    # 1) has only one unique from the start (a column of constants)
    # 2) is reduced to one unique by removal of other low freq uniques
    DELETE_DICT = {}
    for c_idx in deepcopy(unq_ct_dict).keys():
        DELETE_DICT[int(c_idx)] = []

        # manage nans (whether ignoring or not)
        # life is so much easier when we remove any nan & ct from the start!
        # make a new working column wip_unq_ct_dict that has no nans!
        # if ignoring nans, just wont put them back in later!
        col_wip_unq_ct_dict = {}
        _nan_symbol = None
        _nan_ct = 0
        for unq, ct in deepcopy(unq_ct_dict[c_idx]).items():
            if str(unq).lower() == 'nan':
                if _nan_symbol is not None:
                    raise Exception(f"multiple nan-types in MOCK_X[{c_idx}]")
                _nan_symbol = unq
                _nan_ct = ct
            else:
                col_wip_unq_ct_dict[unq] = ct
        # END make working col unq_ct_dict * * * * * * * * *

        if _DTYPES[c_idx] == 'constant':
            DELETE_DICT[c_idx].append(f'DELETE COLUMN')
        elif (_DTYPES[c_idx] == 'bin_int') or \
                (_handle_as_bool and c_idx in _handle_as_bool):

            if _DTYPES[c_idx] not in ['bin_int', 'int', 'float']:
                raise Exception(
                    f'trying to do handle_as_bool a {_DTYPES[c_idx]} column'
                )

            NEW_DICT = {int(0): 0, int(1): 0}
            UNQS_MIGHT_BE_DELETED = []
            for unq, ct in col_wip_unq_ct_dict.items():

                if str(unq).lower() == 'nan':
                    raise Exception

                if unq == 0:
                    NEW_DICT[int(0)] += ct
                else:
                    UNQS_MIGHT_BE_DELETED.append(unq)
                    NEW_DICT[int(1)] += ct

            assert np.array_equal(
                sorted(list(NEW_DICT.keys())),
                [0,1]
            )

            _delete_column = False
            for unq, ct in NEW_DICT.items():
                if ct < _count_threshold:
                    _delete_column = True
                    if _delete_axis_0:
                        if int(unq) == 0:
                            DELETE_DICT[int(c_idx)].append(int(0))
                        elif int(unq) == 1:
                            DELETE_DICT[int(c_idx)] += UNQS_MIGHT_BE_DELETED
                        else:
                            raise Exception(
                                f"logic handling handle_as_bool dict failed"
                            )

            del unq, ct, UNQS_MIGHT_BE_DELETED, NEW_DICT

            # deal with nan for a bin-int or handle as bool column
            if _nan_ct and not _ignore_nan and _nan_ct < _count_threshold:
                if not _delete_axis_0:
                    if _delete_column:
                        pass # if deleting column, dont delete nan rows!
                    elif not _delete_column:
                        DELETE_DICT[c_idx].append(_nan_symbol)
                elif _delete_axis_0:
                    DELETE_DICT[c_idx].append(_nan_symbol)

            if _delete_column:
                DELETE_DICT[int(c_idx)].append(f'DELETE COLUMN')

            del _delete_column

        else:

            if _DTYPES[c_idx] not in ['int', 'float', 'obj']:
                raise Exception(
                    f'{_DTYPES[c_idx]} column, when should only be a int, '
                    f'float, or obj'
                )

            if _handle_as_bool:
                assert c_idx not in _handle_as_bool

            for unq, ct in col_wip_unq_ct_dict.items():

                if str(unq).lower() == 'nan':
                    raise Exception

                if ct < _count_threshold:
                    DELETE_DICT[c_idx].append(unq)

            # before putting nan back in, determine the number of uniques
            # being kept, if only 1 or less non-nan unique, delete column
            _delete_column = \
                (len(col_wip_unq_ct_dict) - len(DELETE_DICT[c_idx]) <= 1)

            if not _ignore_nan and _nan_ct and _nan_ct < _count_threshold:
                DELETE_DICT[c_idx].append(_nan_symbol)

            if _delete_column:
                DELETE_DICT[c_idx].append(f'DELETE COLUMN')

            del _delete_column

        # if there are no delete instructions for a column, then remove
        # the empty list from DELETE_DICT
        if len(DELETE_DICT[c_idx]) == 0:
            del DELETE_DICT[c_idx]


    # perform the instructions in DELETE_DICT on the columns, in reverse
    # order
    for c_idx in reversed(sorted(DELETE_DICT)):

        if sum([__ == 'DELETE COLUMN' for __ in DELETE_DICT[c_idx]]) > 1:
            raise Exception(f"more than on DELETE COLUMN in DELETE_DICT")

        if 'DELETE COLUMN' in DELETE_DICT[c_idx] and \
            DELETE_DICT[c_idx][-1] != 'DELETE COLUMN':
            raise ValueError(
                f"'DELETE COLUMN' is in DELETE_DICT[{c_idx}] but not in "
                f"the last position"
            )

        _delete_column = (DELETE_DICT[c_idx][-1] == 'DELETE COLUMN')
        if _delete_column:
            # extract only the uniques to delete
            DELETE_DICT[c_idx].remove('DELETE COLUMN')

        # if the there are no uniques to delete, but deleting column
        # just delete the column now and skip the rest
        if _delete_column and len(DELETE_DICT[c_idx]) == 0:
            REF_X = np.delete(REF_X, c_idx, axis=1)
            continue

        # but if there are uniques to delete
        ROW_MASK = np.zeros(REF_X.shape[0]).astype(np.uint8)
        for _op in DELETE_DICT[c_idx]:
            if str(_op).lower() == 'nan':
                ROW_MASK += nan_mask(REF_X[:, c_idx]).astype(np.uint8)
            else:
                ROW_MASK += (REF_X[:, c_idx] == _op).astype(np.uint8)

        if (ROW_MASK > 1).any():
            raise Exception(f"more than one unique hit on one row")

        REF_X = REF_X[np.logical_not(ROW_MASK), :]
        del ROW_MASK

        if _delete_column:
            REF_X = np.delete(REF_X, c_idx, axis=1)

    # END MAKE REF_X
    # # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

    TRFM_X = arg_setter(
        MOCK_X=MOCK_X,
        ignore_columns=_ignore_columns,
        ignore_nan=_ignore_nan,
        ignore_non_binary_integer_columns=_ignore_non_binary_integer_columns,
        ignore_float_columns=_ignore_float_columns,
        handle_as_bool=_handle_as_bool,
        delete_axis_0=_delete_axis_0,
        count_threshold=_count_threshold
    )[0]


    assert np.array_equiv(
        TRFM_X[np.logical_not(nan_mask(TRFM_X))],
        REF_X[np.logical_not(nan_mask(REF_X))]
    ), (f'TRFM_X shape = {TRFM_X.shape}: \n{TRFM_X}\n\n'
        f'REF_X.shape = {REF_X.shape}: \n{REF_X}\n')





