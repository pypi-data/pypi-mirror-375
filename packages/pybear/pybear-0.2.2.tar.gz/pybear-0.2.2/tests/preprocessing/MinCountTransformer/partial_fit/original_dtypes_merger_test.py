# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.preprocessing._MinCountTransformer._partial_fit._original_dtypes_merger \
    import _original_dtypes_merger



class TestOriginalDtypesMerger:


    # def _original_dtypes_merger(
    #     _col_dtypes: OriginalDtypesType,
    #     _previous_col_dtypes: OriginalDtypesType | None,
    #     _n_features_in: int
    # ) -> OriginalDtypesType:


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    @pytest.mark.parametrize('length_mismatch',
        ((1, 10), (10, 1), (5, 6), (6, 5))
    )
    def test_rejects_different_length(self, length_mismatch):

        _allowed = ['obj', 'float', 'int', 'bin_int']

        with pytest.raises(ValueError):
            _original_dtypes_merger(
                np.random.choice(_allowed, length_mismatch[0]),
                np.random.choice(_allowed, length_mismatch[1]),
                _n_features_in=length_mismatch[0]
            )

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    _dtypes = ['obj', 'float', 'int', 'bin_int']
    @pytest.mark.parametrize('_col_dtypes',
        (list(_dtypes), tuple(_dtypes), set(_dtypes), np.array(_dtypes))
    )
    def test_previous_col_dtypes_None(self, _col_dtypes):

        out = _original_dtypes_merger(
            _col_dtypes,
            None,
            _n_features_in=4
        )

        assert isinstance(out, np.ndarray)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(
            out,
            list(_col_dtypes)
        )

    del _dtypes


    def test_accuracy(self):

        # -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # same stays same
        out = _original_dtypes_merger(
            ['obj', 'float', 'int', 'bin_int'],
            ['obj', 'float', 'int', 'bin_int'],
            _n_features_in=4
        )

        assert isinstance(out, np.ndarray)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(
            out,
            ['obj', 'float', 'int', 'bin_int']
        )
        # -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # obj & float supercede
        out = _original_dtypes_merger(
            ['float', 'bin_int', 'int', 'bin_int'],
            ['obj', 'float', 'obj', 'float'],
            _n_features_in=4
        )

        assert isinstance(out, np.ndarray)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(
            out,
            ['obj', 'float', 'obj', 'float']
        )
        # -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # obj & float supercede
        out = _original_dtypes_merger(
            ['bin_int', 'int', 'float', 'obj'],
            ['obj', 'float', 'int', 'bin_int'],
            _n_features_in=4
        )

        assert isinstance(out, np.ndarray)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(
            out,
            ['obj', 'float', 'float', 'obj']
        )
        # -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # obj supercedes all
        out = _original_dtypes_merger(
            ['obj', 'float', 'obj', 'bin_int'],
            ['bin_int', 'obj', 'int', 'obj'],
            _n_features_in=4
        )

        assert isinstance(out, np.ndarray)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(
            out,
            ['obj', 'obj', 'obj', 'obj']
        )
        # -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # int & bin_int superceded
        out = _original_dtypes_merger(
            ['float', 'int', 'float', 'bin_int'],
            ['int', 'bin_int', 'bin_int', 'bin_int'],
            _n_features_in=4
        )

        assert isinstance(out, np.ndarray)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(
            out,
            ['float', 'int', 'float', 'bin_int']
        )
        # -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # int supercedes bin_int
        out = _original_dtypes_merger(
            ['int', 'bin_int', 'int', 'bin_int'],
            ['bin_int', 'int', 'bin_int', 'int'],
            _n_features_in=4
        )

        assert isinstance(out, np.ndarray)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(
            out,
            ['int', 'int', 'int', 'int']
        )
        # -- -- -- -- -- -- -- -- -- -- -- -- -- --




