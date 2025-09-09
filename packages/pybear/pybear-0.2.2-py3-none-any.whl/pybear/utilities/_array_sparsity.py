# Authors:
#
#       Bill Sousa
#
# License: BSD 3 clause



from typing import (
    TypeAlias,
)
from .__type_aliases import (
    NumpyTypes,
    PandasTypes,
    PolarsTypes
)

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss



PythonTypes: TypeAlias = list | tuple | list[list] | tuple[tuple]

ScipySparseTypes: TypeAlias = (
    ss.csc_matrix | ss.csc_array | ss.csr_matrix | ss.csr_array
    | ss.coo_matrix | ss.coo_array | ss.dia_matrix | ss.dia_array
    | ss.lil_matrix | ss.lil_array | ss.dok_matrix | ss.dok_array
)

Container: TypeAlias = \
    PythonTypes | NumpyTypes | PandasTypes | PolarsTypes | ScipySparseTypes




def array_sparsity(a: Container) -> float:
    """Calculate the sparsity (percentage of zeros) of an array-like.

    Returns a float between 0 and 100.

    Accepts Python lists and tuples but not sets, numpy ndarrays, pandas
    series and dataframes, polars series and dataframes, and all scipy
    sparse matrices / arrays except bsr.

    Parameters
    ----------
    a : array_like of shape (n_samples, n_features) or (n_samples,)
        Object for which to calculate sparsity. Cannot be empty.

    Returns
    -------
    sparsity : float
        Percentage of zeros in `a`.

    Examples
    --------
    >>> import numpy as np
    >>> from pybear.utilities import array_sparsity
    >>> a = np.array([[0,1,0,2,0],[1,0,0,0,3]])
    >>> array_sparsity(a)
    60.0

    Notes
    -----

    **Type Aliases**

    PythonTypes
        list | tuple | list[list] | tuple[tuple]]

    NumpyTypes
        numpy.ndarray

    PandasTypes
        pandas.Series | pandas.DataFrame

    PolarsTypes
        polars.Series | polars.DataFrame

    ScipySparseTypes
        ss.csc_matrix | ss.csc_array | ss.csr_matrix | ss.csr_array
        | ss.coo_matrix | ss.coo_array | ss.dia_matrix | ss.dia_array
        | ss.lil_matrix | ss.lil_array | ss.dok_matrix | ss.dok_array

    Container:
        PythonTypes | NumpyTypes | PandasTypes | PolarsTypes | ScipySparseTypes

    """

    # if is known container skip validation ** * ** * ** * ** * ** * **
    _skip_validation = 0
    _skip_validation += hasattr(a, 'ravel')  # np
    _skip_validation += hasattr(a, 'to_numpy')   # pd, pl
    _skip_validation += hasattr(a, 'toarray')    # ss
    # END if is known container skip validation ** * ** * ** * ** * ** *


    err_msg = (f"'a' must be a non-empty array-like that can be "
               f"converted to numpy.ndarray.")

    if hasattr(a, 'shape') and np.prod(a.shape) == 0:
        raise ValueError(err_msg)

    if not _skip_validation:

        try:
            list(iter(a))
            if isinstance(a, (str, dict)):
                raise Exception
        except Exception as e:
            raise TypeError(err_msg)


    if isinstance(a, np.ndarray):
        _non_zero = (a == 0).astype(np.int8).sum()
        _size = a.size
    elif isinstance(a, (pd.Series, pd.DataFrame)):
        _non_zero = (a == 0).astype(np.int8).values.sum()
        _size = a.size
    elif isinstance(a, pl.Series):
        _non_zero = (a == 0).cast(pl.Int8).sum()
        _size = np.prod(a.shape)
    elif isinstance(a, pl.DataFrame):
        _non_zero = (a == 0).cast(pl.Int8).sum().sum_horizontal()[0]
        _size = np.prod(a.shape)
    elif hasattr(a, 'toarray'):
        _size = np.prod(a.tocsc().shape)
        _non_zero = _size - a.tocsc().size
    else:
        try:
            a = np.array(list(map(list, a)))
        except:
            try:
                a = np.array(list(a))
            except:
                raise TypeError(f"failed to convert 'a' to a numpy array")

        if a.size == 0:
            raise ValueError(err_msg)

        _non_zero = (a == 0).astype(np.int8).sum()
        _size = a.size


    return float(_non_zero / _size * 100)







