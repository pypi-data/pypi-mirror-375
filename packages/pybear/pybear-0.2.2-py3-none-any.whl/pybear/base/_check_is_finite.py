# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    TypeAlias,
)
import numpy.typing as npt

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

from ..utilities._nan_masking import nan_mask
from ..utilities._inf_masking import inf_mask
from ._copy_X import copy_X as _copy_X



SparseTypes: TypeAlias = (
    ss._csr.csr_matrix | ss._csc.csc_matrix | ss._coo.coo_matrix
    | ss._dia.dia_matrix | ss._bsr.bsr_matrix | ss._csr.csr_array
    | ss._csc.csc_array | ss._coo.coo_array | ss._dia.dia_array
    | ss._bsr.bsr_array
)

XContainer: TypeAlias = npt.NDArray | pd.DataFrame | SparseTypes



def check_is_finite(
    X: XContainer,
    allow_nan:bool = True,
    allow_inf:bool = True,
    cast_inf_to_nan:bool = True,
    standardize_nan:bool = True,
    copy_X:bool = True
) -> XContainer:
    """Look for any nan-like and/or infinity-like values in `X`.

    If any of these are disallowed then raise a ValueError if any are
    present.

    If `cast_inf_to_nan` is True, all infinity-like values will be cast
    to np.nan, otherwise they are left as is.

    If `standardize_nan` is True, all nan-like values will be cast to
    np.nan, otherwise they are left as is.

    `X` cannot be a Python builtin iterable, like list or set. `X` must
    have a copy method.

    Parameters
    ----------
    X : XContainer of shape (n_samples, n_features) or (n_samples,)
        The data to be searched for nan-like and infinity-like values.
    allow_nan : bool, default=True
        If nan-like values are found and this parameter is set to False
        then raise a ValueError.
    allow_inf : bool, default=True
        If infinity-like values are found and this parameter is set to
        False then raise a ValueError.
    cast_inf_to_nan : bool, default=True
        If True, all infinity-like values will be cast to np.nan.
    standardize_nan : bool, default=True
        If True, all nan-like values will be cast to np.nan.
    copy_X : bool
        If True, make a copy of `X` if any infinity-likes are cast to
        np.nan or if any nan-likes are cast to np.nan. If False, operate
        directly on the passed `X` object. Only applicable if either
        `cast_inf_to_nan` or `standardize_nan` is True and there are
        infinity-like or nan-like values in the data.

    Returns
    -------
    X : npt.NDArray | pd.DataFrame | SparseTypes
        The originally passed data with all checks performed and any
        replacements made.

    Notes
    -----

    **Type Aliases**

    SparseTypes:
        ss._csr.csr_matrix | ss._csc.csc_matrix | ss._coo.coo_matrix
        | ss._dia.dia_matrix | ss._bsr.bsr_matrix | ss._csr.csr_array
        | ss._csc.csc_array | ss._coo.coo_array | ss._dia.dia_array
        | ss._bsr.bsr_array

    XContainer:
        numpy.ndarray | pandas.DataFrame | SparseTypes

    Examples
    --------
    >>> from pybear.base import check_is_finite
    >>> import numpy as np
    >>> X = np.random.uniform(0, 1, (5, 3))
    >>> kwargs = {'allow_nan': False, 'allow_inf': False,
    ...   'cast_inf_to_nan': False, 'standardize_nan': False}
    >>> out = check_is_finite(X, **kwargs)
    >>> type(out)
    <class 'numpy.ndarray'>
    >>> X[0, 0] = np.nan
    >>> try:
    ...     check_is_finite(X, **kwargs)
    ... except Exception as e:
    ...     print(repr(e))
    ValueError("'X' has nan-like values but are disallowed")

    """

    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    if not hasattr(X, 'copy') and not hasattr(X, 'clone'):
        raise TypeError(f"'X' must have a 'copy' or 'clone' method.")

    if isinstance(X, (dict, str, list, set, tuple)):
        raise TypeError(
            f"'X' cannot be a python builtin iterable, got {type(X)}."
        )

    for _param in (
        allow_nan, allow_inf, cast_inf_to_nan, standardize_nan, copy_X
    ):
        if not isinstance(_param, bool):
            raise TypeError(
                f":param: {_param} must be boolean, got {type(_param)}."
            )

    if not allow_nan and standardize_nan:
        raise ValueError(
            f"if :param: allow_nan is False, then :param: standardize_nan "
            f"must also be False."
        )

    if not allow_inf and cast_inf_to_nan:
        raise ValueError(
            f"if :param: allow_inf is False, then :param: cast_inf_to_nan "
            f"must also be False."
        )

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # if allowing everything and not changing anything, just skip out
    if all((allow_nan, allow_inf)) and not any((cast_inf_to_nan, standardize_nan)):
        return X

    # reasons we need to check for nans
    if not allow_nan or standardize_nan:
        NAN_MASK = nan_mask(X)
        has_nan = np.any(NAN_MASK)
    else:
        # if we dont need to look for nans, pretend X doesnt have any
        has_nan = False

    # reasons we need to check for infinity
    if not allow_inf or cast_inf_to_nan:
        INF_MASK = inf_mask(X)
        has_inf = np.any(INF_MASK)
    else:
        # if we dont need to look for infs, pretend X doesnt have any
        has_inf = False

    # if X is clean, then there is nothing to do, just return
    if not has_nan and not has_inf:
        try:
            del NAN_MASK
        except:
            pass

        try:
            del INF_MASK
        except:
            pass

        return X

    if not cast_inf_to_nan:
        try:
            del INF_MASK
        except:
            pass

    if not standardize_nan:
        try:
            del NAN_MASK
        except:
            pass

    if has_nan and not allow_nan:
        raise ValueError(f"'X' has nan-like values but are disallowed")

    if has_inf and not allow_inf:
        raise ValueError(f"'X' has infinity-like values but are disallowed")

    if not standardize_nan and not cast_inf_to_nan:
        return X

    # copy_X matters only if we have nans and are  standardizing nans
    # or we have infs and are converting over to nan

    if ((has_nan and standardize_nan) or (has_inf and cast_inf_to_nan)) and copy_X:
        _X = _copy_X(X)
    else:
        _X = X

    if has_nan and standardize_nan:
        if hasattr(_X, 'toarray'):   # scipy sparse
            _X.data[NAN_MASK] = np.nan
        elif hasattr(_X, 'clone'):  # polars
            _columns = _X.columns
            _dtypes = _X.dtypes
            _X = _X.to_numpy()
            _X[NAN_MASK] = np.nan
            _X = pl.from_numpy(_X, schema=_columns)
            _X = _X.cast(dict((zip(_columns, _dtypes))))
            del _columns, _dtypes
        else:
            _X[NAN_MASK] = np.nan

    if has_inf and cast_inf_to_nan:
        if hasattr(_X, 'toarray'):  # scipy sparse
            _X.data[INF_MASK] = np.nan
        elif hasattr(_X, 'clone'):  # polars
            _columns = _X.columns
            _dtypes = _X.dtypes
            _X = _X.to_numpy()
            _X[INF_MASK] = np.nan
            _X = pl.from_numpy(_X, schema=_columns)
            _X = _X.cast(dict((zip(_columns, _dtypes))))
            del _columns, _dtypes
        else:
            _X[INF_MASK] = np.nan


    return _X




