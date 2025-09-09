# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.preprocessing._MinCountTransformer._transform. \
    _make_row_and_column_masks import _make_row_and_column_masks



# ROW_KEEP_MASK, COLUMN_KEEP_MASK = _make_row_and_column_masks(
#     _X: InternalXContainer,
#     _total_counts_by_column: TotalCountsByColumnType,
#     _delete_instr: InstructionsType,
#     _reject_unseen_values: bool
# ) -> tuple[npt.NDArray[bool], npt.NDArray[bool]]:


class TestMakeRowAndColumnMasks:

    # accuracy of row masks is tested in test_parallelized_row_masks


    # fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    @staticmethod
    @pytest.fixture
    def _pool_size(_shape):
        return _shape[0] // 4


    @staticmethod
    @pytest.fixture
    def _thresh(_shape, _pool_size):
        return _shape[0] // _pool_size


    @staticmethod
    @pytest.fixture
    def float_column_no_nan(_pool_size, _shape):
        np.random.seed(14)
        return np.random.randint(0, _pool_size, (_shape[0], 1)).astype(np.float64)


    @staticmethod
    @pytest.fixture
    def float_column_nan(float_column_no_nan, _shape, _thresh):
        np.random.seed(14)
        NAN_MASK = np.random.choice(
            np.arange(_shape[0]), int(_thresh-1), replace=False
        )
        float_column_nan = float_column_no_nan.copy()
        float_column_nan[NAN_MASK, 0] = np.nan

        return float_column_nan


    @staticmethod
    @pytest.fixture
    def str_column_no_nan(_pool_size, _shape):
        np.random.seed(14)
        alpha = 'abcdefghijklmnopqrstuvwxyz'

        pool = list(alpha + alpha.upper())[:_pool_size]
        return np.random.choice(pool, _shape[0], replace=True).reshape((-1,1))


    @staticmethod
    @pytest.fixture
    def str_column_nan(str_column_no_nan, _shape, _thresh):
        np.random.seed(14)
        NAN_MASK = np.random.choice(
            np.arange(_shape[0]), int(_thresh-1), replace=False
        )
        str_column_nan = str_column_no_nan.copy().astype('<U3')
        str_column_nan[NAN_MASK, 0] = 'nan'
        return str_column_nan


    @staticmethod
    @pytest.fixture
    def good_tcbc():

        def foo(any_array_of_columns):

            TCBC = {}
            for _idx, _column in enumerate(any_array_of_columns.transpose()):
                UNIQUES, COUNTS = np.unique(_column, return_counts=True)
                TCBC[_idx] = dict((zip(UNIQUES, list(map(int, COUNTS)))))
            del UNIQUES, COUNTS
            return TCBC

        return foo


    @staticmethod
    @pytest.fixture
    def good_instr():

        def foo(any_tcbc, _thresh):

            _INSTR: dict[int, list[str, int, float]]

            _INSTR = {}
            for col_idx, column_unq_ct_dict in any_tcbc.items():

                _INSTR[col_idx] = []
                _UNQS = np.fromiter(column_unq_ct_dict.keys(), dtype=object)
                _CTS = np.fromiter(column_unq_ct_dict.values(), dtype=np.uint32)

                if np.all((_CTS < _thresh)):
                    _INSTR[col_idx].append('DELETE ALL')
                else:
                    _INSTR[col_idx] += _UNQS[(_CTS < _thresh)].tolist()

                del _UNQS, _CTS

                if 'DELETE ALL' in _INSTR[col_idx] \
                        or len(_INSTR[col_idx]) >= len(column_unq_ct_dict) - 1:
                    _INSTR[col_idx].append('DELETE COLUMN')

            return _INSTR

        return foo

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    @pytest.mark.parametrize('reject_unseen', (True, False))
    def test_accuracy_column_masks(self, float_column_no_nan, str_column_no_nan,
        str_column_nan, float_column_nan, good_tcbc, good_instr, _thresh,
        reject_unseen):

        AVAIL = (
            float_column_no_nan, str_column_no_nan, str_column_nan,
            float_column_nan
        )

        _good_test_was_run = 0

        for _trial in range(5):

            # build tests fixtures ** * ** * ** * ** * ** * ** * ** * **
            X = AVAIL[np.random.randint(len(AVAIL))]
            for _column in range(5):
                X = np.hstack((X, AVAIL[np.random.randint(len(AVAIL))]))

            TCBC = good_tcbc(X)
            _good_instr = good_instr(TCBC, _thresh)
            for col_idx in _good_instr:
                assert len(_good_instr[col_idx]) > 0, \
                    f"if this excepts, it wants to keep all unqs"
            # END build tests fixtures ** * ** * ** * ** * ** * ** * **

            # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
            # derive expected COLUMN_KEEP_MASK and ROW_KEEP_MASK from
            # fixtures. do this before running _make_row_and_column_masks.
            # if all rows or columns were to be deleted,
            # _make_row_and_column_masks will except, wrecking the tests.
            # if these conditions are found in expected, tests
            # _make_row_and_column_masks raises ValueError.

            exp = np.zeros(X.shape[1], dtype=np.uint8)

            for col_idx in TCBC:
                __ = TCBC[col_idx]
                TCBC[int(col_idx)] = dict((
                    zip(map(str, __.keys()), map(int, __.values()))
                ))

            _mock_instr = {}
            _DELETE_ROW_MASK = np.zeros(X.shape[0])
            for col_idx, UNQ_CT_DICT in TCBC.items():
                _mock_instr[col_idx] = []
                for unq, ct in UNQ_CT_DICT.items():
                    if ct < _thresh:
                        _mock_instr[col_idx].append(unq)
                        UNQ_MASK = X[:, col_idx] == unq
                        if np.sum(UNQ_MASK) == 0:
                            UNQ_MASK = X[:, col_idx].astype(str) == str(unq)
                        assert np.sum(UNQ_MASK) > 0

                        _DELETE_ROW_MASK += UNQ_MASK

                        del UNQ_MASK

                if len(_mock_instr[col_idx]) == len(UNQ_CT_DICT):
                    _mock_instr[col_idx].append('DELETE ALL')

                if len(_mock_instr[col_idx]) >= len(UNQ_CT_DICT) - 1:
                    _mock_instr[col_idx].append('DELETE COLUMN')
                else:
                    # if 'DELETE COLUMN' not in, keeping column,
                    # KEEP MASK gets a 1
                    exp[col_idx] = 1

            if all(['DELETE COLUMN' in j for j in _mock_instr.values()]):

                with pytest.raises(ValueError):
                    _make_row_and_column_masks(
                        X,
                        TCBC,
                        _good_instr,
                        reject_unseen
                    )
            elif np.all(_DELETE_ROW_MASK):

                with pytest.raises(ValueError):
                    _make_row_and_column_masks(
                        X,
                        TCBC,
                        _good_instr,
                        reject_unseen
                    )

            else:

                _good_test_was_run += 1

                ROW_KEEP_MASK, COLUMN_KEEP_MASK = _make_row_and_column_masks(
                    X,
                    TCBC,
                    _good_instr,
                    reject_unseen
                )

                assert np.array_equiv(COLUMN_KEEP_MASK, exp.astype(bool))

        # ensure a test that actually tests accuracy was run
        assert _good_test_was_run > 0
        # END ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    def test_sees_nans(self, _thresh, _shape, good_tcbc, good_instr):


        RIGGED_FLOAT_COL = \
            np.random.randint(1, _shape[0]//_thresh, size=(_shape[0] - (_thresh - 1), 1))
        RIGGED_FLOAT_COL = RIGGED_FLOAT_COL.astype(np.float64)

        MASK = np.random.choice(
            list(range(_shape[0] - (_thresh - 1))),
            _thresh - 1,
            replace=False
        )

        RIGGED_FLOAT_COL[MASK] = np.nan

        del MASK

        RIGGED_FLOAT_COL = \
            np.vstack((RIGGED_FLOAT_COL, np.full((_thresh - 1, 1), 2.5)))

        TCBC = good_tcbc(RIGGED_FLOAT_COL)
        _good_instr = good_instr(TCBC, _thresh)

        ROW_KEEP_MASK, COLUMN_KEEP_MASK = _make_row_and_column_masks(
            RIGGED_FLOAT_COL,
            TCBC,
            _good_instr,
            _reject_unseen_values=True
        )

        # nan IS BELOW THRESH SO SHOULD BE FOUND AND MARKED

        KEPT = RIGGED_FLOAT_COL.ravel()[ROW_KEEP_MASK]

        assert np.nan not in KEPT
        assert 'nan' not in KEPT

        assert 2.5 not in KEPT


    def test_row_mask_making_handles_no_rows_to_delete(
        self, _thresh, good_tcbc, good_instr
    ):

        X = np.vstack((
            np.full((2*_thresh, 10), 3).astype(np.float64),
            np.full((2*_thresh, 10), 4).astype(np.float64),
            np.full((2*_thresh, 10), 5).astype(np.float64)
        ))

        TCBC = good_tcbc(X)
        _good_instr = good_instr(TCBC, _thresh)

        ROW_KEEP_MASK, COLUMN_KEEP_MASK = _make_row_and_column_masks(
            X,
            TCBC,
            _good_instr,
            _reject_unseen_values=True
        )

        assert np.array_equiv(
            ROW_KEEP_MASK.ravel(),
            np.ones(X.shape[0]).ravel().astype(bool)
        )

        assert np.array_equiv(
            COLUMN_KEEP_MASK.ravel(),
            np.ones(X.shape[1]).ravel().astype(bool)
        )





