# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Literal,
)
from .._type_aliases import DataType



def _two_uniques_hab(
    _threshold: int,
    _nan_key: float | str | Literal[False],
    _nan_ct: int | Literal[False],
    _COLUMN_UNQ_CT_DICT: dict[DataType, int],
    _delete_axis_0: bool
) -> list[Literal['DELETE COLUMN'] | DataType]:
    """Make delete instructions for a column with two unique non-nan
    values, handling values as booleans.

    WHEN 2 items (NOT INCLUDING nan):
    *** BINARY INT COLUMNS ARE HANDLED DIFFERENTLY THAN OTHER DTYPES ***
    Most importantly, if a binary integer has a value below threshold,
    the DEFAULT behavior is to not delete the respective rows (whereas
    any other dtype will delete the rows), essentially causing bin int
    columns with insufficient count to just be deleted.

    - classify uniques into two classes - 'zero' and 'non-zero'

    - if ignoring nan or no nans
        -- look at cts for the 2 classes, if any ct < thresh, mark all
            associated values for deletion if `delete_axis_0` is True
        -- if any class below thresh, DELETE COLUMN
    - if not ign nan and has nans if `delete_axis_0` is True
        -- treat nan like any other value
        -- look at cts for the 3 unqs (incl nan), if any ct < thresh,
            mark rows for deletion
        -- if any of the non-nan classes below thresh, DELETE COLUMN
    - if not ign nan and has nans if not `delete_axis_0`
        -- look at cts for the 2 non-nan classes, if any ct < thresh,
            DELETE COLUMN
        -- but if keeping the column (both above thresh) and nan ct
            less than thresh, delete the nans

    Parameters
    ----------
    _threshold : int
        The minimum threshold frequency for this column.
    _nan_key : float | str | Literal[False]
        The nan value found in the column. `_columns_getter` converts
        all nan-likes to numpy.nan.
    _nan_ct : int | Literal[False]
        The number of nan-like values found in the column.
    _COLUMN_UNQ_CT_DICT : dict[DataType, int]
        The value from `_total_cts_by_column` for this column, which is
        a dictionary containing the uniques and their frequencies, less
        any nan that may have been in it, and must have 2 non-nan uniques.
    _delete_axis_0 : bool
        Whether to delete the rows associated with any of the values
        that fall below the minimum frequency.

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

    # no nans should be in _COLUMN_UNQ_CT_DICT!

    # SINCE HANDLING AS BOOL, ONLY NEED TO KNOW WHAT IS ZERO, NON-ZERO
    # AND IF ROWS WILL BE DELETED OR KEPT

    # let nums as strs be handled as nums. the unqs in COLUMN_UNQ_CT_DICT
    # are in the raw format as found in X. it is possible that numbers
    # are in string format but MCT correctly diagnosed the column as
    # numbers, and is handling as such.
    total_zeros = dict((zip(
        map(float, _COLUMN_UNQ_CT_DICT.keys()),
        _COLUMN_UNQ_CT_DICT.values()
    ))).get(0, 0)
    total_non_zeros = sum(_COLUMN_UNQ_CT_DICT.values()) - total_zeros

    _instr_list = []
    if not _nan_ct:  # EITHER IGNORING NANS OR NONE IN FEATURE

        if _delete_axis_0:
            # there are only be 2 entries in _UNQ_CT_DICT so iterating
            # is light. need to do this the hard way because numbers
            # could be str formats
            for unq in _COLUMN_UNQ_CT_DICT:

                if float(unq) == 0 and total_zeros < _threshold:
                    _instr_list.append(unq)

                if float(unq) != 0 and total_non_zeros < _threshold:
                    _instr_list.append(unq)

        if (total_zeros < _threshold) or (total_non_zeros < _threshold):
            _instr_list.append('DELETE COLUMN')


    else:  # HAS NANS AND NOT IGNORING

        if _delete_axis_0:
            # there are only be 2 entries in _UNQ_CT_DICT so iterating
            # is light. need to do this the hard way because numbers
            # could be str formats
            for unq in _COLUMN_UNQ_CT_DICT:

                if float(unq) == 0 and total_zeros < _threshold:
                    _instr_list.append(unq)

                if float(unq) != 0 and total_non_zeros < _threshold:
                    _instr_list.append(unq)

            if _nan_ct < _threshold:
                _instr_list.append(_nan_key)

            if (total_zeros < _threshold) or (total_non_zeros < _threshold):
                _instr_list.append('DELETE COLUMN')

        elif not _delete_axis_0:
            # only delete nans if below threshold and not deleting column
            # OTHERWISE IF _nan_ct < _threshold but not delete_axis_0
            # AND NOT DELETE COLUMN THEY WOULD BE KEPT DESPITE
            # BREAKING THRESHOLD
            if (total_zeros < _threshold) or (total_non_zeros < _threshold):
                _instr_list.append('DELETE COLUMN')
            elif _nan_ct < _threshold:
                _instr_list.append(_nan_key)


    del total_zeros, total_non_zeros

    return _instr_list




