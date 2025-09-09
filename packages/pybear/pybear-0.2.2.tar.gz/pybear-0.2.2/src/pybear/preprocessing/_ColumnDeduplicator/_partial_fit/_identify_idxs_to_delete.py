# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    DuplicatesType,
    KeepType,
    FeatureNamesInType,
    DoNotDropType,
    ConflictType,
    RemovedColumnsType
)

from copy import deepcopy
import itertools

import numpy as np



def _identify_idxs_to_delete(
    _duplicates: DuplicatesType,
    _keep: KeepType,
    _do_not_drop: DoNotDropType,
    _columns: FeatureNamesInType | None,
    _conflict: ConflictType,
    _rand_idxs: tuple[int, ...]
) -> RemovedColumnsType:
    """Apply the rules given by `keep`, `conflict`, and `do_not_drop`
    to the sets of duplicates in `_duplicates`.

    Produce the :attr:`removed_columns_` dictionary, which has all the
    deleted column indices as keys and the respective kept column as
    values.

    Parameters
    ----------
    _duplicates : DuplicatesType
        The groups of identical columns, indicated by their zero-based
        column index positions.
    _keep : KeepType
        The strategy for keeping a single representative from a set of
        identical columns. 'first' retains the column left-most in the
        data; 'last' keeps the column right-most in the data; 'random'
        keeps a single randomly-selected column of the set of duplicates.
    _do_not_drop : DoNotDropType
        A list of columns not to be dropped. If fitting is done on a
        container that has a header, a list of feature names may be
        provided. Otherwise, a list of column indices must be provided.
        If a conflict arises, such as two columns specified in `do_not_drop`
        are duplicates of each other, the behavior is managed by `conflict`.
    _columns : FeatureNamesInType | None of shape (n_features,)
        If fitting is done on a container that has a header, this is a
        ndarray of strings, otherwise is None.
    _conflict : ConflictType
        Ignored when `do_not_drop` is not passed. Instructs CDT how to
        deal with a conflict between the instructions in `keep` and
        `do_not_drop`. A conflict arises when the instruction in `keep`
        ('first', 'last', 'random') is applied and column in `do_not_drop`
        is found to be a member of the columns to be deleted. When
        `conflict` is 'raise', an exception is raised in the case of
        such a conflict. When `conflict` is 'ignore', there are 2
        possible scenarios:

        1) when only one column in `do_not_drop` is among the columns to
        be removed, the `keep` instruction is overruled and the
        do-not-drop column is kept

        2) when multiple columns in `do_not_drop` are among the columns
        to be deleted, the `keep` instruction ('first', 'last', 'random')
        is applied to the set of do-not-delete columns that are amongst
        the duplicates --- this may not give the same result as applying
        the `keep` instruction to the entire set of duplicate columns.
        This also causes at least one member of the columns not to be
        dropped to be removed.
    _rand_idxs : tuple[int]
        An ordered tuple whose values are a sequence of column indices,
        one index selected from each set of duplicates in `_duplicates`.
        For example, if `_duplicates` is [[0, 8], [1, 5, 9]], then a
        possible `_rand_idxs` might look like (8, 1).

    Returns
    -------
    removed_columns_ : RemovedColumnsType
        The keys are the indices of duplicate columns removed from the
        original data, indexed by their column location in the original
        data; the values are the column index in the original data of
        the respective duplicate that was kept.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # _duplicates must be list of list of ints
    assert isinstance(_duplicates, list)
    for _set in _duplicates:
        assert isinstance(_set, list)
        assert len(_set) >= 2
        assert all(map(isinstance, _set, (int for _ in _set)))
    # -- -- -- --
    # all idxs in duplicates must be unique
    __ = list(itertools.chain(*_duplicates))
    assert len(np.unique(__)) == len(__)
    del __
    # -- -- -- --
    assert isinstance(_keep, str)
    assert _keep.lower() in ['first', 'last', 'random']
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

        assert not any(
            map(isinstance, _do_not_drop, (bool for _ in _do_not_drop))
        )
        assert all(
            map(isinstance, _do_not_drop, ((int, str) for _ in _do_not_drop))
        ), err_msg

        if isinstance(_do_not_drop[0], str) and _columns is None:
            raise AssertionError(
                f"if _columns is not passed, _do_not_drop can only be passed "
                f"as integers"
            )
    # -- -- -- --
    assert isinstance(_conflict, str)
    assert _conflict.lower() in ['raise', 'ignore']
    # -- -- -- --
    err_msg = (
        f"'_rand_idxs' must be a tuple of integers 0 <= idx < X.shape[1], "
        f"and a single idx from each set of duplicates must be represented "
        f"in _rand_idxs"
    )
    assert isinstance(_rand_idxs, tuple), err_msg
    # all idxs in _rand_idxs must be in range of num features in X
    if len(_rand_idxs):
        assert min(_rand_idxs) >= 0, err_msg
        if _columns is not None:
            assert max(_rand_idxs) < len(_columns)
    # len _rand_idxs must match number of sets of duplicates
    assert len(_rand_idxs) == len(_duplicates)
    # if there are duplicates, every entry in _rand_idxs must match one idx
    # in each set of duplicates
    if len(_duplicates):
        for _idx, _dupl_set in enumerate(_duplicates):
            assert list(_rand_idxs)[_idx] in _dupl_set, \
                f'rand idx = {list(_rand_idxs)[_idx]}, dupl set = {_dupl_set}'

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # apply the keep, do_not_drop, and conflict rules to the duplicate idxs

    # do_not_drop can be None! if do_not_drop is strings, convert to idxs
    if _do_not_drop is not None and isinstance(_do_not_drop[0], str):
        _do_not_drop = [list(_columns).index(col) for col in set(_do_not_drop)]


    removed_columns_ = {}
    for _idx, _set in enumerate(_duplicates):

        if _do_not_drop is None:
            _n = 0
        else:
            _dnd_idxs = sorted(set(_do_not_drop).intersection(_set))
            _n = len(_dnd_idxs)

        if _n == 0:   # no _do_not_drops in _set, or _do_not_drop is None
            if _keep == 'first':
                _keep_idx = min(_set)
            elif _keep == 'last':
                _keep_idx = max(_set)
            elif _keep == 'random':
                _keep_idx = list(_rand_idxs)[_idx]

        elif _n == 1:

            # if the idx we are keeping is the do_not_drop idx,
            # then all good

            _dnd_idx = _dnd_idxs[0]

            if _dnd_idx == min(_set) and _keep == 'first':
                _keep_idx = _dnd_idx
            elif _dnd_idx == max(_set) and _keep == 'last':
                _keep_idx = _dnd_idx
            elif _keep == 'random':
                _keep_idx = _rand_idxs[_idx]
            elif _conflict == 'ignore':
                _keep_idx = _dnd_idx
            else:   # 'keep' doesnt conveniently align and _conflict=='raise'
                if _columns is None:
                    __ = f""
                else:
                    __ = f", '{_columns[_dnd_idx]}'"
                raise ValueError(
                    f"duplicate indices={_set}, do_not_drop={_do_not_drop}, ",
                    f"keep={_keep}, wants to drop column index {_dnd_idx}{__}, "
                    f"conflict with do_not_drop."
                )

            del _dnd_idx

        elif _n > 1:

            if _conflict == 'ignore':
                # since _dnd_idxs has multiple values, apply the 'keep' rules to
                # that list
                if _keep == 'first':
                    _keep_idx = min(_dnd_idxs)
                elif _keep == 'last':
                    _keep_idx = max(_dnd_idxs)
                elif _keep == 'random':
                    _keep_idx = _rand_idxs[_idx]

            elif _conflict == 'raise':
                if _columns is None:
                    __ = f""
                else:
                    __ = " (" + ", ".join([_columns[_] for _ in _dnd_idxs]) + ")"
                raise ValueError(
                    f"Duplicates have a conflict with do_not_drop. "
                    f"\nduplicate indices={_set}, do_not_drop={_do_not_drop}, ",
                    f"keep={_keep}. CDT wants to drop do_not_drop index(es) "
                    f"{', '.join(map(str, _dnd_idxs))} {__}"
                )

        else:
            raise Exception

        __ = deepcopy(_set)
        __.remove(_keep_idx)
        for _ in __:
            removed_columns_[int(_)] = int(_keep_idx)


    return removed_columns_






