# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd

from pybear.preprocessing._MinCountTransformer._partial_fit._tcbc_merger import \
    _tcbc_merger

from pybear.utilities._nan_masking import nan_mask



class TestTCBCMergerTest:

    # FIXTURES * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

    @staticmethod
    @pytest.fixture(scope='module')
    def _tcbc():
        return {
            0: {0: 10, 1: 5, 2: 8, 3: 15, np.nan: 3},
            1: {0: 5, 1: 7, 2: 3, 3: 2, 'nan': 5}
        }


    @staticmethod
    @pytest.fixture(scope='module')
    def _tcbc_no_nan():
        return {
            0: {0: 10, 1: 5, 2: 8, 3: 15},
            1: {0: 5, 1: 7, 2: 3, 3: 2}
        }


    @staticmethod
    @pytest.fixture(scope='module')
    def _tcbc_multiple_nan():
        return {
            0: {'nan': 10, 'NAN': 5, 'a': 8, 'b': 15},
            1: {0: 5, 1: 7, np.nan: 3, pd.NA: 2}
        }


    @staticmethod
    @pytest.fixture(scope='module')
    def _unqs_cts_tuples_multiple_nan():
        return [
            ('str', {'c': 10, 'd': 5, 'nan': 8, 'NaN': 15}),
            ('float', {0: 5, 1: 7, np.nan: 4, pd.NA: 2})
        ]

    # END FIXTURES * * * * * * * * * * * * * * * * * * * * * * * * * * *


    def test_catches_multiple_nan_in_tcbc(self, _tcbc_multiple_nan):

        # str column
        with pytest.raises(ValueError):
            _tcbc_merger(
                _DTYPE_UNQS_CTS_TUPLES=[('obj', {'c':5, 'd':8})],
                _tcbc={0: _tcbc_multiple_nan[0]}
            )

        # float column
        with pytest.raises(ValueError):
            _tcbc_merger(
                _DTYPE_UNQS_CTS_TUPLES=[('float', {2:15, 3:2})],
                _tcbc={0: _tcbc_multiple_nan[1]}
            )


    def test_catches_multiple_nan_in_unqct(
        self, _unqs_cts_tuples_multiple_nan, _tcbc_no_nan
    ):

        _unqct = _unqs_cts_tuples_multiple_nan

        # str column
        with pytest.raises(ValueError):
            _tcbc_merger(
                _DTYPE_UNQS_CTS_TUPLES=[_unqct[0], _unqct[0]],
                _tcbc=_tcbc_no_nan
            )

        # float column
        with pytest.raises(ValueError):
            _tcbc_merger(
                _DTYPE_UNQS_CTS_TUPLES=[_unqct[1], _unqct[1]],
                _tcbc=_tcbc_no_nan
            )


    def test_correctly_doubles_values_no_nans(self, _tcbc_no_nan):

        out = _tcbc_merger(
            _DTYPE_UNQS_CTS_TUPLES=[('int', v) for k,v in _tcbc_no_nan.items()],
            _tcbc=_tcbc_no_nan
        )

        assert np.array_equal(list(out.keys()), list(_tcbc_no_nan.keys()))

        for _c_idx in out:
            assert np.array_equal(
                list(out[_c_idx].keys()),
                list(_tcbc_no_nan[_c_idx].keys())
            )
            for _unq in out[_c_idx]:
                assert out[_c_idx][_unq] == 2 * _tcbc_no_nan[_c_idx][_unq]


    def test_correctly_doubles_values_with_nans(self, _tcbc):

        out = _tcbc_merger(
            _DTYPE_UNQS_CTS_TUPLES=[('int', v) for k,v in _tcbc.items()],
            _tcbc=_tcbc
        )

        assert np.array_equal(list(out.keys()), list(_tcbc.keys()))

        for _c_idx in out:
            _out_keys = np.fromiter(out[_c_idx], dtype=object)
            _tcbc_keys = np.fromiter(out[_c_idx], dtype=object)
            assert np.array_equal(
                _out_keys[np.logical_not(nan_mask(_out_keys))],
                _tcbc_keys[np.logical_not(nan_mask(_tcbc_keys))]
            )
            for _unq in _out_keys:
                assert out[_c_idx][_unq] == 2 * _tcbc[_c_idx][_unq]


    def test_correctly_fills_empty_old_tcbc(self, _tcbc_no_nan, _tcbc):

        # no nans - - - - - - - - - - - - - - - - - - - - - - - - - - -
        _new_unqs_cts_1 = [
            ('float', _tcbc_no_nan[0]), ('float', _tcbc_no_nan[1])
        ]

        out = _tcbc_merger(
            _DTYPE_UNQS_CTS_TUPLES=_new_unqs_cts_1, _tcbc={0: {}, 1: {}}
        )

        assert out == _tcbc_no_nan
        # END no nans - - - - - - - - - - - - - - - - - - - - - - - - -


        # nans - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        _new_unqs_cts_2 = [
            ('obj', _tcbc[0]), ('float', _tcbc[1])
        ]

        out = _tcbc_merger(
            _DTYPE_UNQS_CTS_TUPLES=_new_unqs_cts_2, _tcbc={0: {}, 1: {}}
        )

        assert out == _tcbc

        # END nans - - - - - - - - - - - - - - - - - - - - - - - - - - -




