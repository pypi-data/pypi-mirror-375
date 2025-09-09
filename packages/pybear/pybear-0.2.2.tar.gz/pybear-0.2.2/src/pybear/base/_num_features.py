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



def num_features(X: XContainer) -> int:
    """Return the number of features in an array-like `X`.

    `X` must have a 'shape' attribute.

    numpy, pandas, & polars:
        `X` must be 1 or 2 dimensional.

    scipy:
        `X` must be 2 dimensional.

    If `X` is a 1D vector (i.e., `len(X.shape)==1`), return 1.

    Parameters
    ----------
    X : XContainer of shape (n_samples, n_features) or (n_samples,)
        Object to find the number of features in, that has a 'shape'
        attribute.

    Returns
    -------
    features : int
        Number of features.

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
        return 1
    elif len(X.shape) == 2:
        return int(X.shape[1])
    else:
        raise ValueError(
            f"The passed object has {len(X.shape)} dimensions. pybear "
            f"requires that all data-bearing objects be 1 or 2 dimensional."
        )



    # keep this for reference
    # from sklearn[1.5].utils.validation._num_features
    # message = f"Unable to find the number of features from X of type {type(X)}"
    # # Do not consider an array-like of strings or dicts to be a 2D array
    # if isinstance(X[0], (str, bytes, dict)):
    #     message += f" where the samples are of type {type(X[0]).__qualname__}"
    #     raise TypeError(message)





