# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy.typing as npt
from .._type_aliases import (
    TotalCountsByColumnType,
    InstructionsType
)

import numpy as np

from ....utilities._nan_masking import nan_mask



def _parallelized_row_masks(
    _X_CHUNK: npt.NDArray,
    _UNQ_CT_DICT: TotalCountsByColumnType,
    _instr: InstructionsType,
    _reject_unseen_values: bool
) -> npt.NDArray[np.uint32]:
    """Create mask indicating row indices to delete for a chunk of
    columns from X.

    Use the instructions provided in `_instr` to get the uniques to
    delete from a column. For each unique to be deleted from that column,
    locate the positions of that unique within the column and store the
    locations in a vector that has the same number of rows as the chunk.
    Sum the vectors from each unique to create a vector that indicates
    all the row indices to be deleted from that column. Finally, sum the
    vectors for each column in the array to produce a single vector that
    indicates row indices to delete from this chunk.

    Simultaneously, if rejecting unseen values, compare the uniques
    in `_UNQ_CT_DICT` (which were found during fit) against the uniques
    currently found in each column (during transform, this is a transform
    sub-module). Raise exception if rejecting unseen values and there
    are new uniques.

    Parameters
    ----------
    _X_CHUNK : npt.NDArray
        A block of columns from X. Must be 2D numpy array.
    _UNQ_CT_DICT : TotalCountsByColumnType
        The `_total_counts_by_column` entries for the column(s) in the
        chunk.
    _instr : InstructionsType
        The `_delete_instr` entries for the column(s) in the chunk.
    _reject_unseen_values : bool
        If False, do not even look to see if there are unknown uniques.
        If True, compare uniques in each column against uniques in
        `_UNQ_CT_DICT` and raise exception if there is a value not
        previously seen.

    Returns
    -------
    CHUNK_ROW_MASK : npt.NDArray[np.uint32]
        A 1D mask of rows to delete from X based on the instructions in
        `_delete_instr` for these columns.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    assert isinstance(_X_CHUNK, np.ndarray)
    assert len(_X_CHUNK.shape) == 2
    assert isinstance(_UNQ_CT_DICT, dict)
    assert all(map(isinstance, _UNQ_CT_DICT.keys(), (int for _ in _instr)))
    assert all(map(isinstance, _UNQ_CT_DICT.values(), (dict for _ in _UNQ_CT_DICT)))
    assert isinstance(_instr, dict)
    assert all(map(isinstance, _instr.keys(), (int for _ in _instr)))
    assert all(map(isinstance, _instr.values(), (list for _ in _instr)))

    assert _X_CHUNK.shape[1] == len(_UNQ_CT_DICT) == len(_instr)
    assert np.array_equal(list(_UNQ_CT_DICT.keys()), list(_instr.keys()))

    assert isinstance(_reject_unseen_values, bool)

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # create an empty mask to hold the sum of the mask vectors for all
    # columns
    CHUNK_ROW_MASK = np.zeros(_X_CHUNK.shape[0], dtype=np.uint32)

    # cannot only use the column indices from range(_X_CHUNK.shape[1])!
    # must use the column indices that are in the keys of unq_cts/instr
    # and use the enumerate idx to pull the column from _X_CHUNK
    for _chunk_c_idx, _x_c_idx in enumerate(_UNQ_CT_DICT):

        # create an empty mask to hold the sum of the masks for each unq
        # in the column
        COLUMN_ROW_MASK = np.zeros(_X_CHUNK.shape[0], dtype=np.uint8)

        # reject_unseen_values_mask
        if _reject_unseen_values:
            RUV_MASK = np.zeros(_X_CHUNK.shape[0], dtype=np.uint8)

        # pull one column from the chunk
        _X_COLUMN = _X_CHUNK[:, _chunk_c_idx]

        # this counts how many times 'nan' is a key in one column in
        # UNQ_CT_DICT. there should be at most one in any column
        _nan_ctr = 0
        # cycle thru the uniques that were found for this column in fit
        for unq in _UNQ_CT_DICT[_x_c_idx]:

            # create an empty mask for this one unique on this one column.
            # this will get populated with matches in the column and be
            # used to increment both the COLUMN RUV vector and the COLUMN
            # MASK
            MASK_ON_X_COLUMN_UNQ = np.zeros(_X_COLUMN.shape[0], dtype=np.uint8)

            # the unq in UNQ_CT_DICT is not necessarily in _delete_instr.
            # if it is, and/or if rejecting unseen, need to retain this
            # vector.
            if (unq in _instr[_x_c_idx] or str(unq) in map(str, _instr[_x_c_idx])) \
                    or _reject_unseen_values:

                if str(unq).lower() == 'nan':
                    _nan_ctr += 1
                    if _nan_ctr > 1:
                        raise ValueError(f">=2 nans in UNQ_CT_DICT[{_x_c_idx}]")
                    MASK_ON_X_COLUMN_UNQ += nan_mask(_X_COLUMN)
                else:
                    MASK_ON_X_COLUMN_UNQ += (_X_COLUMN == unq)


            if unq in _instr[_x_c_idx] or str(unq) in map(str, _instr[_x_c_idx]):
                COLUMN_ROW_MASK += MASK_ON_X_COLUMN_UNQ

            if _reject_unseen_values:
                RUV_MASK += MASK_ON_X_COLUMN_UNQ

        del _nan_ctr, MASK_ON_X_COLUMN_UNQ

        # python sum is not working correctly on RUV_MASK when has a
        # np dtype, need to use np sum to get the correct result. Or, could
        # convert RUV_MASK with .astype(int), and py sum works correctly.
        # Could go either way with this fix.

        # all the uniques found during fit should cumulatively mask all
        # of _X_COLUMN (RUV_MASK should be all ones). any zero value in
        # RUV_MASK means that value is not in UNQ_CT_DICT, which means
        # the value was not seen during fit.
        if _reject_unseen_values and np.sum(RUV_MASK) != _X_COLUMN.shape[0]:

            # build things to display info about unseen values ** * ** *
            _UNSEEN = _X_COLUMN[np.logical_not(RUV_MASK)]

            try:
                _UNSEEN_UNQS = np.unique(_UNSEEN.astype(np.float64))
            except:
                _UNSEEN_UNQS = np.unique(_UNSEEN.astype(str))

            _UNSEEN_UNQS = _UNSEEN_UNQS.astype(_X_COLUMN.dtype)

            del _UNSEEN
            # END build things to display info about unseen values ** *

            if len(_UNSEEN_UNQS) > 10:
                _UNSEEN_UNQS = f"{_UNSEEN_UNQS[:10]} + others"

            raise ValueError(f"Transform data has values not seen "
                f"during fit --- "
                f"\ncolumn index = {_x_c_idx}"
                f"\nunseen values = {_UNSEEN_UNQS}")

        try:
            del RUV_MASK
        except:
            pass

        # COLUMN_ROW_MASK was incremented for each unq hit found in the
        # column. so right now COLUMN_ROW_MASK shows all the row indices
        # in this column that will cause a row to be removed from the
        # big X. increment the CHUNK_ROW_MASK with the hits for this
        # column.
        CHUNK_ROW_MASK += COLUMN_ROW_MASK

        del COLUMN_ROW_MASK


    return CHUNK_ROW_MASK






