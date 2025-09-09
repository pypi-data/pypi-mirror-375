# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#




from pybear.preprocessing._SlimPolyFeatures._partial_fit. \
    _deconstant_poly_dupls import _deconstant_poly_dupls


import pytest





class TestRemoveConstantsFromPolyDuplicates:

    # poly_constants cannot have tuples from X in it, but poly_duplicates can

    def test_accuracy_both_empty(self):

        out = _deconstant_poly_dupls(
                _poly_duplicates = [],
                _poly_constants = {}
        )

        assert out == []


    def test_accuracy_no_overlap(self):

        _poly_duplicates = [
            [(0,), (1,2), (4,5)],
            [(6,), (7,8), (9,10)]
        ]

        _poly_constants = {(2,3): 0, (3,5): 0}

        out = _deconstant_poly_dupls(
            _poly_duplicates=_poly_duplicates,
            _poly_constants=_poly_constants
        )

        for _dupl_idx, _dupl_set in enumerate(_poly_duplicates):
            for _tuple_idx, _tuple in enumerate(_dupl_set):
                assert _tuple == out[_dupl_idx][_tuple_idx]


    def test_accuracy_partial_overlap(self):

        _poly_duplicates = [
            [(0,), (1,2), (4,5)],
            [(6,), (7,8), (9,10)]
        ]

        _poly_constants = {(1,2): 0, (7,8): 0}

        out = _deconstant_poly_dupls(
            _poly_duplicates=_poly_duplicates,
            _poly_constants=_poly_constants
        )

        #         out should look like  = [
        #             [(0,), (4,5)],
        #             [(6,), (9,10)]
        #         ]

        assert out[0][0] == (0,)
        assert out[0][1] == (4,5)
        assert out[1][0] == (6,)
        assert out[1][1] == (9,10)


    def test_accuracy_full_overlap(self):

        _poly_duplicates = [[(1,2), (2,3), (4,5)]]

        _poly_constants = {(1,2): 1, (2,3): 0, (4,5): 0}

        out = _deconstant_poly_dupls(
            _poly_duplicates=_poly_duplicates,
            _poly_constants=_poly_constants
        )

        assert out == []










