# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Literal,
)
from .._type_aliases import DataType



def _two_uniques_not_hab(
    _threshold: int,
    _nan_key: float | str | Literal[False],
    _nan_ct: int | Literal[False],
    _COLUMN_UNQ_CT_DICT: dict[DataType, int]
) -> list[Literal['DELETE COLUMN'] | DataType]:
    """Make delete instructions for a column with two unique non-nan
    values that is not handled as boolean (could be strings or floats.)

    - if ignoring nan or no nans
        -- look at cts for the 2 unqs, if any ct < thresh, mark rows
            for deletion
        -- if any below thresh, DELETE COLUMN
    - if not ign nan and has nans
        -- treat nan like any other value
        -- look at cts for the 3 unqs (incl nan), if any ct < thresh,
            mark rows for deletion
        -- if any of the non-nan values below thresh, DELETE COLUMN

    Parameters
    ----------
    _threshold : int
        The minimum threshold frequency for this column.
    _nan_key : float | str | Literal[False]
        The nan value found in the column in its original dtype.
        `_columns_getter` converts all nan-like values to numpy.nan.
    _nan_ct : int | Literal[False]
        The number of nan-like values found in the column.
    _COLUMN_UNQ_CT_DICT : dict[DataType, int]
        The value from `_total_cts_by_column` for this column which is a
        dictionary containing the uniques and their frequencies, less
        any nan that may have been in it, and must have 2 non-nan
        uniques.

    Returns
    -------
    _instr_list : list[Literal['DELETE COLUMN'] | DataType]
        The row and column operations for this column.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    if 'nan' in list(map(str.lower, map(str, _COLUMN_UNQ_CT_DICT.keys()))):
        raise ValueError(f"nan-like is in _UNQ_CTS_DICT and should not be")

    if len(_COLUMN_UNQ_CT_DICT) != 2:
        raise ValueError(f"len(_UNQ_CTS_DICT) != 2")

    if (_nan_ct is False) + (_nan_key is False) not in [0, 2]:
        raise ValueError(f"_nan_key is {_nan_key} and _nan_ct is {_nan_ct}")

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # nans should not be in _COLUMN_UNQ_CT_DICT!

    _instr_list = []
    if not _nan_ct:  # EITHER IGNORING NANS OR NONE IN FEATURE

        _ctr = 0
        for unq, ct in _COLUMN_UNQ_CT_DICT.items():
            if ct < _threshold:
                _ctr += 1
                _instr_list.append(unq)
        if _ctr > 0:
            _instr_list.append('DELETE COLUMN')
        del _ctr, unq, ct


    else:  # HAS NANS AND NOT IGNORING

        _ctr = 0
        for unq, ct in _COLUMN_UNQ_CT_DICT.items():
            if ct < _threshold:
                _ctr += 1
                _instr_list.append(unq)

        if _nan_ct < _threshold:
            _instr_list.append(_nan_key)

        if _ctr > 0:
            _instr_list.append('DELETE COLUMN')
        del _ctr, unq, ct


    return _instr_list




