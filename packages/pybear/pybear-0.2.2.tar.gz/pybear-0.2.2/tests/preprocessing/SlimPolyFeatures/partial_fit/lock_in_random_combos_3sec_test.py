# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.preprocessing._SlimPolyFeatures._partial_fit. \
    _lock_in_random_combos import _lock_in_random_combos

import pytest



# def _lock_in_random_combos(
#     poly_duplicates_: list[list[tuple[int, ...]]]
# ) -> tuple[tuple[int, ...], ...]:



class TestLIRCValidation:

    # test validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    # ------------------------------
    @pytest.mark.parametrize('junk_poly_duplicates',
        (-1,0,1,3.14,None,True,False,'trash',{'a':1}, min, lambda x: x)
    )
    def test_rejects_junk_poly_duplicates(self, junk_poly_duplicates):

        with pytest.raises(AssertionError):
            _lock_in_random_combos(junk_poly_duplicates)


    @pytest.mark.parametrize('bad_poly_duplicates',
        (
            [[0,1], [2,3]], [[('a',),('b',)], [('c',),('d',)]],
            [[(1,)]], [[(2,2)],[(2,2)]]
         )
    )
    def test_rejects_bad_poly_duplicates(self, bad_poly_duplicates):

        # not tuples
        # not ints
        # only one int in tuple
        # repeated tuple

        with pytest.raises(AssertionError):
            _lock_in_random_combos(bad_poly_duplicates)


    def test_accepts_good_poly_duplicates(self):

        out = _lock_in_random_combos([[(2, 3), (4, 5)]])

        assert isinstance(out, tuple)
        assert all(map(isinstance, out, (tuple for _ in out)))

    # ------------------------------

    # END test validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **



class TestLIRCAccuracy:

    # accuracy ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    def test_no_poly_duplicates(self):

        # no duplicates, so _rand_idxs should be empty

        rand_idxs_out = _lock_in_random_combos(poly_duplicates_=[])

        assert isinstance(rand_idxs_out, tuple)
        assert rand_idxs_out == tuple()



    @pytest.mark.parametrize('_poly_duplicates',
        ([[(0,1), (1, 4)]], [[(0, 1), (0,2)], [(2,4), (3,4)]])
    )
    def test_accuracy(self, _poly_duplicates):

        rand_idxs_out = _lock_in_random_combos(_poly_duplicates)

        assert isinstance(rand_idxs_out, tuple)

        # all we can validate is that that position in rand_idxs_out
        # contains one of the dupl combinations
        for _idx, _set in enumerate(_poly_duplicates):
            # kept would be randomly selected from _set
            assert list(rand_idxs_out)[_idx] in _set







