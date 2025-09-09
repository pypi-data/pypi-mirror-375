# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.preprocessing._SlimPolyFeatures._partial_fit._is_constant import \
    _is_constant

from pybear.utilities import nan_mask_numerical

import uuid

import numpy as np

import pytest




class TestParallelConstantFinder:


    @pytest.mark.parametrize('has_nan', (True, False))
    @pytest.mark.parametrize('equal_nan', (True, False))
    @pytest.mark.parametrize('rtol, atol', ((1e-7, 1e-8), (1e-1, 1e-2)))
    def test_accuracy(self, has_nan, equal_nan, rtol, atol):

        # Methodology
        # _is_constant will only ever see numpy arrays.
        # put a level of noise in the data that in one case is less
        # that rtol/atol, so that the column is considered constant; in
        # the other case the column is not constant because the noise
        # is greater than rtol/atol.

        _noise = 1e-6
        _size = 100

        _X = np.random.normal(loc=1, scale=_noise, size=(_size,))

        if has_nan:
            _rand_idxs = \
                np.random.choice(range(_size), _size//10, replace=False)
            _X[_rand_idxs] = np.nan


        out = _is_constant(_X, equal_nan, rtol, atol)

        if has_nan:
            if equal_nan:
                if _noise <= atol:
                    _not_nan_mask = np.logical_not(nan_mask_numerical(_X))
                    assert out == np.mean(_X[_not_nan_mask])
                elif _noise > atol:
                    assert isinstance(out, uuid.UUID)
            elif not equal_nan:
                assert isinstance(out, uuid.UUID)
        elif not has_nan:
            # equal_nan doesnt matter
            if _noise <= atol:
                assert out == np.mean(_X)
            elif _noise > atol:
                assert isinstance(out, uuid.UUID)


    @pytest.mark.parametrize('equal_nan', (True, False))
    def test_all_nans(self, equal_nan):

        # Methodology
        # need to test two different data types, numbers and strings
        # that are all nans

        _size = 100

        _X = np.full((_size,), np.nan)

        out = _is_constant(_X, equal_nan, 1e-5, 1e-8)

        if equal_nan:
            assert str(out) == 'nan'
        elif not equal_nan:
            assert isinstance(out, uuid.UUID)














