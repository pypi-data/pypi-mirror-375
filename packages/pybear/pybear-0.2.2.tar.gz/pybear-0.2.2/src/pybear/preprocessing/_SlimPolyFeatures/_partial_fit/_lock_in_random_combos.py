# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    CombinationsType,
    PolyDuplicatesType
)

import itertools

import numpy as np




def _lock_in_random_combos(
    poly_duplicates_: PolyDuplicatesType
) -> CombinationsType:
    """Build a static ordered tuple of randomly selected combo tuples,
    one tuple from each set of duplicates.

    When SPF `keep` is set to 'random', SPF `transform` needs to keep
    the same poly terms for all batch-wise transforms, otherwise the
    outputted batches will have different columns. `transform` needs
    a static set of random combo tuples to use repeatedly, rather
    than a set of dynamic tuples that are regenerated with each call to
    `transform`.

    `_identify_combos_to_keep` (_ictk) handles setting the combos to
    keep from sets of duplicates on every call to SPF `partial_fit` and
    `transform`. Random tuples can't be chosen in _ictk because it is
    called in `transform` as well as `partial_fit`. There must be a
    stand-alone module in `partial_fit` that locks in random tuples for
    all `transform` calls.

    Goal: Create a static set of random combo tuples that is regenerated
    with each call to `partial_fit`, but is unchanged when `transform`
    is called.

    This module builds a static ordered tuple of randomly selected
    combo tuples, one tuple from each set of duplicates. For example,
    a simple case would be if `poly_duplicates_` is
    [[(1, 2), (3, 5)], [(0, 8), (6, 7)]], then a possible `_rand_combos`
    might look like ((1, 2), (6, 7)). THE ORDER OF THE TUPLES IN
    _rand_combos IS CRITICALLY IMPORTANT AND MUST ALWAYS MATCH THE ORDER
    OF GROUPS IN `poly_duplicates_`.

    We can just randomly pick tuples from dupl groups where a column from
    X is included, e.g., [[(1,), (1,2), (1,3)]], because when we choose
    the actual columns to keep, _ictk will ignore `_rand_combos` for
    that dupl group and the column from X will always be kept.

    This module assumes that `keep` == 'random', even though that may
    not be the case. This makes the static list ready and waiting for
    use by `transform` should at any time SPF `keep` be changed to
    'random' via `set_params` after fitting.

    Parameters
    ----------
    poly_duplicates_ : PolyDuplicatesType
        The groups of column index tuples that create identical columns.

    Returns
    -------
    _rand_combos : CombinationsType
        An ordered tuple whose values are tuples of column indices from
        X, each tuple being selected from a group of duplicates in
        `poly_duplicates_`. One tuple is selected from each group of
        duplicates.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # poly_duplicates_ must be list of lists of tuples of ints

    assert isinstance(poly_duplicates_, list)
    for _set in poly_duplicates_:
        assert isinstance(_set, list)
        assert len(_set) >= 2, f"{len(_set)=}"
        for _tuple in _set:
            assert isinstance(_tuple, tuple)
            assert all(map(isinstance, _tuple, (int for _ in _tuple)))
            assert len(_tuple) >= 1, f"{len(_tuple)=}"

    # all idx tuples in poly_duplicates_ must be unique
    a = set(itertools.chain(*poly_duplicates_))
    b = list(itertools.chain(*poly_duplicates_))
    assert len(a) == len(b), \
        f"{a=}, {len(a)=}, {b=}, {len(b)=}"
    del a, b

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    _rand_combos: CombinationsType = []

    for _dupl_set in poly_duplicates_:

        # we can just randomly pick anything from _dupl_set even if
        # _dupl_set[0] turns out to be from X (len(_dupl_set[0])==1),
        # because it is overruled in _identify_combos_to_keep anyway

        _keep_tuple_idx = np.random.choice(np.arange(len(_dupl_set)))

        _rand_combos.append(_dupl_set[_keep_tuple_idx])

    # _rand_combos cant be a set, it messes up the order against
    # poly_duplicates_.
    # it is also important that if there is only one tuple it be returned
    # like ((0,1),).  The list-to-tuple method as used here is tested and
    # appears to be robust for this purpose.
    _rand_combos = tuple(_rand_combos)


    # output validation ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    err_msg = (
        f"'_rand_combos' must be a tuple of tuples of integers, and a "
        f"single tuple from each set of duplicates must be represented, "
        f"implying at least len(_rand_combos)==len(poly_duplicates_). "
        f"\n{_rand_combos=}, {poly_duplicates_=}"
    )

    assert isinstance(_rand_combos, tuple), err_msg

    # len _rand_combos must match number of sets of duplicates
    assert len(_rand_combos) == len(poly_duplicates_), err_msg

    # if there are duplicates, every entry in _rand_combos must match
    # one tuple in each dupl group in poly_duplicates_, in order
    for _idx, _dupl_set in enumerate(poly_duplicates_):
        assert _rand_combos[_idx] in _dupl_set, err_msg


    return _rand_combos





