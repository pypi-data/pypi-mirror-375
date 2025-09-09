# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    CombinationsType,
    DroppedPolyDuplicatesType,
    PolyDuplicatesType
)

from copy import deepcopy



def _build_dropped_poly_duplicates(
    poly_duplicates_: PolyDuplicatesType,
    _kept_combos: CombinationsType
) -> DroppedPolyDuplicatesType:
    """Build `dropped_poly_duplicates_`.

    `dropped_poly_duplicates_` is the subset of `poly_duplicates_` that
    is left out of the final polynomial expansion. It is a dictionary
    with the combo tuples of the excluded duplicates as keys. The value
    for each key is the combo tuple that is identical to the key that is
    kept in the final expansion.

    Parameters
    ---------
    poly_duplicates_ : PolyDuplicatesType
        The groups of duplicates found in the polynomial expansions
        across all partial fits. If `min_degree` is 1 and any combos
        were equal to a column in `X`, then the `X` idx tuple (c_idx, )
        must be included, must be first, and there can only be one.
    _kept_combos : CombinationsType
        The kept combo for each set of duplicates in `poly_duplicates_`.
        Length must equal the length of `poly_duplicates_`.

    Returns
    -------
    dropped_poly_duplicates_ : DroppedPolyDuplicatesType
        A dictionary with the dropped poly duplicate combos as keys.

    """


    # validation - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    assert isinstance(poly_duplicates_, list)
    for _list in poly_duplicates_:
        assert isinstance(_list, list)
        assert len(_list) >= 2
        for _tuple in _list:
            assert isinstance(_tuple, tuple)
            assert len(_tuple) >= 1
            assert all(map(isinstance, _tuple, (int for _ in _tuple)))

    if len(poly_duplicates_):
        del _list, _tuple

    assert isinstance(_kept_combos, tuple)
    assert len(_kept_combos) == len(poly_duplicates_)
    for _tuple in _kept_combos:
        assert isinstance(_tuple, tuple)
        assert all(map(isinstance, _tuple, (int for _ in _tuple)))

    # END validation - - - - - - - - - - - - - - - - - - - - - - - - - -


    # need to know from :param: _kept_combos which one from each dupl set
    # is kept, all other poly_duplicates_ are dropped

    dropped_poly_duplicates_: DroppedPolyDuplicatesType = {}
    for _dupl_set_idx, _dupl_set in enumerate(poly_duplicates_):

        # dont need to sort poly_duplicates_ or _dupl_sets here, that
        # was done on the way out of _merge_partialfit_dupls

        _kept_combo = _kept_combos[_dupl_set_idx]
        _dropped_combos = deepcopy(_dupl_set)
        try:
            _dropped_combos.remove(_kept_combo)
        except:
            raise AssertionError(
                f"algorithm failure. the combo in _kept_combos is not in "
                f"_dupl_set."
            )

        assert len(_dropped_combos) >= 1

        for _combo in _dropped_combos:
            dropped_poly_duplicates_[_combo] = _kept_combo


    if len(poly_duplicates_):
        del _kept_combo, _dropped_combos, _dupl_set_idx, _dupl_set


    return dropped_poly_duplicates_





