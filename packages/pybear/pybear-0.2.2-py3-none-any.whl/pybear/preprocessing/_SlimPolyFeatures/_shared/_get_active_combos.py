# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    CombinationsType,
    DroppedPolyDuplicatesType,
    PolyConstantsType
)


def _get_active_combos(
    _combos: list[tuple[int, ...]],
    poly_constants_: PolyConstantsType,
    dropped_poly_duplicates_: DroppedPolyDuplicatesType
) -> CombinationsType:
    """Find the tuples of column index combinations that will be in the
    outputted polynomial expansion.

    This supports both `partial_fit` and `transform`.

    Index tuples that are in `dropped_poly_duplicates_` or in
    `poly_constants_` are omitted from `_active_combos` and the final
    polynomial expansion. `_active_combos` is filled with the remaining
    index tuples from `_combos`.

    The output must be sorted asc on degree (shortest tuple to longest
    tuple), then asc on the indices.

    `_combos` must come in sorted for this to go out sorted.

    `_combos` is built directly from `itertools.combinations` or
    `itertools.combinations_with_replacement`, and is sorted coming out
    of :func:`_combination_builder` to ensure the correct sort, in case
    itertools built-ins ever change.

    Parameters
    ----------
    _combos : list[tuple[int, ...]]
        All combinations of column indices that are to be multiplied
        together for the polynomial expansion.
    poly_constants_ : PolyConstantsType
        A dictionary whose keys are tuples of indices in the original
        data that produced a column of constants. The dictionary values
        are the constant values in those columns.
    dropped_poly_duplicates_ : DroppedPolyDuplicatesType
        A dictionary whose keys are the tuples that are removed from the
        polynomial expansion because they produced a duplicate of another
        column. The values of the dictionary are the tuples of indices
        of the respective duplicate that was kept.

    Returns
    -------
    _active_combos : CombinationsType
        The tuples of column index combinations to be kept in the
        outputted polynomial expansion.

    """


    # validation - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    assert isinstance(_combos, list)
    assert all(map(isinstance, _combos, (tuple for _ in _combos)))

    assert isinstance(dropped_poly_duplicates_, dict)
    for k, v in dropped_poly_duplicates_.items():
        assert isinstance(k, tuple)
        assert all(map(isinstance, k, (int for _ in k)))
        assert isinstance(v, tuple)
        assert all(map(isinstance, v, (int for _ in v)))

    assert isinstance(poly_constants_, dict)
    assert all(map(
        isinstance, poly_constants_, (tuple for _ in poly_constants_)
    ))
    # END validation - - - - - - - - - - - - - - - - - - - - - - - - - -


    _active_combos = []
    for _combo in _combos:

        if _combo in dropped_poly_duplicates_:
            continue

        if _combo in poly_constants_:
            continue

        _active_combos.append(_combo)


    # it is extremely important that single tuples like (0, 1) leave here
    # as ((0,1),) !!!  piling them into a list like above then converting
    # to tuple is tested and appears to be robust to when there is only
    # one tuple.

    return tuple(_active_combos)



