# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    TypeAlias,
)
from .__type_aliases import (
    NumpyTypes,
    PandasTypes,
    PolarsTypes,
    ScipySparseTypes
)

XContainer: TypeAlias = \
    NumpyTypes | PandasTypes | PolarsTypes | ScipySparseTypes



def num_samples(X: XContainer) -> int:
    """Return the number of samples in an array-like `X`.

    `X` must have a 'shape' attribute.

    numpy, pandas, & polars:
        `X` must be 1 or 2 dimensional.
    scipy:
        `X` must be 2 dimensional.

    If `X` is a 1D vector (i.e., `len(X.shape)==1`), return `len(X)`.

    Parameters
    ----------
    X : XContainer of shape (n_samples, n_features) or (n_samples,)
        Object to find the number of samples in, that has a 'shape'
        attribute.

    Returns
    -------
    rows : int
        Number of samples.

    Notes
    -----

    **Type Aliases**

    NumpyTypes:
        numpy.ndarray

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
        NumpyTypes | PandasTypes | PolarsTypes | ScipySparseTypes

    Examples
    --------
    >>> from pybear.base import num_samples
    >>> import numpy as np
    >>> X = np.random.randint(0, 10, (5, 4))
    >>> num_samples(X)
    5

    """


    try:
        X.shape
    except:
        raise ValueError(
            f"\nThe passed object does not have a 'shape' attribute. "
            f"\nMost pybear estimators and transformers require data-bearing "
            f"objects to have a 'shape' attribute, like numpy arrays, pandas "
            f"dataframes, polars dataframes, and scipy sparse matrices / arrays."
        )


    if hasattr(X, 'toarray') and len(X.shape) != 2:  # is scipy sparse
        # there is inconsistent behavior with scipy array/matrix and 1D.
        # in some cases scipy.csr_array is allowing 1D to be passed and
        # in other cases it is not. scipy.csr_matrix takes a 1D and reports
        # 2D shape. avoid the whole issue, force all scipy to be 2D.
        raise ValueError(
            f"pybear requires all scipy sparse objects be 2 dimensional"
        )


    if len(X.shape) == 1:
        return len(X)
    elif len(X.shape) == 2:
        return int(X.shape[0])
    else:
        raise ValueError(
            f"The passed object has {len(X.shape)} dimensions. pybear "
            f"requires that all data-bearing objects be 1 or 2 dimensional."
        )





