# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import TotalCountsByColumnType



def _tcbc_update(
    old_tcbc: TotalCountsByColumnType,
    recursion_tcbc: TotalCountsByColumnType,
    MAP_DICT: dict[int, int]
) -> TotalCountsByColumnType:
    """Iterate over self._tcbc (old_tcbc) and compare the counts to the
    corresponding ones in RecursiveCls._tcbc (recursion_tcbc).

    If RecursiveCls's value is lower, put it into self's; if key does
    not exist in `recursion_tcbc`, set self's value to 0.

    `_total_counts_by_column` is a dict of unqs and cts for each column
    in X. If X had features deleted when it was processed by self before
    being passed into recursion, then map feature locations in
    RecursiveCls._tcbc to their old locations in self._tcbc.

    There is a problem with matching that largely seems to impact nan.
    Create a new working unq_ct_dict for both self and recursion that
    removes any nans (there should be at most one in each!), and
    retain their counts. Perform the number swapping operation on the
    working old_tcbc unq_ct_dict. After that, put the nan key from self
    and the value from RecursionCls into the working old_tcbc unq_ct_dict.
    Replace the unq_ct_dict in old_tcbc for that column index with the
    working version. Do this for all the columns. Return old_tcbc.

    Parameters
    ----------
    old_tcbc : TotalCountsByColumnType
        The total_cts_by_column dictionary from self.
    recursion_tcbc : TotalCountsByColumnType
        The total_cts_by_column dictionary from the recursion instance.
    MAP_DICT : dict[int, int]
        Dictionary mapping a feature's location in Recursion._tcbc to
        its (possibly different) location in self._tcbc.

    Returns
    -------
    old_tcbc : TotalCountsByColumnType
        Updated with counts from Recursion._tcbc

    """


    # validation - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # old_tcbc
    for _c_idx, _inner in old_tcbc.items():
        assert isinstance(_c_idx, int)
        assert isinstance(_inner, dict)
        # dont validate keys (uniques) could be anything
        assert all(map(isinstance, _inner.values(), (int for _ in _inner)))

    # recursion_tcbc
    for _c_idx, _inner in recursion_tcbc.items():
        assert isinstance(_c_idx, int)
        assert isinstance(_inner, dict)
        # dont validate keys (uniques) could be anything
        assert all(map(isinstance, _inner.values(), (int for _ in _inner)))

    # map_dict
    assert isinstance(MAP_DICT, dict)
    for k, v in MAP_DICT.items():
        assert isinstance(k, int), f"k = {k}, type(k) = {type(k)}"
        assert isinstance(v, int), f"v = {v}, type(v) = {type(v)}"
    # END validation - - - - - - - - - - - - - - - - - - - - - - - - - -


    for new_col_idx in recursion_tcbc:

        old_col_idx = MAP_DICT[new_col_idx]

        # if old_tcbc had an empty UNQ_CT_DICT (which it may have, because
        # for ignored <columns, float columns, or bin-int columns>
        # UNQ_CT_DICT is set to {}) then recursion_tcbc UNQ_CT_DICT FOR
        # that column (possibly in a different index slot) must also be {}
        if not len(old_tcbc[old_col_idx]) and len(recursion_tcbc[new_col_idx]):
            raise AssertionError(
                f"old_tcbc[{old_col_idx}] is empty, but "
                f"recursion_tcbc[{new_col_idx}] is not"
            )



        # ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
        # manipulation of old_tcbc and recursion tcbc to get the nans out
        # remove any nans from unqs (should only be 1!), and get the count

        # reconstruct old_tcbc[col_idx] in a copy
        _old_tcbc_nan_symbol = None
        _old_tcbc_nan_ct = 0
        _old_tcbc_col_dict = {}
        for k, v in old_tcbc[old_col_idx].items():
            if str(k) in ['nan', 'NAN', 'NaN', '<NA>']:
                if _old_tcbc_nan_symbol is not None:
                    raise ValueError(
                        f">=2 nan-like in old_tcbc: col idx {old_col_idx}, "
                        f"{old_tcbc[old_col_idx]}"
                    )
                _old_tcbc_nan_symbol = k
                _old_tcbc_nan_ct = v
            else:
                _old_tcbc_col_dict[k] = v

        # reconstruct recursion_tcbc in a copy
        _rcr_nan_symbol = None
        _rcr_nan_ct = 0
        _rcr_col_dict = {}
        for k, v in recursion_tcbc[new_col_idx].items():
            if str(k).upper() in ['NAN', '<NA>']:
                if _rcr_nan_symbol is not None:
                    raise ValueError(
                        f">=2 nan-like in recursion_tcbc: col idx {new_col_idx}, "
                        f"{recursion_tcbc[new_col_idx]}"
                    )
                _rcr_nan_symbol = k
                _rcr_nan_ct = v
            else:
                _rcr_col_dict[k] = v

        # END manipulation of old_tcbc and recursion tcbc to get the nans out
        # ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

        # now that nans are out, update self.tcbc (old_tcbc) with the new
        # (lower) values in recursion_tcbc, where applicable

        for unq, ct in _old_tcbc_col_dict.items():

            if not _rcr_col_dict.get(unq, 0) <= ct:
                raise AssertionError(
                    f"algorithm failure, count of a unique in a deeper "
                    f"recursion is > the count of the same unique in a "
                    f"higher recursion, can only be <="
                )

            # if unq not in _rcr_col_dict, put 0 into that key for old tcbc
            _old_tcbc_col_dict[unq] = _rcr_col_dict.get(unq, 0)


        # last thing, put the nans into the updated dict
        if _old_tcbc_nan_symbol and _rcr_nan_symbol:
            if not _rcr_nan_ct <= _old_tcbc_nan_ct:
                raise AssertionError(
                    f"algorithm failure, count of nans in a deeper "
                    f"recursion is > the count of nans in a higher "
                    f"recursion, can only be <="
                )
            _old_tcbc_col_dict[_old_tcbc_nan_symbol] = _rcr_nan_ct
        elif _old_tcbc_nan_symbol and not _rcr_nan_symbol:
            # if no nans in _rcr_col_dict, set _old_tcbc_col_dict to 1,
            # placehold so that there is indication that the column
            # originally had nans in it so they will be in delete_instr.
            # 1 will always be below thresh (min=2). much of the code
            # that handles nan processing depends on nan being in tcbc
            # keys, and freq being greater than zero.
            _old_tcbc_col_dict[_old_tcbc_nan_symbol] = 1
        elif not _old_tcbc_nan_symbol and _rcr_nan_symbol:
            raise AssertionError(
                f"algorithm failure, nans have showed up in a deeper "
                f"recursion but are not in the previous recursion -- "
                f"{_rcr_nan_symbol}, type {type(_rcr_nan_symbol)}, "
                f"\nold_tcbc unqs = {old_tcbc[old_col_idx]}, "
                f"\nrecursion_tcbc unqs = {recursion_tcbc[new_col_idx]}"
            )
        else:
            # no nans in either
            pass

        old_tcbc[old_col_idx] = _old_tcbc_col_dict


    del new_col_idx, old_col_idx, unq, ct

    return old_tcbc




