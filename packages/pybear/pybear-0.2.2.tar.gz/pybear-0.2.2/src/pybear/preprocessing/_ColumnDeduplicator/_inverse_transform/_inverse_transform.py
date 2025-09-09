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
    """Revert deduplicated data back to its original state.

    CDT cannot restore any nan-like values that may have been in the
    original data (unless the column was all nans.)

    Parameters
    ----------
    _X : InternalXContainer of shape (n_samples, n_transformed_features)
        A deduplicated data set. The container must be numpy ndarray,
        pandas dataframe, polars dataframe, or scipy csc only.
    _removed_columns : RemovedColumnsType
        The keys are the indices of duplicate columns removed from the
        original data, indexed by their column location in the original
        data; the values are the column index in the original data of
        the respective duplicate that was kept.
    _feature_names_in : FeatureNamesInType | None
        The feature names found during fitting, if X was passed in a
        container with a header.

    Returns
    -------
    X_tr : InternalXContainer of shape (n_samples, n_features)
        Transformed data reverted to its original state.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    assert isinstance(_X,
        (np.ndarray, pd.DataFrame, pl.DataFrame, ss.csc_matrix,
        ss.csc_array)
    )
    assert isinstance(_removed_columns, dict)
    for k, v in _removed_columns.items():
        assert isinstance(k, int) and isinstance(v, int)
    if _feature_names_in is not None:
        assert isinstance(_feature_names_in, np.ndarray)
        assert all(
            map(isinstance, _feature_names_in, (str for _ in _feature_names_in))
        )
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    # retain what the original format was
    _og_X_format = type(_X)

    # if data is a pd/pl df, convert to numpy
    if isinstance(_X, (pd.DataFrame, pl.DataFrame)):
        # remove any header that may be on this df, feature_names_in
        # will go on if available, otherwise container default header
        _X = _X.to_numpy()

    # confirmed via pytest 24_10_10 this need to stay
    # assure _removed_columns keys are accessed ascending
    for k in sorted(_removed_columns.keys()):
        _removed_columns[int(k)] = int(_removed_columns.pop(k))

    # insert blanks into the given data to get dimensions back to original,
    # so indices will match the indices of _parent_dict.
    # must do this from left to right!
    _blank = np.empty((_X.shape[0], 1))
    if isinstance(_X, np.ndarray):
        for _rmv_idx in _removed_columns:  # this was sorted above
            _X = np.insert(
                _X,
                _rmv_idx,
                _blank.ravel(),  # ravel is important
                axis=1
            )
    elif isinstance(_X, (ss.csc_matrix, ss.csc_array)):
        for _rmv_idx in _removed_columns:  # this was sorted above
            _X = ss.hstack(
                (_X[:, :_rmv_idx], ss.csc_matrix(_blank), _X[:, _rmv_idx:]),
                format="csc",
                dtype=_X.dtype
            )
    else:
        raise Exception

    del _blank


    # use the _removed_columns dict to put in copies of the parent column
    if isinstance(_X, np.ndarray):
        # df was converted to array above
        for _dupl_idx, _parent_idx in _removed_columns.items():
            _X[:, _dupl_idx] = _X[:, _parent_idx].copy()
    elif isinstance(_X, (ss.csc_matrix, ss.csc_array)):
        for _dupl_idx, _parent_idx in _removed_columns.items():
            _X[:, [_dupl_idx]] = _X[:, [_parent_idx]].copy()
    else:
        raise Exception


    _X = _og_X_format(_X) if _og_X_format is not np.ndarray else _X

    # if was a dataframe and feature names are available, reattach
    if _feature_names_in is not None \
            and _og_X_format in [pd.DataFrame, pl.DataFrame]:
        _X.columns = _feature_names_in


    return _X



