# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    TypeAlias,
)
import numpy.typing as npt

import numbers
from copy import deepcopy

import numpy as np
import pandas as pd
import scipy.sparse as ss
import polars as pl



PythonTypes: TypeAlias = list | tuple | set
NumpyTypes: TypeAlias = npt.NDArray[numbers.Number | str] | np.ma.MaskedArray
PandasTypes: TypeAlias = pd.Series | pd.DataFrame
PolarsTypes: TypeAlias = pl.Series | pl.DataFrame
SparseTypes: TypeAlias = (
    ss.csc_matrix | ss.csc_array | ss.csr_matrix | ss.csr_array
    | ss.coo_matrix | ss.coo_array | ss.dia_matrix | ss.dia_array
    | ss.lil_matrix | ss.lil_array | ss.dok_matrix | ss.dok_array
    | ss.bsr_matrix | ss.bsr_array
)

XContainer: TypeAlias = \
    PythonTypes | NumpyTypes | PandasTypes | PolarsTypes | SparseTypes



def copy_X(
    X: XContainer
) -> XContainer:
    """Make a deep copy of `X`.

    Can take Python lists, tuples, and sets, numpy ndarrays and masked
    arrays, pandas dataframes and series, polars dataframes and series,
    and scipy sparse matrices/arrays.

    Parameters
    ----------
    X : XContainer of shape (n_samples, n_features) or (n_samples,)
        The data to be copied.

    Returns
    -------
    X : XContainer
        A deep copy of `X`.

    Notes
    -----
    **Type Aliases**

    PythonTypes:
        list | tuple | set

    NumpyTypes:
        numpy.ndarray | numpy.ma.MaskedArray

    PandasTypes:
        pandas.Series | pandas.DataFrame

    PolarsTypes:
        polars.Series | polars.DataFrame

    SparseTypes:
        ss.csc_matrix | ss.csc_array | ss.csr_matrix | ss.csr_array
        | ss.coo_matrix | ss.coo_array | ss.dia_matrix | ss.dia_array
        | ss.lil_matrix | ss.lil_array | ss.dok_matrix | ss.dok_array
        | ss.bsr_matrix | ss.bsr_array

    XContainer:
        PythonTypes | NumpyTypes | PandasTypes | PolarsTypes | SparseTypes

    Examples
    --------
    >>> from pybear.base import copy_X
    >>> import pandas as pd
    >>> X = pd.DataFrame([[1, 2], [3, 4], [5, 6]])
    >>> X
       0  1
    0  1  2
    1  3  4
    2  5  6
    >>> new_X = copy_X(X)
    >>> new_X
       0  1
    0  1  2
    1  3  4
    2  5  6

    """


    # dont use type aliases as long as supporting py39
    if not isinstance(
        X,
        (list, tuple, set, np.ndarray, np.ma.MaskedArray, pd.Series,
         pd.DataFrame, pl.Series, pl.DataFrame,
         ss.csc_matrix, ss.csc_array, ss.csr_matrix, ss.csr_array,
         ss.coo_matrix, ss.coo_array, ss.dia_matrix, ss.dia_array,
         ss.lil_matrix, ss.lil_array, ss.dok_matrix, ss.dok_array,
         ss.bsr_matrix, ss.bsr_array)
    ):
        raise TypeError(f"copy_X(): unsupported container {type(X)}")

    if isinstance(X, np.recarray):
        raise TypeError(f"copy_X(): unsupported container {type(X)}")

    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    if hasattr(X, 'clone'):
        _X = X.clone()
    elif isinstance(X, (list, tuple, set)) or not hasattr(X, 'copy'):
        _X = deepcopy(X)
    else:  # has copy() method
        _X = X.copy()


    return _X





