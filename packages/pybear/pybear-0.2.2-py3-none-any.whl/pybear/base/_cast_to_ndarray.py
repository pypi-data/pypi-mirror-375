# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    TypeAlias
)
import numpy.typing as npt
from .__type_aliases import (
    PythonTypes,
    PandasTypes,
    PolarsTypes,
    ScipySparseTypes
)

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

from ._copy_X import copy_X as _copy_X
from ..utilities._nan_masking import nan_mask


NumpyTypes: TypeAlias = npt.NDArray | np.ma.MaskedArray

XContainer: TypeAlias = \
    PythonTypes | NumpyTypes | PandasTypes | PolarsTypes | ScipySparseTypes



def cast_to_ndarray(
    X:XContainer,
    copy_X:bool = True
) -> npt.NDArray:
    """Convert the container of `X` to numpy.ndarray.

    Can take Python lists, tuples, and sets, numpy ndarrays and masked
    arrays, pandas dataframes and series, polars dataframes and series,
    and scipy sparse matrices and arrays. Any nan-like values are
    standardized to numpy.nan.

    Parameters
    ----------
    X : XContainer of shape (n_samples, n_features) or (n_samples,)
        The array-like data to be converted to ndarray.
    copy_X : bool, default=True
        Whether to copy `X` before casting to ndarray or perform the
        operations directly on the passed `X`.

    Returns
    -------
    X : numpy.ndarray
        The original data converted to numpy.ndarray.

    Notes
    -----

    **Type Aliases**

    PythonTypes:
        list | tuple | set | list[list] | tuple[tuple]

    NumpyTypes:
        numpy.ndarray | numpy.ma.MaskedArray

    PandasTypes:
        pandas.Series | pandas.DataFrame

    PolarsTypes:
        polars.Series | polars.DataFrame

    ScipySparseTypes:
        ss.csc_matrix | ss.csc_array | ss.csr_matrix | ss.csr_array
        | ss.coo_matrix | ss.coo_array | ss.dia_matrix | ss.dia_array
        | ss.lil_matrix | ss.lil_array | ss.dok_matrix | ss.dok_array
        | ss.bsr_matrix | ss.bsr_array

    XContainer:
        PythonTypes | NumpyTypes | PandasTypes | PolarsTypes | ScipySparseTypes

    """


    if not isinstance(copy_X, bool):
        raise TypeError(f"'copy_X' must be boolean.")


    # block unsupported containers -- -- -- -- -- -- -- -- -- -- -- --
    # dont use the type aliases while still supporting py39
    if not isinstance(X,
        (list, tuple, set, np.ndarray, np.ma.MaskedArray, pd.Series,
         pd.DataFrame, pl.Series, pl.DataFrame,
         ss.csc_matrix, ss.csc_array, ss.csr_matrix, ss.csr_array,
         ss.coo_matrix, ss.coo_array, ss.dia_matrix, ss.dia_array,
         ss.lil_matrix, ss.lil_array, ss.dok_matrix, ss.dok_array,
         ss.bsr_matrix, ss.bsr_array)
    ):
        raise TypeError(
            f"cast_to_ndarray(): unsupported container {type(X)}. "
        )

    if isinstance(X, np.recarray):
        raise TypeError(f"copy_X(): unsupported container {type(X)}")
    # END block unsupported containers -- -- -- -- -- -- -- -- -- -- --

    if copy_X:
        _X = _copy_X(X)
    else:
        _X = X

    # convert to ndarray -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    if isinstance(_X, (list, tuple, set)):
        try:
            if isinstance(_X, set):
                raise Exception
            if any(map(isinstance, _X, (str for _ in _X))):
                # dont map iterable to strings!
                # must be 1D
                raise Exception
            map(list, _X)
            # must be 2D
            # if is ragged numpy will still make ndarray. dont let it.
            if len(set(map(len, _X))) > 1:
                raise UnicodeError
            _X = np.array(list(map, list(_X)))
        except UnicodeError:
            raise ValueError(
                f"X is ragged. pybear does not allow this to be cast "
                f"to ndarray."
            )
        except Exception as e:
            _X = np.array(list(_X))
    elif hasattr(_X, 'toarray'):
        # scipy sparse
        _X = _X.toarray()
    elif hasattr(_X, 'clone'):
        # polars
        _X = _X.to_numpy()
    elif isinstance(_X, np.ma.MaskedArray):
        _X = np.ma.getdata(_X)

    # do pd separate, compute may output a dataframe
    if isinstance(_X, (pd.Series, pd.DataFrame)):
        # pandas
        _X = _X.to_numpy()


    # standardize all nans to np
    try:
        # will except on int dtype
        _og_dtype = _X.dtype
        _X = _X.astype(np.float64)
        _X[nan_mask(_X)] = np.nan
        _X = _X.astype(_og_dtype)
        del _og_dtype
    except Exception as e:
        # can only kick out to here if non-numeric
        try:
            _X[nan_mask(_X)] = np.nan
        except:
            pass


    # if is not an integer dtype, try to cast to float
    # (it might be all numbers but as object dtype)
    try:
        if 'int' in str(_X.dtype).lower():
            raise Exception
        _X = _X.astype(np.float64)
    except Exception as e:
        pass

    # END convert to ndarray -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # *** _X MUST BE np ***

    if not isinstance(_X, np.ndarray):
        raise TypeError(
            f"X is an invalid data-type {type(_X)} after trying to cast "
            f"to ndarray."
        )


    return _X





