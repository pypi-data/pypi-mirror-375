# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import DataType

from copy import deepcopy



def _tcbc_merger(
    _DTYPE_UNQS_CTS_TUPLES: list[tuple[str, dict[DataType, int]]],
    _tcbc: dict[int, dict[DataType, int]]
):
    """Merge the `_DTYPE_UNQS_CTS_TUPLES` list from the current
    partial_fit with the `total_counts_by_column` dictionary from any
    previous partial fits.

    If doing fit, or on the first partial_fit, there are no previous
    fits, so the uniques and counts in the unq_cts dictionary of
    `_DTYPE_UNQS_CTS_TUPLES` for the first fit are merged into an empty
    `total_counts_by_column` (tcbc) dictionary.

    When doing multiple partial_fits, combine the results in the unqs/cts
    dictionary of `_DTYPE_UNQS_CTS_TUPLES` from the current partial_fit
    with the unqs/cts results from previous partial_fits that are already
    in the `total_counts_by_column` dictionary. If the column does not
    exist in `total_counts_by_column`, add the entire unq_cts dict in
    that slot. For columns that already exist, if a unique is not in
    that column of `total_counts_by_column`, add the unique and its
    count. If the unique already exists in that column, add the current
    count to the old count.

    Parameters
    ----------
    _DTYPE_UNQS_CTS_TUPLES : list[tuple[str, dict[DataType, int]]]
        A list of tuples, where each tuple holds (dtype, unq_ct_dict)
        for each column in the current {partial_}fit.
    _tcbc : dict[int, dict[DataType, int]]
        The `total_counts_by_column` dictionary, outer keys are the
        column index of the data, values are dicts with keys that are
        the uniques in that column, and the values are the frequency.

    Returns
    -------
    _tcbc : dict[int, dict[DataType, int]]
        The `total_counts_by_column` dictionary updated with the uniques
        and counts in `_DTYPE_UNQS_CTS_TUPLES`.

    """


    # validation - - - - - - - - - - - - - - - - - - - - - -
    assert isinstance(_DTYPE_UNQS_CTS_TUPLES, list)
    for _tuple in _DTYPE_UNQS_CTS_TUPLES:
        assert isinstance(_tuple, tuple)
        assert len(_tuple) == 2
        assert isinstance(_tuple[0], str)
        assert isinstance(_tuple[1], dict)
        # keys could be anything, dont test
        assert all(map(isinstance, _tuple[1].values(), (int for _ in _tuple[1])))

    assert isinstance(_tcbc, dict)
    for _c_idx, _inner in _tcbc.items():
        assert isinstance(_c_idx, int)
        assert isinstance(_inner, dict)
        # keys could be anything, dont test
        assert all(map(isinstance, _inner.values(), (int for _ in _inner)))

    # _DTYPE_UNQS_CTS_TUPLES num columns must be >= tcbc num columns
    assert len(_DTYPE_UNQS_CTS_TUPLES) >= len(_tcbc), \
        f"_tcbc has more columns than _DTYPE_UNQS_CTS_TUPLES"
    # END validation - - - - - - - - - - - - - - - - - - - - - -


    # this is important because of back-talk. verified this needs to stay!
    __tcbc = deepcopy(_tcbc)

    for col_idx, (_dtype, UNQ_CT_DICT) in enumerate(_DTYPE_UNQS_CTS_TUPLES):

        if col_idx not in __tcbc:
            __tcbc[col_idx] = UNQ_CT_DICT
            continue

        # can only get here if col_idx already in tcbc from previous fit

        # reconstruct tcbc[col_idx] in a copy
        # remove any nans from unqs (should only be 1!), and get the count
        _tcbc_nan_symbol = None
        _tcbc_nan_ct = 0
        _tcbc_col_dict = {}
        for k,v in __tcbc[col_idx].items():
            if str(k).upper() in ['NAN', '<NA>']:
                if _tcbc_nan_symbol is not None:
                    raise ValueError(
                        f">=2 nan-like in tcbc: col_idx {col_idx}, "
                        f"\n{__tcbc[col_idx]}"
                    )
                _tcbc_nan_symbol = k
                _tcbc_nan_ct = v
            else:
                _tcbc_col_dict[k] = v
        # END reconstruct tcbc[col_idx] in a copy sans nans -- -- -- --

        # reconstruct UNQ_CT_DICT in a copy
        # remove any nans from unqs (should only be 1!), and get the count
        _ucd_nan_symbol = None
        _ucd_nan_ct = 0
        _ucd_col_dict = {}
        for k,v in UNQ_CT_DICT.items():
            if str(k).upper() in ['NAN', '<NA>']:
                if _ucd_nan_symbol is not None:
                    raise ValueError(
                        f">=2 nan-like in UNQ_CT_DICT: col idx {col_idx}, "
                        f"\n{UNQ_CT_DICT}"
                    )
                _ucd_nan_symbol = k
                _ucd_nan_ct = v
            else:
                _ucd_col_dict[k] = v
        # END reconstruct UNQ_CT_DICT in a copy sans nans -- -- -- -- --

        # merge the two reconstructed dicts w/o nans
        # always add to _tcbc, that holds the totals from previous fits
        for k in (_tcbc_col_dict | _ucd_col_dict).keys():
            if k in _tcbc_col_dict and k in _ucd_col_dict:
                _tcbc_col_dict[k] += _ucd_col_dict[k]
            elif k not in _tcbc_col_dict:   # only in _ucd_col_dict
                _tcbc_col_dict[k] = _ucd_col_dict[k]
            # elif k in _tcbc_col_dict and k not in _ucd_col_dict:
            #     tcbc count does not change

        # merge the nans
        if _tcbc_nan_symbol and _ucd_nan_symbol:
            _tcbc_col_dict[_tcbc_nan_symbol] = (_tcbc_nan_ct + _ucd_nan_ct)
        elif _tcbc_nan_symbol and not _ucd_nan_symbol:
            _tcbc_col_dict[_tcbc_nan_symbol] = _tcbc_nan_ct
        elif not _tcbc_nan_symbol and _ucd_nan_symbol:
            _tcbc_col_dict[_ucd_nan_symbol] = _ucd_nan_ct
        else:
            # no nans in either
            pass

        __tcbc[col_idx] = _tcbc_col_dict


    return __tcbc




