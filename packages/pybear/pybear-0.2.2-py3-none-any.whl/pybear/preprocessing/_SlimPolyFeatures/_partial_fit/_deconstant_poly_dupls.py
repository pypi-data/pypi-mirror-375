# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    PolyDuplicatesType,
    PolyConstantsType
)



def _deconstant_poly_dupls(
    _poly_duplicates: PolyDuplicatesType,
    _poly_constants: PolyConstantsType
) -> PolyDuplicatesType:
    """Remove any constant combos from the in-process `_poly_duplicates`.

    Parameters
    ----------
    _poly_duplicates : PolyDuplicatesType
        The in-process version of poly_duplicates_, which holds the
        groups of column index tuples that create identical columns in
        the expansion, constant columns included.
    _poly_constants : PolyConstantsType
        A dictionary whose keys are tuples of indices in the original
        data that produced a column of constants in the polynomial
        expansion. The dictionary values are the constant values in
        those columns.

    Returns
    -------
    _no_constant_poly_duplicates : PolyDuplicatesType
        A copy of `_poly_duplicates` that has constant combos removed,
        if there were any.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    assert isinstance(_poly_duplicates, list)
    assert all(map(isinstance, _poly_duplicates, (list for _ in _poly_duplicates)))

    assert isinstance(_poly_constants, dict)
    assert all(map(isinstance, _poly_constants, (tuple for _ in _poly_constants)))

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    _no_constant_poly_duplicates: PolyDuplicatesType = []

    for _dupl_set in _poly_duplicates:

        _no_constant_dupl_set = set(_dupl_set)
        _no_constant_dupl_set -= set(_dupl_set).intersection(_poly_constants)
        _no_constant_dupl_set = list(_no_constant_dupl_set)

        # ensure sort is correct, asc on tuple len, then asc on indices
        _no_constant_dupl_set = \
            sorted(_no_constant_dupl_set, key=lambda x: (len(x), x))

        _no_constant_poly_duplicates.append(_no_constant_dupl_set)

    # remove any empties that may have been left by set intersection.
    # also, if there is a dupl from X (which would be a constant in X),
    # it may get left here leaving only one entry in a _dupl_set, so
    # remove it in that case. if there is a single poly combo left in a
    # dupl_set, then we have a serious algorithm problem.
    # must go thru this backwards, deleting on the fly
    for _dupl_idx in range(len(_no_constant_poly_duplicates)-1, -1, -1):
        _active_dupl_set = _no_constant_poly_duplicates[_dupl_idx]
        _dupl_set_len = len(_active_dupl_set)
        if _dupl_set_len == 0:
            _no_constant_poly_duplicates.pop(_dupl_idx)
        if _dupl_set_len == 1:
            if len(_active_dupl_set[0]) == 1:
                # this is "OK", it is a constant in X, just delete the dupl_set
                _no_constant_poly_duplicates.pop(_dupl_idx)
            elif len(_active_dupl_set[0]) > 1:
                # this is bad, a single combo tuple is in a dupl_set
                raise AssertionError(
                    f"algorithm failure. a single combo tuple is in a "
                    f"poly_dupl dupl_set"
                )

    # just to be safe, ensure sort is correct across inner groups
    if len(_no_constant_poly_duplicates):
        _no_constant_poly_duplicates = \
            sorted(_no_constant_poly_duplicates, key=lambda x: (len(x[0]), x[0]))


    return _no_constant_poly_duplicates





