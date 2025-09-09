# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.preprocessing._SlimPolyFeatures._shared._identify_combos_to_keep \
    import _identify_combos_to_keep



class TestICTKBasicValidation:

    # def _identify_combos_to_keep(
    #     poly_duplicates_: list[list[tuple[int, ...]]],
    #     _keep: Literal['first', 'last', 'random'],
    #     _rand_combos: tuple[tuple[int, ...], ...]
    # ) -> tuple[tuple[int, ...], ...]:


    @pytest.mark.parametrize('junk_inputs',
        (-2.7,-1,0,1,2.7,True,False,None,'trash',[0,1],(0,1),{0,1},lambda x: x)
    )
    def test_rejects_junk(self, junk_inputs):

        # poly_duplicates
        with pytest.raises(AssertionError):
            _identify_combos_to_keep(
                junk_inputs,
                _keep='first',
                _rand_combos=((1,),(2,3),(4,5))
            )

        # keep
        with pytest.raises(AssertionError):
            _identify_combos_to_keep(
                poly_duplicates_=[[(1,), (8,9)], [(1,2), (2,3)], [(2,4), (4,5)]],
                _keep=junk_inputs,
                _rand_combos=((1,),(2,3),(4,5))
            )

        # rand_idxs
        with pytest.raises(AssertionError):
            _identify_combos_to_keep(
                poly_duplicates_=[[(1,), (8,9)], [(1,2), (2,3)], [(2,4), (4,5)]],
                _keep='last',
                _rand_combos=junk_inputs
            )


    @pytest.mark.parametrize('_keep', ('first', 'last', 'random'))
    def test_accepts_good(self, _keep):

        _poly_dupls = [[(1,), (8,9)], [(1,2), (2,3)], [(2,4), (4,5)]]
        _rand_combos = ((1,), (2, 3), (4, 5))

        out = _identify_combos_to_keep(
            poly_duplicates_=_poly_dupls,
            _keep=_keep,
            _rand_combos=_rand_combos
        )

        assert isinstance(out, tuple)
        assert len(out) == len(_poly_dupls)


class TestICTKAccuracy:

    @pytest.mark.parametrize('_keep', ('first', 'last', 'random'))
    def test_accuracy(self, _keep):

        _poly_dupls = [[(1,), (8, 9)], [(1, 2), (2, 3)], [(2, 4), (4, 5)]]
        _rand_combos = ((1,), (2, 3), (4, 5))

        out = _identify_combos_to_keep(
            poly_duplicates_=_poly_dupls,
            _keep=_keep,
            _rand_combos=_rand_combos
        )

        assert isinstance(out, tuple)
        assert len(out) == len(_poly_dupls)

        # remember that len(tuple)==1 always overrides keep!
        if _keep == 'first':
            assert out == ((1,), (1,2), (2,4))
        elif _keep == 'last':
            assert out == ((1,), (2,3), (4,5))
        if _keep == 'random':
            assert len(out) == len(_poly_dupls)
            # random indices must match those in _rand_combos exactly!
            for _out_idx, _out_combo in enumerate(out):
                # remember len(tuple)==1 always overrides keep! even for random!
                if len(_poly_dupls[0]) == 1:
                    assert _out_combo == _poly_dupls[0]
                else:
                    assert out[_out_idx] == _rand_combos[_out_idx]


    @pytest.mark.parametrize('_keep', ('first', 'last', 'random'))
    def rejects_mismatch_between_poly_dupls_and_rand_combos(self, _keep):

        with pytest.raises(AssertionError):
            _identify_combos_to_keep(
                poly_duplicates_=[
                    [(1,), (8, 9)], [(1, 2), (2, 3)], [(2, 4), (4, 5)]
                ],
                _keep=_keep,
                _rand_combos=((8, 8), (2, 4), (3, 5))
            )















