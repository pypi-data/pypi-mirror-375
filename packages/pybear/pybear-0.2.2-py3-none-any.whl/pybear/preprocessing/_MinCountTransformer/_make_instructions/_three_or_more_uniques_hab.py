# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Literal,
)
from .._type_aliases import DataType



def _three_or_more_uniques_hab(
    _threshold: int,
    _nan_key: float | str | Literal[False],
    _nan_ct: int |  Literal[False],
    _COLUMN_UNQ_CT_DICT: dict[DataType, int],
    _delete_axis_0: bool
) -> list[Literal['DELETE COLUMN'] | DataType]:
    """Make delete instructions for a column with three or more unique
    non-nan values that is handled as bool.

    Because `_handle_as_bool` is True, `_delete_axis_0` matters.

    WHEN 3 items (NOT INCLUDING nan):
    *** BIN INT COLUMNS ARE HANDLED DIFFERENTLY THAN OTHER DTYPES ***
    Most importantly, if a bin int column has a value below threshold,
    the DEFAULT behavior is to not delete the respective rows (whereas
    any other dtype will delete the rows), essentially causing bin int
    columns with insufficient count to just be deleted.

    classify uniques into two classes - 'zero' and 'non-zero'

    if no nans or ignoring
      look at the cts in the 2 classes (bool False & bool True)
      if any below threshold
          if `delete_axis_0`, mark associated values to delete
          DELETE COLUMN
    if not ignoring nans
      if `delete_axis_0`:
          look at the cts in the 2 classes and nan ct
          if any below threshold
              mark associated values to delete
          if either zero or non-zero classes below threshold
              DELETE COLUMN
      if not `delete_axis_0`
          look at the cts in the 2 classes
          if any of zero or non-zero classes below threshold
          DELETE COLUMN
          if no class below threshold, column is staying, look at nan ct,
          if below threshold, delete nan rows

    Parameters
    ----------
    _threshold : int
        The minimum frequency threshold for this column
    _nan_key : float | str | Literal[False]
        The nan value in the column. `_columns_getter` converts all
        nan-likes to numpy.nan.
    _nan_ct : int | Literal[False]
        The frequency of nan in the column
    _COLUMN_UNQ_CT_DICT : dict[DataType, int]
        The value from `_total_cts_by_column` for this column which is a
        dictionary that holds the uniques and their frequencies. Must
        have had nan removed, and must have at least 3 non-nan uniques.
    _delete_axis_0 : bool
        Whether to delete along the sample axis if either or both of the
        boolean values fall below the minimum count threshold.

    Return
    ------
    _instr_list : list[Literal['DELETE COLUMN'] | DataType]
        The row and column operation instructions for this column.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    if 'nan' in list(map(str.lower, map(str, _COLUMN_UNQ_CT_DICT.keys()))):
        raise ValueError(f"nan-like is in _UNQ_CTS_DICT and should not be")

    if not len(_COLUMN_UNQ_CT_DICT) >= 3:
        raise ValueError(f"len(_UNQ_CTS_DICT) not >= 3")

    if (_nan_ct is False) + (_nan_key is False) not in [0, 2]:
        raise ValueError(f"_nan_key is {_nan_key} and _nan_ct is {_nan_ct}")

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # nan should not be in _COLUMN_UNQ_CT_DICT!

    # IF HANDLING AS BOOL, ONLY NEED TO KNOW WHAT IS ZERO, NON-ZERO, AND
    # IF ROWS WILL BE DELETED OR KEPT

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
            # IF ALL UNQS DELETED THIS SHOULD PUT ALL False IN
            # ROW MASK AND CAUSE EXCEPT DURING transform()

            # do this the long way, not by slicing numpy vectors which will
            # turn everything to stuff like np.str_('a'), to preserve
            # the original format of the unqs. _COLUMN_UNQ_CT_DICT could be
            # huge.
            for unq in _COLUMN_UNQ_CT_DICT:

                if float(unq) == 0 and total_zeros < _threshold:
                    _instr_list.append(unq)

                if float(unq) != 0 and total_non_zeros < _threshold:
                    _instr_list.append(unq)

        if (total_zeros < _threshold) or (total_non_zeros < _threshold):
            _instr_list.append('DELETE COLUMN')

    else:  # HAS NANS AND NOT IGNORING

        # bool(np.nan) GIVES True, DONT USE IT!
        # LEAVE nan OUT TO DETERMINE KEEP/DELETE COLUMN
        # REMEMBER THAT nan IS ALREADY OUT OF COLUMN_UNQ_CT_DICT
        # AND STORED SEPARATELY, USE _nan_key & _nan_ct

        if _delete_axis_0:
            # IF ALL UNQS DELETED THIS SHOULD PUT ALL False IN
            # ROW MASK AND CAUSE EXCEPT DURING transform()

            # do this the long way, not by slicing numpy vectors which will
            # turn everything to stuff like np.str_('a'), to preserve
            # the original format of the unqs. _COLUMN_UNQ_CT_DICT could be
            # huge.
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





