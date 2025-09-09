# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
    Literal
)
from .._type_aliases import (
    KeepType,
    ConstantColumnsType,
    FeatureNamesInType
)
from ...__shared._type_aliases import XContainer

import warnings

import numpy as np
import pandas as pd
import polars as pl



def _manage_keep(
    _keep: KeepType,
    _X: XContainer,
    _constant_columns: ConstantColumnsType,
    _n_features_in: int,
    _feature_names_in: FeatureNamesInType,
    _rand_idx: int
) -> Literal['none'] | dict[str, Any] | int:
    """Before going into `_make_instructions`, process some of the
    mapping of `keep` to a column index and validate against
    `_constant_columns`.

    Helps to simplify `_make_instructions` and makes for easier testing.

    If dict[int, Any], just pass through without validation.
    If callable, convert to int and verify is a constant column.
    If a feature name, convert to int and verify is a constant column.
    If a `keep` literal ('first', 'last', 'random'):
        if there are no constant columns, warn and set `keep` to 'none'
        otherwise map to a column index.
    If `keep` literal 'none':
        if there are no constant columns, warn, otherwise pass through.
    If `keep` is integer, verify is a constant column.


    FROM columns & keep VALIDATION, WE KNOW ** * ** * ** * ** * ** * **

    `feature_names_in_` could be:
        type(None),
        Sequence[str] whose len == X.shape[1]

    `keep` could be
        Literal['first', 'last', 'random', 'none'],
        dict[str, Any],
        callable(X),
        int,
        a feature name

    if `keep` is str in ('first', 'last', 'random', 'none'):
    	if 'feature_names_in_' is not None, keep literal is not in it
    if `keep` is dict:
    	len == 1
    	key is str
    	warns if 'feature_names_in_' is not None and key is in it
        value cannot be callable, cannot be non-str sequence
    if `keep` is callable(X):
    	output is int
    	output is not bool
    	output is in range(X.shape[1])
    if `keep` is number:
    	is int
    	is not bool
    	is in range(X.shape[1])
    if `keep` is str not in literals:
    	`feature_names_in_` cannot be None
    	`keep` must be in `feature_names_in_`

    END WHAT WE KNOW FROM columns & keep VALIDATION ** * ** * ** * ** *

    RULES FOR `_manage_keep`:

    `feature_names_in_` is not changed

    `keep`:
    --'first', 'last', 'random'         converted to int, validated--
    --'none'                            passes thru--
    --dict[str, Any]                    passes thru--
    --callable(X)                       converted to int, validated--
    --int                               validated--
    --a feature name                    converted to int, validated--

    keep can only leave here as dict[int, Any], int, or Literal['none']

    Parameters
    ----------
    _keep : KeepType
        The strategy for handling the constant columns. See 'The keep
        Parameter' section for a lengthy explanation of the `keep`
        parameter.
    _X : XContainer of shape (n_samples, n_features)
        The data that was searched for constant columns. The data need
        not be InternalXContainer.
    _constant_columns : ConstantColumnsType
        Constant column indices and their values found in all partial
        fits.
    _n_features_in : int
        Number of features in the fitted data before transform.
    _feature_names_in : npt.NDArray[str] | None
        The names of the features as seen during fitting. Only accessible
        if `X` is passed to `fit` or `partial_fit` in a container that
        has a header.
    _rand_idx : int
        Instance attribute that specifies the random column index to
        keep when `keep` is 'random'. This value must be static on calls
        to `transform`.

    Returns
    -------
    __keep : dict[int, Any] | int | Literal['none']
        `_keep` converted to integer for callable, 'first', 'last',
        'random', or feature name. `__keep` can only return as an
        integer, dict, or Literal['none']

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # dont need to validate 'keep' this is the first thing 'keep' sees
    # after _validate in both partial_fit and transform (the only places
    # where this is called)

    assert isinstance(_X, (np.ndarray, pd.DataFrame, pl.DataFrame)) \
        or hasattr(_X, 'toarray')

    assert isinstance(_n_features_in, int)
    assert _n_features_in > 0
    assert isinstance(_feature_names_in, (np.ndarray, type(None)))
    if isinstance(_feature_names_in, np.ndarray):
        assert len(_feature_names_in) == _n_features_in

    assert isinstance(_constant_columns, dict)
    if len(_constant_columns):
        assert all(map(
            isinstance, _constant_columns, (int for _ in _constant_columns)
        ))
        assert min(_constant_columns) >= 0
        assert max(_constant_columns) < _n_features_in

    if _rand_idx is not None:
        assert _rand_idx in range(_n_features_in)

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    if isinstance(_keep, dict):
        __keep = _keep
    elif callable(_keep):
        __keep = _keep(_X)
        if __keep not in _constant_columns:
            raise ValueError(
                f"'keep' callable has returned an integer column index "
                f"({__keep}) that is not a column of constants. \nconstant "
                f"columns: {_constant_columns}"
            )
    elif isinstance(_keep, str) and _feature_names_in is not None and \
            _keep in _feature_names_in:
        # if keep is str, convert to idx
        # validity of keep as feature str (header was passed, keep is in
        # header) should have been validated in _validation > _keep_and_columns
        __keep = int(np.arange(_n_features_in)[_feature_names_in == _keep][0])
        # this is the first place where we can validate whether the _keep
        # feature str is actually a constant column in the data
        if __keep not in _constant_columns:
            raise ValueError(
                f"'keep' was passed as '{_keep}' corresponding to column "
                f"index {__keep} which is not a column of constants. "
                f"\nconstant columns: {_constant_columns}"
            )
    elif _keep in ('first', 'last', 'random', 'none'):
        _sorted_constant_column_idxs = sorted(list(_constant_columns))
        if len(_sorted_constant_column_idxs) == 0:
            warnings.warn(
                f"ignoring :param: keep literal '{_keep}', there are no "
                f"constant columns"
            )
            __keep = 'none'
        elif _keep == 'first':
            __keep = int(_sorted_constant_column_idxs[0])
        elif _keep == 'last':
            __keep = int(_sorted_constant_column_idxs[-1])
        elif _keep == 'random':
            __keep = _rand_idx
        elif _keep == 'none':
            __keep = 'none'
    elif isinstance(_keep, int):
        # this is the first place where we can validate whether the
        # _keep int is actually a constant column in the data
        __keep = _keep
        if __keep not in _constant_columns:
            raise ValueError(
                f"'keep' was passed as column index ({_keep}) which is not a "
                f"column of constants. \nconstant columns: {_constant_columns}"
            )
    else:
        raise AssertionError(f"algorithm failure. invalid 'keep': {_keep}")


    # __keep could be dict[str, Any], int, or 'none'
    return __keep






