# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import itertools

from pybear.preprocessing._SlimPolyFeatures._attributes. \
    _build_dropped_poly_duplicates import _build_dropped_poly_duplicates



class TestBuildDroppedPolyDuplicates:

    # def _build_dropped_poly_duplicates(
    #     poly_duplicates_: list[list[tuple[int, ...]]],
    #     _kept_combos: tuple[tuple[int, ...], ...]
    # ) -> dict[tuple[int, ...], tuple[int, ...]]:


    @pytest.mark.parametrize('junk_inputs',
        (-2.7,-1,0,1,2.7,True,None,'junk',[0,],(0,),{0,}, {'a':1}, lambda x: x)
    )
    def test_basic_validation(self, junk_inputs):

        # poly_duplicates_
        with pytest.raises(AssertionError):
            _build_dropped_poly_duplicates(
                poly_duplicates_=junk_inputs,
                _kept_combos=((1,), (2,3), (4,5))
            )


        # _kept_combos
        with pytest.raises(AssertionError):
            _build_dropped_poly_duplicates(
                poly_duplicates_=[[(1,), (6,7)], [(2,3), (4,5)]],
                _kept_combos=junk_inputs
            )


    def test_rejects_kept_combo_not_in_poly_dupls(self):

        with pytest.raises(AssertionError):
            _build_dropped_poly_duplicates(
                poly_duplicates_=[[(1,), (6,7)], [(2,3), (4,5)]],
                _kept_combos=((2,), (8,9))
            )


    def test_accuracy(self):

        _poly_dupls = [[(1,), (6, 7)], [(2, 3), (4, 5)]]
        _kept_combos = ((1,), (4, 5))

        out = _build_dropped_poly_duplicates(
            poly_duplicates_=_poly_dupls,
            _kept_combos=_kept_combos
        )

        assert isinstance(out, dict)
        assert all(map(isinstance, out.keys(), (tuple for _ in out)))
        assert all(map(isinstance, out.values(), (tuple for _ in out)))

        assert len(out) == \
               (len(list(itertools.chain(*_poly_dupls))) - len(_kept_combos))

        for _dropped_combo, _kept_combo in out.items():
            assert _dropped_combo not in _kept_combos
            assert _kept_combo in _kept_combos













