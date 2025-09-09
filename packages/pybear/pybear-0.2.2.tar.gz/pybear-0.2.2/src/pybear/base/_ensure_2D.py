# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    TypeAlias,
)
from .__type_aliases import (
    PandasTypes,
    PolarsTypes
)

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

from ._copy_X import copy_X as _copy_X



NumpyTypes: TypeAlias = np.ndarray | np.ma.MaskedArray

ScipySparseTypes: TypeAlias = (
    ss.csc_matrix | ss.csc_array | ss.csr_matrix | ss.csr_array
    | ss.coo_matrix | ss.coo_array | ss.dia_matrix | ss.dia_array
    | ss.lil_matrix | ss.lil_array | ss.bsr_matrix | ss.bsr_array
)

XContainer: TypeAlias = \
    NumpyTypes | PandasTypes | PolarsTypes | ScipySparseTypes



def ensure_2D(
    X,
    copy_X:bool=True
):
    """Ensure that `X` has 2-dimensional shape, i.e., len(X.shape) == 2.

    If `X` is a 1D vector, assume the vector is a single feature of
    samples, not a single sample of features. `X` must have a 'shape'
    attribute. The only time `copy_X` matters is if `copy_X` is True and
    `X` is 1-dimensional. This module does not accept Python builtin
    iterables like list, set, and tuple.

    Parameters
    ----------
    X : array_like of shape (n_samples, n_features) or (n_samples,)
        The data to be put into a 2-dimensional container.
    copy : bool
        Whether to copy `X` or operate directly on the passed `X`.

    Returns
    -------
    X : array_like of shape (n_samples, n_features)
        The data in a 2-dimensional container.

    Notes
    -----

    **Type Aliases**

    NumpyTypes:
        numpy.ndarray | numpy.ma.MaskedArray

    PandasTypes:
        pandas.Series | pandas.DataFrame

    PolarsTypes:
        polars.Series | polars.DataFrame

    ScipySparseTypes:
        ss.csc_matrix | ss.csc_array | ss.csr_matrix | ss.csr_array
        | ss.coo_matrix | ss.coo_array | ss.dia_matrix | ss.dia_array
        | ss.lil_matrix | ss.lil_array | ss.bsr_matrix | ss.bsr_array

    XContainer:
        NumpyTypes | PandasTypes | PolarsTypes | ScipySparseTypes

    Examples
    --------
    >>> from pybear.base import ensure_2D
    >>> import numpy as np
    >>> X = np.array([1, 2, 3, 4, 5], dtype=np.int8)
    >>> out = ensure_2D(X, copy_X=True)
    >>> print(out)
    [[1]
     [2]
     [3]
     [4]
     [5]]

    """

    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    try:
        # bypass dok check, it is a python dict and wont pass
        if isinstance(X, (ss.dok_array, ss.dok_matrix)):
            raise UnicodeError
        iter(X)
        if isinstance(X, (str, dict, set, tuple, list)):
            raise Exception
    except UnicodeError:
        pass
    except:
        raise ValueError(
            f"ensure_2D: 'X' must be an iterable data-bearing container. "
            f"python builtin iterables are not allowed. Got {type(X)}."
        )


    if not hasattr(X, 'shape'):
        raise ValueError(f"ensure_2D: 'X' must have a 'shape' attribute.")

    if not isinstance(copy_X, bool):
        raise TypeError(f"'copy_X' must be boolean.")

    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    _dim = len(X.shape)

    if _dim == 0:
        raise ValueError(
            f"ensure_2D: 'X' is zero dimensional. Cannot convert 0D to 2D."
        )
    elif _dim == 1:

        if not hasattr(X, 'copy') and not hasattr(X, 'clone'):
            raise ValueError(f"'X' must have a 'copy' or 'clone', method.")

        if copy_X:
            _X = _copy_X(X)
        else:
            _X = X

        if isinstance(_X, (np.ndarray, np.ma.MaskedArray)):
            return _X.reshape((-1, 1))
        elif isinstance(_X, pd.Series):
            return _X.to_frame()
        elif isinstance(_X, pl.Series):
            return pl.DataFrame(_X)
        # should not have scipy sparse here
        else:
            raise ValueError(f"ensure_2D: unable to cast X to 2D")
    elif _dim == 2:
        return X
    elif _dim > 2:
        raise ValueError(
            f"ensure_2D: 'X' must be 2D or less, got {_dim}. Cannot "
            f"convert 3D+ to 2D."
        )




