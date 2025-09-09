# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy.typing as npt
from .._type_aliases import (
    InternalXContainer,
    TotalCountsByColumnType,
    InstructionsType
)

import numpy as np

from ._parallelized_row_masks import _parallelized_row_masks
from .._partial_fit._columns_getter import _columns_getter



def _make_row_and_column_masks(
    _X: InternalXContainer,
    _total_counts_by_column: TotalCountsByColumnType,
    _delete_instr: InstructionsType,
    _reject_unseen_values: bool
) -> tuple[npt.NDArray[bool], npt.NDArray[bool]]:
    """Make a mask that indicates which columns to keep and another mask
    that indicates which rows to keep from `X`.

    Columns that are to be deleted are already flagged in `_delete_instr`
    with 'DELETE COLUMN'. For rows, iterate over all columns, and within
    each column iterate over its respective uniques in `_delete_instr`,
    to identify which rows are to be deleted.

    Parameters
    ----------
    _X : InternalXContainer
        The data to be transformed.
    _total_counts_by_column : TotalCountsByColumnTime
        Dictionary holding the uniques and their counts for each column.
    _delete_instr : InstructionsType
        A dictionary that is keyed by column index and the values are
        lists. Within the lists is information about operations to
        perform with respect to values in the column. The following
        items may be in the list:

        -'INACTIVE' - ignore the column and carry it through for all
            other operations

        -Individual values - (in raw datatype format, not converted to
            string) indicates to delete the rows on axis 0 that contain
            that value in that column, including nan-like values

        -'DELETE ALL' - delete every value in the column.

        -'DELETE COLUMN' - perform any individual row deletions that
            need to take place while the column is still in the data,
            then delete the column from the data.
    _reject_unseen_values: bool
        If False, do not even look to see if there are unknown uniques
        in the column. If True, compare uniques in the column against
        uniques in `_COLUMN_UNQ_CT_DICT` and raise exception if there is
        a value not previously seen.

    Returns
    -------
    masks : tuple[np.ndarray[bool], np.ndarray[bool]
        The masks for the rows and columns to keep in binary integer
        format.

    """


    # MAKE COLUMN DELETE MASK ** * ** * ** * ** * ** * ** * ** * ** * **

    _delete_columns_mask = np.zeros(_X.shape[1], dtype=np.uint8)

    for col_idx, _instr in _delete_instr.items():
        if 'DELETE COLUMN' in _instr:
            _delete_columns_mask[col_idx] += 1

    # END MAKE COLUMN DELETE MASK ** * ** * ** * ** * ** * ** * ** * **

    # MAKE ROW DELETE MASK ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # if there is a 'DELETE ALL' just make a mask of all ones and forget
    # about the loop.
    for _instr in _delete_instr.values():
        if 'DELETE ALL' in _instr:
            _delete_rows_mask = np.ones(_X.shape[0], dtype=np.uint8)
            break
    # otherwise build the mask from individual row masks.
    else:
        _ACTIVE_COL_IDXS = []
        for col_idx, _instr in _delete_instr.items():
            if 'INACTIVE' in _instr or len(_instr) == 0:
                continue
            else:
                _ACTIVE_COL_IDXS.append(col_idx)

        # no longer using joblib. even with sending chunks of X instead
        # of single columns across joblib it still wasnt a benefit. The
        # cost of serializing the data is not worth it for the light
        # task of building & summing binary vectors.

        # the original attempt at this was passing all col indices in _X
        # to columns_getter and passing the whole thing as np to _prm.
        # It turned out that this was creating a brief but huge spike in
        # RAM because a full copy of the entire _X was being made. so
        # trade off by pulling smaller chunks of _X and passing to _prm.
        # this gives the benefit of less calls to _columns_getter & _prm
        # than would be if pulling one column at a time, still with some
        # memory spike but much smaller, and get some economy of scale
        # with the speed of scanning a ndarray chunk.
        # number of columns to pull and scan in one pass of the :for: loop
        _n_cols = 10
        _delete_rows_mask = np.zeros(_X.shape[0], dtype=np.uint32)
        for i in range(0, len(_ACTIVE_COL_IDXS), _n_cols):

            _idxs = np.array(_ACTIVE_COL_IDXS)[
                list(range(i, min(i + _n_cols, len(_ACTIVE_COL_IDXS))))
            ]

            _delete_rows_mask += _parallelized_row_masks(
                _columns_getter(_X, tuple(map(int, _idxs.tolist()))),
                {k:v for k,v in _total_counts_by_column.items() if k in _idxs},
                {k:v for k,v in _delete_instr.items() if k in _idxs},
                _reject_unseen_values
            )

        del _ACTIVE_COL_IDXS

    # END MAKE ROW DELETE MASK ** * ** * ** * ** * ** * ** * ** * ** *


    ROW_KEEP_MASK = np.logical_not(_delete_rows_mask)
    del _delete_rows_mask
    COLUMN_KEEP_MASK = np.logical_not(_delete_columns_mask)
    del _delete_columns_mask

    delete_all_msg = \
        lambda j: f"this threshold and recursion depth will delete all {j}"

    if not any(ROW_KEEP_MASK):
        raise ValueError(delete_all_msg('rows'))

    if not any(COLUMN_KEEP_MASK):
        raise ValueError(delete_all_msg('columns'))

    del delete_all_msg

    # ^^^ END BUILD ROW_KEEP & COLUMN_KEEP MASKS ** ** ** ** ** ** ** **


    return ROW_KEEP_MASK, COLUMN_KEEP_MASK




