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

    This supports :func:`_find_constants`. The container must be numpy
    ndarray, pandas dataframe, polars dataframe, or scipy csc only.
    Return extracted column(s) as a numpy array. In the case of scipy
    sparse, the columns are converted to dense.

    Parameters
    ----------
    _X : InternalXContainer of shape (n_samples, n_features)
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


    # validation ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
    assert isinstance(_X,
        (np.ndarray, pd.DataFrame, pl.DataFrame, ss.csc_array,
         ss.csc_matrix)
    )

    assert isinstance(_col_idxs, (int, tuple))
    if isinstance(_col_idxs, int):
        _col_idxs = (_col_idxs,)   # <==== int _col_idx converted to tuple
    assert len(_col_idxs), f"'_col_idxs' cannot be empty"
    for _idx in _col_idxs:
        assert isinstance(_idx, int)
        assert _idx in range(_X.shape[1]), f"col idx out of range"
    # END validation ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

    _col_idxs = sorted(list(_col_idxs))

    if isinstance(_X, np.ndarray):
        _columns = _X[:, _col_idxs]
    elif isinstance(_X, pd.DataFrame):
        _columns = _X.iloc[:, _col_idxs].to_numpy()
    elif isinstance(_X, pl.DataFrame):
        _columns = _X[:, _col_idxs].to_numpy()
    elif hasattr(_X, 'toarray'):    # scipy sparse, must be csc
        # there are a lot of ifs, ands, and buts if trying to determine
        # if a column is constant just from the dense indices and values.
        # the most elegant way is just to convert to dense, at the expense
        # of some memory swell.

        # code that converts a ss column to np array
        _columns = _X[:, _col_idxs].tocsc().toarray()

        # old code that stacks ss column indices and values
        # c1 = _X[:, [_col_idx]]
        # column = np.hstack((c1.indices, c1.data))
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
    # objects passing thru the IM machinery. Dont know the reason why.
    # using nan_mask here and reassigning all nans identified here as
    # np.nan resolved the issue. np.nan assignment excepts on dtype int
    # array, so ask for forgiveness
    try:
        _columns[nan_mask(_columns)] = np.nan
    except:
        pass

    # 25_05_22 pd numeric with junky nan-likes are coming out of here
    # as dtype object. since _columns_getter produces an intermediary
    # container that is used to find constants and doesnt impact the
    # container coming out of transform, ok to let that condition
    # persist.

    return _columns





