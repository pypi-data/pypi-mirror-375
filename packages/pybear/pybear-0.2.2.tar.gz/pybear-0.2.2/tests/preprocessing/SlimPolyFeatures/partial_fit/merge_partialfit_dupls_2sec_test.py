# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#




from pybear.preprocessing._SlimPolyFeatures._partial_fit._merge_partialfit_dupls \
    import _merge_partialfit_dupls

import pytest



class TestDuplCombos:


    @staticmethod
    @pytest.fixture(scope='module')
    def _init_duplicates():
        # the sorting must be asc len(tuple) then asc idxs
        return [
            [(1,), (15,18)],
            [(3,4), (8,9), (12,18)]
        ]


    @staticmethod
    @pytest.fixture(scope='module')
    def _less_duplicates():
        # the sorting must be asc len(tuple) then asc idxs
        return [
            [(1,), (15,18)],
            [(3,4), (12,18)]
        ]


    @staticmethod
    @pytest.fixture(scope='module')
    def _more_duplicates():
        # the sorting must be asc len(tuple) then asc idxs
        return [
            [(1,), (4,6), (15,18)],
            [(3,4), (8,9), (12,18)]
        ]


    def test_first_pass(self, _init_duplicates):

        # on first pass, the output of _new_duplicates is returned directly.

        out = _merge_partialfit_dupls(None, _init_duplicates)

        for idx in range(len(out)):
            #                  vvvvvvvvvvvvvvvvvvvvv
            assert out[idx] == _init_duplicates[idx]


    def test_less_dupl_found(self, _init_duplicates, _less_duplicates):

        # on a partial fit where less duplicates are found, outputted melded
        # duplicates should reflect the lesser columns

        out = _merge_partialfit_dupls(_init_duplicates, _less_duplicates)

        for idx in range(len(out)):
            #                  vvvvvvvvvvvvvvvvvvvvv
            assert out[idx] == _less_duplicates[idx]


    def test_more_dupl_found(self, _init_duplicates, _more_duplicates):

        # on a partial fit where more duplicates are found, outputted melded
        # duplicates should not add the newly found columns

        out = _merge_partialfit_dupls(_init_duplicates, _more_duplicates)

        for idx in range(len(out)):
            #                  vvvvvvvvvvvvvvvvvvvvv
            assert out[idx] == _init_duplicates[idx]


    def test_more_and_less_duplicates_found(
        self, _init_duplicates, _less_duplicates, _more_duplicates
    ):

        duplicates_ = _merge_partialfit_dupls(None, _init_duplicates)

        duplicates_ = _merge_partialfit_dupls(duplicates_, _more_duplicates)

        duplicates_ = _merge_partialfit_dupls(duplicates_, _less_duplicates)

        # _less_duplicates must be the correct output
        for idx in range(len(duplicates_)):
            assert duplicates_[idx] == _less_duplicates[idx]



    def test_no_duplicates_found(self, _init_duplicates):

        duplicates_ = _merge_partialfit_dupls(None, [])

        assert duplicates_ == []

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        duplicates_ = _merge_partialfit_dupls(None, _init_duplicates)

        duplicates_ = _merge_partialfit_dupls(duplicates_, [])

        assert duplicates_ == []


    def test_special_case_accuracy(self):

        # test cases where columns repeat, but in different groups

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        _fst_duplicates = [[(0,), (1,9), (2,10)], [(3,11), (4,12), (5,13)]]
        _scd_duplicates = [[(0,), (4,12), (5,13)], [(1,9), (2,10), (3,11)]]

        out = _merge_partialfit_dupls(_fst_duplicates, _scd_duplicates)

        assert out == [[(1,9), (2,10)], [(4,12), (5,13)]]

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        _fst_duplicates = [[(1,), (3,11), (5,13)], [(0,), (2,10), (4,12)]]
        _scd_duplicates = [[(0,), (2,10), (4,12)], [(1,), (3,11), (5,13)]]

        out = _merge_partialfit_dupls(_fst_duplicates, _scd_duplicates)

        assert out == [[(0,), (2,10), (4,12)], [(1,), (3,11), (5,13)]]

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        _fst_duplicates = [[(0,), (1,10)], [(2,), (3,12)], [(4,), (5,14)]]
        _scd_duplicates = [[(0,), (4,)], [(1,10), (3,12)], [(2,), (5,14)]]

        out = _merge_partialfit_dupls(_fst_duplicates, _scd_duplicates)

        assert out == []


    def test_sorting(self):

        # always returns _dupl_sets sorted by asc len(tuple), then asc on idxs

        _fst_duplicates = [[(3,11), (1,), (5,13)], [(4,12), (0,1), (2,)]]
        _scd_duplicates = [[(0,1), (4,12), (2,)], [(1,), (3,11), (5,13)]]

        out = _merge_partialfit_dupls(_fst_duplicates, _scd_duplicates)

        assert out == [[(1,), (3,11), (5,13)], [(2,), (0,1), (4,12)]]




