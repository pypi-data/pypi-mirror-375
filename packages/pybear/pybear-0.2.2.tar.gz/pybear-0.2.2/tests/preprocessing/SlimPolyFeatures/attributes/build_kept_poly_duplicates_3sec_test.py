# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import itertools

from pybear.preprocessing._SlimPolyFeatures._attributes. \
    _build_kept_poly_duplicates import _build_kept_poly_duplicates



class TestBuildKeptPolyDuplicates:

    # def _build_kept_poly_duplicates(
    #     poly_duplicates_: list[list[tuple[int, ...]]],
    #     _kept_combos: tuple[tuple[int, ...], ...]
    # ) -> dict[tuple[int, ...], list[tuple[int, ...]]]:


    @pytest.mark.parametrize('junk_inputs',
        (-2.7,-1,0,1,2.7,True,None,'junk',[0,],(0,),{0,}, {'a':1}, lambda x: x)
    )
    def test_basic_validation(self, junk_inputs):

        # poly_duplicates_
        with pytest.raises(AssertionError):
            _build_kept_poly_duplicates(
                poly_duplicates_=junk_inputs,
                _kept_combos=((1,), (2,3), (4,5))
            )


        # _kept_combos
        with pytest.raises(AssertionError):
            _build_kept_poly_duplicates(
                poly_duplicates_=[[(1,), (6,7)], [(2,3), (4,5)]],
                _kept_combos=junk_inputs
            )


    def test_rejects_kept_combo_not_in_poly_dupls(self):

        with pytest.raises(AssertionError):
            _build_kept_poly_duplicates(
                poly_duplicates_=[[(1,), (6,7)], [(2,3), (4,5)]],
                _kept_combos=((2,), (8,9))
            )



    def test_accuracy(self):

        _kept_combos = ((1,), (4, 5))

        out = _build_kept_poly_duplicates(
            poly_duplicates_=[[(1,), (6, 7)], [(2, 3), (4, 5)]],
            _kept_combos=_kept_combos
        )

        assert isinstance(out, dict)
        assert all(map(isinstance, out.keys(), (tuple for _ in out)))
        assert all(map(isinstance, out.values(), (list for _ in out)))

        for _combo in _kept_combos:
            assert _combo in out

        _all_dropped = list(itertools.chain(*list(out.values())))
        for _tuple in _all_dropped:
            assert isinstance(_tuple, tuple)
            assert all(map(isinstance, _tuple, (int for _ in _tuple)))









