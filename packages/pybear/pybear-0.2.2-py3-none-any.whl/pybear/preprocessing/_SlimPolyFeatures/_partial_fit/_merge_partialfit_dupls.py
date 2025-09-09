# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import PolyDuplicatesType

import itertools
import warnings

from ....utilities._union_find import union_find



def _merge_partialfit_dupls(
    _old_duplicates: PolyDuplicatesType | None,
    _new_duplicates: PolyDuplicatesType,
) -> PolyDuplicatesType:
    """Compare the newest duplicates found in the current partial fit
    with duplicates found on earlier partial fits and meld together to
    produce overall duplicates.

    The lead-up to this module:

    Within a partial fit, for all combos get the duplicates
    with :func:`_get_dupls_for_combo_in_X_and_poly`. Convert the output
    format with :func:`pybear.utilities.union_find`. The output of
    `union_find` is the final list of duplicates for the current
    partial fit. Merge the current partial fit's dupls with dupls from
    previous partial fits with this module.

    Any combos previously not identified as equal but currently are
    equal, are coincidentally equal and are not added to the final list.
    Combos previously found to be equal but are not currently equal are
    removed from the final lists of duplicates. The only duplicates
    retained are those combos found to be identical for all partial fits.

    The merged duplicates must be sorted in this way:

    All combos should already be sorted asc on indices. Within each
    group of duplicates, sort first on tuple len (degree), then sort asc
    on idx values. Across groups of duplicates sort in the same way on
    the first value in each group, so that the groups are asc on degree,
    then on indices.

    Parameters
    ----------
    _old_duplicates : PolyDuplicatesType | None
        The duplicate combos carried over from the previous partial fits.
        Is None if on the first partial fit.
    _new_duplicates : PolyDuplicatesType
        The duplicate combos found during the current partial fit.

    Returns
    -------
    duplicates_ : PolyDuplicatesType
        The groups of identical combos across all partial fits.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    assert isinstance(_old_duplicates, (list, type(None)))
    if _old_duplicates is not None:
        for _dupl_set in _old_duplicates:
            assert len(_dupl_set) >= 2
            assert isinstance(_dupl_set, list)
            assert all(map(isinstance, _dupl_set, (tuple for _ in _dupl_set)))
            for _tuple in _dupl_set:
                assert isinstance(_tuple, tuple)
                assert all(map(isinstance, _tuple, (int for _ in _tuple)))

    assert isinstance(_new_duplicates, list)
    for _dupl_set in _new_duplicates:
        assert len(_dupl_set) >= 2
        assert isinstance(_dupl_set, list)
        assert all(map(isinstance, _dupl_set, (tuple for _ in _dupl_set)))
        for _tuple in _dupl_set:
            assert isinstance(_tuple, tuple)
            assert all(map(isinstance, _tuple, (int for _ in _tuple)))

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # if _old_duplicates is None, this is the first pass
    if _old_duplicates is None:
        _duplicates = _new_duplicates
    elif _old_duplicates is not None:
        # duplicates found on later partial fits cannot increase the
        # number of duplicates over what was found on previous partial
        # fits. If later partial fits find new identical columns, it can
        # only be coincidental, as those columns were previously found to
        # be unequal. The number of duplicates can decrease, however, if
        # later partial fits find non-equality in columns that were
        # previously found to be equal.

        # compare the newest duplicates against the previously found
        # duplicates. Only a group of 2+ columns that appear together in
        # a set of dupls in both duplicates can carry forward. make sense?
        # this uses single column indices, not combos
        # _old_duplicates = [[0,1,2], [4,5]]
        # _new_duplicates = [[0,3], [1,2], [4,5]]
        # only [1,2] and [4,5] carry forward.

        # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
        # get the possible combinations of pairs within both old and new
        # duplicates, then find the intersection, to find all pairs of
        # numbers that are in the same subset for both duplicates.

        all_old_comb = []
        for _dupl_set in _old_duplicates:
            all_old_comb += list(itertools.combinations(_dupl_set, 2))

        all_new_comb = []
        for _dupl_set in _new_duplicates:
            all_new_comb += list(itertools.combinations(_dupl_set, 2))

        _intersection = set(all_old_comb).intersection(all_new_comb)

        if len(_old_duplicates) or len(_new_duplicates):
            del _dupl_set
        del all_old_comb, all_new_comb

        # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

        # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
        _duplicates = list(map(list, union_find(_intersection)))

        # Sort each component and the final result for consistency.
        # within connected sets, sort asc len, then within the same lens
        # sort asc idxs
        for _idx, _conn_set in enumerate(_duplicates):
            _duplicates[_idx] = sorted(_conn_set, key=lambda x: (len(x), x))
        # across all dupl sets, only look at the first value in a dupl set,
        # sort on len asc, then indices asc
        _duplicates = sorted(_duplicates, key=lambda x: (len(x[0]), x[0]))

    # if any dupl set contains more than 1 tuple of len==1 (i.e., more
    # than one column from X) warn for duplicate columns in X.
    # in SPF.partial_fit(), SPF will warn if duplicates/constants are
    # found in X, but only when SPF :param: scan_X is True.
    # This will warn regardless of whether the scan is performed or not.
    for _dupl_set in _duplicates:
        if sum(map(lambda x: x==1, map(len, _dupl_set))) > 1:
            warnings.warn(
                f"There are duplicate columns in X. Do more partial fits "
                f"or use pybear ColumnDeduplicator to remove them before "
                f"using SlimPoly."
            )


    return _duplicates





