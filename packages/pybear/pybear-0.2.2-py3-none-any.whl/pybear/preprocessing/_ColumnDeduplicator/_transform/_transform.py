# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    ColumnMaskType,
    InternalXContainer
)

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss



def _transform(
    _X: InternalXContainer,
    _column_mask: ColumnMaskType
) -> InternalXContainer:
    """Remove the duplicate columns from `X` as indicated in the
    `_column_mask` vector.

    Parameters
    ----------
    _X : InternalXContainer of shape (n_samples, n_features)
        The data to be deduplicated. Must be numpy ndarray, pandas
        dataframe, polars dataframe, or scipy sparse csc matrix/array.
    _column_mask : ColumnMaskType
        A boolean vector of shape (n_features,) that indicates which
        columns to keep (True) and which columns to delete (False).

    Returns
    -------
    _X :
        InternalXContainer of shape (n_samples, n_transformed_features) -
        The deduplicated data.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    assert isinstance(
        _X,
        (np.ndarray, pd.DataFrame, pl.DataFrame, ss.csc_array,
         ss.csc_matrix)
    )
    assert isinstance(_column_mask, np.ndarray)
    assert _column_mask.dtype == bool

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    if isinstance(_X, pd.DataFrame):
        return _X.loc[:, _column_mask]
    else:
        return _X[:, _column_mask]





