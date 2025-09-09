# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    DoNotDropType,
    DuplicatesType,
    FeatureNamesInType
)

import itertools

import numpy as np



def _lock_in_random_idxs(
    _duplicates: DuplicatesType,
    _do_not_drop: DoNotDropType,
    _columns: FeatureNamesInType | None
) -> tuple[int, ...]:
    """Lock in random indices for when `keep` is 'random'.

    The :meth:`transform` method needs to mask the same indices for
    all batch-wise transforms, otherwise the outputted batches will
    have different columns. When `keep` is set to 'random', `transform`
    needs a static set of random column indices to use repeatedly,
    rather than a set of dynamic indices that are regenerated with each
    call to `transform`.

    Goal: Create a static set of random indices that is regenerated with
    each call to :meth:`partial_fit`, but is unchanged when `transform`
    is called.

    This module builds a static ordered tuple of randomly selected
    indices, one index from each set of duplicates, subject to any
    constraints imposed by `do_not_drop`, if passed. For example, a
    simple case would be if `_duplicates` is [[0, 8], [1, 5, 9]], and
    `do_not_drop` is not passed, then a possible `_rand_idxs` might look
    like (8, 1). THE ORDER OF THE INDICES IN `_rand_idxs` IS CRITICALLY
    IMPORTANT AND MUST ALWAYS MATCH THE ORDER IN `_duplicates`.

    This module assumes that `keep` == 'random', even though that may
    not be the case. This makes the static list ready and waiting for
    use by `transform` should at any time `keep` be changed to 'random'
    via :meth:`set_params` after fitting.

    Parameters
    ----------
    _duplicates : DuplicatesType
        The groups of identical columns, indicated by their zero-based
        column index positions.
    _do_not_drop : DoNotDropType
        A list of columns not to be dropped. If fitting is done on a
        container that has a header, a list of feature names may be
        provided. Otherwise, a list of column indices must be provided.
    _columns : FeatureNamesInType | None of shape (n_features,)
        If fitting is done on a container that has a header, this is a
        ndarray of strings, otherwise is None.

    Returns
    -------
    _rand_idxs : tuple[int]
        An ordered tuple whose values are a sequence of column indices,
        one index selected from each set of duplicates in `_duplicates`.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # _duplicates must be list of lists of ints
    assert isinstance(_duplicates, list)
    for _set in _duplicates:
        assert isinstance(_set, list)
        assert len(_set) >= 2
        assert all(map(isinstance, _set, (int for _ in _set)))
    # all idxs in duplicates must be unique
    __ = list(itertools.chain(*_duplicates))
    assert len(np.unique(__)) == len(__)
    del __
    # -- -- -- --
    err_msg = "if not None, '_columns' must be a sequence of strings"
    if _columns is not None:
        try:
            iter(_columns)
            if isinstance(_columns, (str, dict)):
                raise Exception
        except:
            raise AssertionError(err_msg)

        assert all(map(isinstance, _columns, (str for _ in _columns))), err_msg
    # -- -- -- --
    err_msg = \
        "if not None, 'do_not_drop' must be a sequence of integers or strings"
    if _do_not_drop is not None:
        try:
            iter(_do_not_drop)
            if isinstance(_do_not_drop, (dict, str)):
                raise Exception
        except:
            raise AssertionError(err_msg)

        assert not any(map(isinstance, _do_not_drop, (bool for _ in _do_not_drop)))
        assert all(
            map(isinstance, _do_not_drop, ((int, str) for _ in _do_not_drop))
        ), err_msg

        if isinstance(_do_not_drop[0], str) and _columns is None:
            raise AssertionError(
                f"if _columns is not passed, _do_not_drop can only be passed "
                f"as integers"
            )
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # do_not_drop can be None! if do_not_drop is strings, convert to idxs
    if _do_not_drop is not None and isinstance(_do_not_drop[0], str):
        _do_not_drop = [list(_columns).index(col) for col in set(_do_not_drop)]


    _rand_idxs = []

    for _idx, _set in enumerate(_duplicates):

        if _do_not_drop is None:
            _n = 0
        else:
            _dnd_idxs = sorted(set(_do_not_drop).intersection(_set))
            _n = len(_dnd_idxs)

        if _n == 0:
            # no _do_not_drops in _set, or _do_not_drop is None
            _keep_idx = np.random.choice(_set)
        elif _n == 1:
            # conveniently 1 do_not_drop index in this set of dupls
            _keep_idx = _dnd_idxs[0]
        elif _n > 1:
            # pretend that always _conflict=='ignore' to get an index.
            # if conflict=='raise', _identify_idxs_to_delete() will raise,
            # and the fact that we took an invalid index will be moot
            _keep_idx = np.random.choice(_dnd_idxs)
        else:
            raise Exception(f"algorithm failure")

        _rand_idxs.append(_keep_idx)

    # this cant be a set, it messes up the order against duplicates_
    _rand_idxs = tuple(_rand_idxs)


    # output validation ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    err_msg = (
        f"'_rand_idxs' must be a tuple of integers, 0 <= idx < X.shape[1], "
        f"and a single idx from each set of duplicates must be represented "
        f"that is, len(_rand_idxs)==len(duplicates)."
    )

    assert isinstance(_rand_idxs, tuple), err_msg
    # all idxs in _rand_idxs must be in range of num features in X
    if len(_rand_idxs):
        assert min(_rand_idxs) >= 0, err_msg
        if _columns is not None:
            assert max(_rand_idxs) < len(_columns), err_msg
    # len _rand_idxs must match number of sets of duplicates
    assert len(_rand_idxs) == len(_duplicates), \
        err_msg + f"{_rand_idxs=}, {_duplicates=}"
    # if there are duplicates, every entry in _rand_idxs must match one idx
    # in each set of duplicates
    for _idx, _dupl_set in enumerate(_duplicates):
        assert _rand_idxs[_idx] in _dupl_set, \
            err_msg + f'rand idx = {_rand_idxs[_idx]}, dupl set = {_dupl_set}'
    # END output validation ** * ** * ** * ** * ** * ** * ** * ** * ** *


    return _rand_idxs




