# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
)
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
) -> npt.NDArray[Any]:
    """Handles the mechanics of extracting one or more columns from the
    various allowed data container types.

    This supports _find_duplicates. The container must be numpy ndarray,
    pandas dataframe, polars dataframe, or scipy csc only. Return
    extracted column(s) as a numpy array. In the case of scipy sparse,
    the columns are converted to dense.

    Parameters
    ----------
    _X : InternalXContainer
        The data to extract columns from. The container must be numpy
        ndarray, pandas dataframe, polars dataframe, or scipy csc only.
        This module expects `_X` to be in a valid state when passed, and
        will not condition it.
    _col_idxs : int | tuple[int, ...]
        The column index / indices to extract from `_X`.

    Returns
    -------
    _columns : NDArray[Any]
        The column(s) from `_X` corresponding to the given index/indices.

    """


    # validation & conditioning ** * ** * ** * ** * ** * ** * ** * ** *
    assert isinstance(_X,
        (np.ndarray, pd.DataFrame, pl.DataFrame, ss.csc_array,
         ss.csc_matrix)
    )

    # _col_idxs can be an int or a tuple of ints

    assert isinstance(_col_idxs, (int, tuple))
    if isinstance(_col_idxs, int):
        _col_idxs = (_col_idxs,)   # <==== int _col_idx converted to tuple
    assert len(_col_idxs), f"'_col_idxs' cannot be empty"
    for _idx in _col_idxs:
        assert isinstance(_idx, int)
        assert _idx in range(_X.shape[1]), f"col idx out of range"
    # END validation & conditioning ** * ** * ** * ** * ** * ** * ** *

    _col_idxs = sorted(list(_col_idxs))

    if isinstance(_X, np.ndarray):
        _columns = _X[:, _col_idxs]
    elif isinstance(_X, pd.DataFrame):
        _columns = _X.iloc[:, _col_idxs].to_numpy()
    elif isinstance(_X, pl.DataFrame):
        _columns = _X[:, _col_idxs].to_numpy()
    elif hasattr(_X, 'toarray'):    # scipy sparse
        # No longer stacking .indices & .data. need to convert to dense
        # because now pulling chunks instead of single columns. different
        # columns may have different sparsity, which would cause the
        # stacked indices/data to have different len, which cant be
        # stacked nicely in an array.

        # code that converts a ss column to np array
        _columns = _X[:, _col_idxs].tocsc().toarray()

        # old code that converts a ss column to np array
        # _columns = _X.copy().tocsc()[:, [_col_idxs]].toarray().ravel()
        # del _X_wip
        # _columns = np.hstack((c1.indices, c1.data)).reshape((-1, 1))
        # del c1
    else:
        try:
            _columns = np.array(_X[:, _col_idxs])
        except:
            raise TypeError(
                f"invalid data container '{type(_X)}' that could not be "
                f"sliced by numpy-style indexing and converted to ndarray."
            )


    # this assignment must stay here. there was a nan recognition problem
    # that wasnt happening in offline tests of entire data objects
    # holding the gamut of nan-likes but was happening with similar data
    # objects passing thru the CDT machinery. Dont know the reason why,
    # maybe because the columns get parted out, or because they get sent
    # thru the joblib machinery? using nan_mask here and reassigning all
    # nans identified here as np.nan resolved the issue.
    # np.nan assignment excepts on dtype int array, so ask for forgiveness
    try:
        _columns[nan_mask(_columns)] = np.nan
    except:
        pass

    # 25_05_24 pd numeric with junky nan-likes are coming out of here as
    # dtype object. since _columns_getter produces an intermediary container
    # that is used to find constants and doesnt impact the container
    # coming out of transform, ok to let that condition persist.

    return _columns





