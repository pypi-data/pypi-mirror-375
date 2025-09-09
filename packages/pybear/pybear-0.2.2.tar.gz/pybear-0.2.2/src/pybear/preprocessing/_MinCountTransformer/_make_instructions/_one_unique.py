# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#s



from typing import (
    Literal,
)
from .._type_aliases import DataType



def _one_unique(
    _threshold: int,
    _nan_key: float | str | Literal[False],
    _nan_ct: int | Literal[False],
    _COLUMN_UNQ_CT_DICT: dict[DataType, int],
) -> list[Literal['DELETE COLUMN'] | DataType]:
    """Make delete instructions for a column with one unique non-nan
    value.

    *** CONSTANT COLUMNS ARE HANDLED DIFFERENTLY THAN OTHER DTYPES ***
    No matter how many nans are in the column, or whether `ignore_nan`
    is True or False, and no matter how many non-nan values are in the
    column, or if either fall below the threshold, delete the column
    without deleting any rows. After all, it is just a column of
    constants with or without some nans mixed in.

    Parameters
    ----------
    _threshold : int
        The threshold value for the selected column.
    _nan_key : float | str | Literal[False]
        The nan value found in the data. all nan-likes are converted to
        numpy.nan by :func:`_columns_getter`.
    _nan_ct : int | Literal[False]
        The number of nans found in this column.
    _COLUMN_UNQ_CT_DICT : dict[DataType, int]
        The value from `_total_cts_by_column` for this column which is a
        dictionary that holds the uniques and their frequencies. must
        have 1 non-nan key:value pair in it (any nan key:value pair that
        may have been it must have already been removed.)

    Returns
    -------
    _instr_list : list[Literal['DELETE COLUMN']]
        The row and column operation instructions for this column. Can
        only be to delete the entire column without deleting rows.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    if 'nan' in list(map(str.lower, map(str, _COLUMN_UNQ_CT_DICT.keys()))):
        raise ValueError(f"nan-like is in _UNQ_CTS_DICT and should not be")

    if len(_COLUMN_UNQ_CT_DICT) > 1:
        raise ValueError(f"len(_UNQ_CTS_DICT) > 1")

    if (_nan_ct is False) + (_nan_key is False) not in [0, 2]:
        raise ValueError(f"_nan_key is {_nan_key} and _nan_ct is {_nan_ct}")

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # this has been arrived at after several previous iterations where
    # nan values and/or non-nan like values that were below threshold
    # also had the corresponding rows deleted.
    _instr_list = ['DELETE COLUMN']


    return _instr_list





