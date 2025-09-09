# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    InternalXContainer,
    RemovedColumnsType,
    FeatureNamesInType
)

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss



def _inverse_transform(
    _X: InternalXContainer,
    _removed_columns: RemovedColumnsType,
    _feature_names_in: FeatureNamesInType | None
) -> InternalXContainer:
    """Revert transformed data back to its original state.

    IM cannot account for any nan-like values that may have been in the
    original data (unless the column was all nans).

    Parameters
    ----------
    _X : InternalXContainer of shape (n_samples, n_transformed_features)
        A transformed data set. Any appended intercept column (via
        a `keep` dictionary) needs to be removed before coming into this
        module. The container must be numpy ndarray, pandas dataframe,
        polars dataframe, or scipy csc only.
    _removed_columns : RemovedColumnsType
        The keys are the indices of constant columns removed from the
        original data, the respective values are the constant that was
        in that column.
    _feature_names_in : FeatureNamesInType | None
        The feature names found during fitting, if `X` was passed in a
        container with a header.

    Returns
    -------
    X_tr : InternalXContainer of shape (n_samples, n_features)
        Transformed data reverted to its original state.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    assert isinstance(_X,
        (np.ndarray, pd.DataFrame, pl.DataFrame, ss.csc_matrix,
         ss.csc_array)
    )
    assert isinstance(_removed_columns, dict)
    for k, v in _removed_columns.items():
        assert isinstance(k, int)
    if _feature_names_in is not None:
        assert isinstance(_feature_names_in, np.ndarray)
        assert all(
            map(isinstance, _feature_names_in, (str for _ in _feature_names_in))
        )
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # retain what the original format was
    _og_X_format = type(_X)

    # if data is a pd/pl df, convert to numpy
    if isinstance(_X, (pd.DataFrame, pl.DataFrame)):
        # remove any header that may be on this df, feature_names_in
        # will go on if available, otherwise container default header
        _X = _X.to_numpy()

    # must do this from left to right!
    # use the _removed_columns dict to insert columns with the original
    # constant values
    if isinstance(_X, np.ndarray):   # pd/pl was converted to np
        for _rmv_idx, _value in _removed_columns.items():  # this was sorted above
            _X = np.insert(
                _X,
                _rmv_idx,
                np.full((_X.shape[0],), _value),
                axis=1
            )
    elif isinstance(_X, (ss.csc_array, ss.csc_matrix)):
        for _rmv_idx, _value in _removed_columns.items():  # this was sorted above
            _X = ss.hstack(
                (
                    _X[:, :_rmv_idx],
                    ss.csc_matrix(np.full((_X.shape[0], 1), _value)),
                    _X[:, _rmv_idx:]
                ),
                format="csc",
                dtype=_X.dtype
            )
    else:
        raise Exception


    _X = _og_X_format(_X) if _og_X_format is not np.ndarray else _X

    # if was a dataframe and feature names are available, reattach
    if _feature_names_in is not None \
            and _og_X_format in [pd.DataFrame, pl.DataFrame]:
        _X.columns = _feature_names_in


    return _X



