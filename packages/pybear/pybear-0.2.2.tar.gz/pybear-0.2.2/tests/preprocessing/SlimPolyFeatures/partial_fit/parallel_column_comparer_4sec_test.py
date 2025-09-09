# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.preprocessing._SlimPolyFeatures._partial_fit. \
    _parallel_column_comparer import _parallel_column_comparer



class TestColumnComparer:


    # np cant be int if using nans
    # this cant take str/obj. non-num X is blocked by validate_data anyway.
    @pytest.mark.parametrize('_has_nan', (True, False))
    @pytest.mark.parametrize('_equal_nan', (True, False))
    def test_accuracy(
        self, _X_factory, _has_nan, _equal_nan, _shape
    ):

        # a sneaky trick here. _X_factory peppers nans after propagating
        # duplicates. which means nans are likely to be different on every
        # column. so if create a 2 column array and both columns are the
        # same, then both will be identical except for the nans.

        _shape = (100, 2)

        _X_flt = _X_factory(
            _dupl=[[0,1]],
            _format='np',
            _dtype='flt',
            _has_nan=_has_nan,
            _columns=None,
            _zeros=0.33,
            _shape=_shape
        )

        _X1 = _X_flt[:, [0]]

        _X2 = _X_flt[:, [1]]


        _are_equal = _parallel_column_comparer(
            _X1, _X2, _rtol=1e-5, _atol=1e-8, _equal_nan=_equal_nan
        )


        if _equal_nan or not _has_nan:
            assert _are_equal
        elif not _equal_nan:
            assert not _are_equal





