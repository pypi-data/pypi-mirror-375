# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import itertools

import numpy as np

from pybear.preprocessing._SlimPolyFeatures._partial_fit. \
    _parallel_chunk_comparer import _parallel_chunk_comparer



class TestChunkComparer:


    # np cant be int if using nans
    @pytest.mark.parametrize('_has_nan', (True, False))
    @pytest.mark.parametrize('_equal_nan', (True, False))
    def test_accuracy(
        self, _X_factory, _shape, _has_nan, _equal_nan
    ):

        # we know that _parallel_column_comparer works from its own tests.
        # rig 2 chunks to have some identical columns, then see if
        # _chunk_comparer finds them

        # need to rig some constants for _X_factory
        # get some random indices that will be equal
        _rand_idxs = np.random.choice(
            list(range(_shape[1])), (3, ), replace=False
        ).tolist()

        # set what the value in those columns will be
        _constants = {i: np.e for i in _rand_idxs}

        _X1 = _X_factory(
            _dupl=None,
            _format='np',
            _dtype='flt',
            _has_nan=_has_nan,
            _columns=None,
            _constants=_constants,
            _shape=_shape
        )

        _X2 = _X_factory(
            _dupl=None,
            _format='np',
            _dtype='flt',
            _has_nan=_has_nan,
            _columns=None,
            _constants=_constants,
            _shape=_shape
        )

        # output should be every permutation of the indices of the equal
        # columns like [(0, 1), (0, 2), (1, 2)] if 0, 1, & 2 are equal

        out = _parallel_chunk_comparer(
            _chunk1=_X1,
            _chunk1_X_indices=tuple((i,) for i in tuple(range(_shape[1]))),
            _chunk2=_X2,
            _chunk2_X_indices=tuple((j,) for j in tuple(range(_shape[1]))),
            _rtol=1e-5,
            _atol=1e-8,
            _equal_nan=_equal_nan
        )

        assert isinstance(out, list)

        # the out of _chunk_comparer is not sorted. that doesnt happen
        # until after union-find... wherever that is happening
        out = sorted(list(map(tuple, map(sorted, out))))


        if not _has_nan or (_has_nan and _equal_nan):

            assert all(map(isinstance, out, (tuple for i in out)))

            _tuple_rand_idxs = [(k,) for k in _rand_idxs]

            _exp = list(itertools.combinations(_tuple_rand_idxs, 2))
            _exp = sorted(list(map(tuple, map(sorted, _exp))))

            assert len(out) == len(_exp)
            for _combo in list(_exp):
                assert _combo in out
        else:
            # if has nans
            assert len(out) == 0





