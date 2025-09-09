# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy.typing as npt
from .._type_aliases import InternalXContainer

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

from ....utilities._nan_masking import nan_mask



def _columns_getter(
    _X: InternalXContainer,
    _col_idxs: int | tuple[int, ...]
) -> npt.NDArray:
    """Handles the mechanics of extracting one or more columns from the
    various allowed data container types.

    This supports `_get_dtypes_unqs_cts` and `_make_row_and_column_masks`.
    Container must be numpy array, pandas dataframe, polars dataframe,
    or scipy csc matrix/array. Return extracted column(s) as a numpy
    array. In the case of scipy sparse, the columns are converted to
    dense.

    Parameters
    ----------
    _X : InternalXContainer
        The data to undergo minimum frequency thresholding. There is no
        conditioning of the data here and this module expects to receive
        it in suitable form.
    _col_idxs : int | tuple[int, ...]
        The column index / indices to extract from `_X`.

    Returns
    -------
    _columns : NDArray
        The column(s) from `_X` corresponding to the given index/indices.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    assert isinstance(_X, (np.ndarray, pd.DataFrame,
        pl.DataFrame, ss.csc_array, ss.csc_matrix))

    assert isinstance(_col_idxs, (int, tuple))
    if isinstance(_col_idxs, int):
        _col_idxs = (_col_idxs,)   # <==== int _col_idx converted to tuple
    assert len(_col_idxs), f"'_col_idxs' cannot be empty"
    for _idx in _col_idxs:
        assert isinstance(_idx, int)
        assert _idx in range(_X.shape[1]), f"col idx out of range"
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    _col_idxs = sorted(list(_col_idxs))

    if isinstance(_X, np.ndarray):
        _columns = _X[:, _col_idxs]
    elif isinstance(_X, pd.DataFrame):
        _columns = _X.iloc[:, _col_idxs].to_numpy()
    elif isinstance(_X, pl.DataFrame):
        _columns = _X[:, _col_idxs].to_numpy()
    elif isinstance(_X, (ss.csc_array, ss.csc_matrix)):
        _columns = _X[:, _col_idxs].toarray()
    else:
        try:
            _columns = np.array(_X[:, _col_idxs])
        except:
            raise TypeError(
                f"invalid data container '{type(_X)}' that could not be "
                f"sliced by numpy-style indexing and converted to ndarray."
            )

    # this assignment must stay here.
    # np.nan assignment excepts on dtype int array, so ask for forgiveness
    try:
        _columns[nan_mask(_columns)] = np.nan
    except:
        pass

    return _columns





