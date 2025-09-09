# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import DuplicatesType

import itertools

from ....utilities._union_find import union_find



def _merge_dupls(
    _previous_duplicates: DuplicatesType | None,
    _current_duplicates: DuplicatesType
) -> DuplicatesType:
    """Compare the newest duplicates found in the current partial fit
    with previous duplicates found on earlier partial fits and meld
    together to produce overall duplicates.

    Any columns previously not identified as equal but currently are
    equal, are coincidentally equal and are not added to the final list.
    Columns previously found to be equal but are not currently equal are
    removed from the final lists of duplicates. The only duplicates
    retained are those columns found to be identical for all partial
    fits.

    Parameters
    ----------
    _previous_duplicates : DuplicatesType | None
        The duplicate columns carried over from the previous partial
        fits. Is None if on the first partial fit.
    _current_duplicates : DuplicatesType
        The duplicate columns found on the current partial fit.

    Returns
    -------
    duplicates_ : DuplicatesType
        The groups of identical columns, indicated by their zero-based
        column index positions.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    assert isinstance(_previous_duplicates, (list, type(None)))
    if _previous_duplicates is not None:
        for _set in _previous_duplicates:
            assert isinstance(_set, list)
            assert all(map(isinstance, _set, (int for _ in _set)))

    assert isinstance(_current_duplicates, list)
    for _set in _current_duplicates:
        assert isinstance(_set, list)
        assert all(map(isinstance, _set, (int for _ in _set)))

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # if _duplicates is None, this is the first pass
    if _previous_duplicates is None:
        return _current_duplicates

    # elif _previous_duplicates is not None:
    # duplicates found on subsequent partial fits cannot increase the
    # number of duplicates over what was found on previous partial
    # fits. If later partial fits find new identical columns, it can
    # only be coincidental, as those columns were previously found to
    # be unequal. The number of duplicates can decrease, however, if
    # later partial fits find non-equality in columns that were
    # previously found to be equal.

    # compare the newest duplicates against the previously found
    # duplicates. Only a group of 2+ columns that appear together in
    # a set of dupls for all partial fits can carry forward. make sense?
    # _duplicates_1 = [[0,1,2], [4,5]]
    # _duplicates_2 = [[0, 3], [1,2], [4,5]]
    # only [1,2] and [4,5] carry forward.

    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
    # get the possible combinations of pairs for both duplicates, then
    # find the intersection, to find all pairs of numbers that are in the
    # same subset for both duplicates.

    all_old_comb = []
    for _set in _previous_duplicates:
        all_old_comb += list(itertools.combinations(_set, 2))

    all_new_comb = []
    for _set in _current_duplicates:
        all_new_comb += list(itertools.combinations(_set, 2))

    _intersection = set(all_old_comb).intersection(all_new_comb)

    del all_old_comb, all_new_comb

    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

    duplicates_ = union_find(_intersection)

    # Sort each component and the final result for consistency
    duplicates_ = [sorted(component) for component in duplicates_]
    duplicates_ = sorted(duplicates_, key=lambda x: x[0])


    return duplicates_





